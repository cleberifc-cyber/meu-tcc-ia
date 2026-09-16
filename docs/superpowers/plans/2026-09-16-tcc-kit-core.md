# TCC Kit Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a first-time user clone/install the toolkit, answer a short Portuguese questionnaire, and receive a grounded, ready-to-edit TCC workspace.

**Architecture:** A Python package exposes `tcc-kit` through `argparse`; the initializer validates user-provided project data, copies packaged starter assets, and writes a machine-readable profile. Prompt-only stage guidance works without an AI account or network service.

**Tech Stack:** Python >=3.11, setuptools, `python-docx` as the DOCX dependency in the following formatter plan, standard-library `argparse`, `json`, `tomllib`, `pathlib`, and `unittest`/`pytest`.

**Spec:** `docs/superpowers/specs/2026-09-16-tcc-abnt-studio-design.md`

## Global Constraints

- PT-BR is the canonical initial onboarding language.
- The default first-run flow makes no AI-provider call and sends no manuscript content over the network.
- Never invent the research problem, method, findings, or references to fill missing answers.
- The CLI must preserve existing files and explain conflicts before writing.
- Python minimum version is 3.11.

---

### Task 1: Make the repository installable and add a testable CLI entry point

**Files:**
- Create: `pyproject.toml`
- Create: `src/tcc_kit/__init__.py`
- Create: `src/tcc_kit/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:** `tcc_kit.cli.main(argv: list[str] | None = None) -> int` parses `init`, `prompt`, `source`, `check`, and `format` command groups. Only `init` and `prompt` are implemented in this plan; other groups must return a Portuguese “not available in this release” error rather than an exception. The project extra `[test]` installs pytest for contributors.

- [ ] **Step 1: Write the CLI help test**

```python
import pytest
from tcc_kit.cli import main

def test_help_lists_supported_commands(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "init" in output
    assert "prompt" in output
```

- [ ] **Step 2: Run `python -m pytest tests/test_cli.py -q`; confirm it fails because the package/entry point is absent.**
- [ ] **Step 3: Add `pyproject.toml` with `requires-python = ">=3.11"`, dependency `python-docx>=1.1,<2`, test extra `pytest>=8,<10` plus `build>=1,<2`, project version `0.1.0a1`, and console script `tcc-kit = "tcc_kit.cli:main"`; add a parser whose help contains all five command groups.**
- [ ] **Step 4: Run `python -m pytest tests/test_cli.py -q`; confirm PASS, then run `python -m pip install -e .` and `tcc-kit --help`.**
- [ ] **Step 5: Commit with `git add pyproject.toml src/tcc_kit tests/test_cli.py; git commit -m "feat: add installable tcc-kit CLI"`.**

### Task 2: Collect, validate, and persist the project questionnaire

**Files:**
- Create: `src/tcc_kit/project.py`
- Create: `tests/test_project.py`
- Modify: `src/tcc_kit/cli.py`

**Interfaces:** `collect_answers(read: Callable[[str], str], write: Callable[[str], None]) -> dict[str, str]`; `validate_answers(answers: dict[str, str]) -> list[str]`; `render_project_toml(answers: dict[str, str]) -> str`; `create_project(destination: Path, answers: dict[str, str]) -> list[Path]`.

- [ ] **Step 1: Test required keys, valid “ainda não sei” values, invalid empty topic, and conflict-safe creation.**

```python
import pytest

def test_create_project_writes_answers_without_overwriting(tmp_path):
    answers = {"topic": "Acessibilidade digital", "course": "Sistemas", "institution": "IFC",
               "work_type": "monografia", "problem": "Ainda não definido", "objectives": "Ainda não definido",
               "method": "Ainda não definido"}
    created = create_project(tmp_path / "meu-tcc", answers)
    assert (tmp_path / "meu-tcc" / "tcc.toml").exists()
    assert created
    with pytest.raises(FileExistsError):
        create_project(tmp_path / "meu-tcc", answers)
```

- [ ] **Step 2: Run `python -m pytest tests/test_project.py -q`; confirm the missing functions cause failure.**
- [ ] **Step 3: Implement the injected-I/O questionnaire and write UTF-8 TOML using JSON string escaping for TOML basic strings; create only the profile file in this task, then copy packaged project assets in Task 3.**

```python
def create_project(destination: Path, answers: dict[str, str]) -> list[Path]:
    if destination.exists():
        raise FileExistsError(destination)
    errors = validate_answers(answers)
    if errors:
        raise ValueError("; ".join(errors))
    destination.mkdir(parents=True, exist_ok=False)
    profile = destination / "tcc.toml"
    profile.write_text(render_project_toml(answers), encoding="utf-8")
    return [profile]
```
- [ ] **Step 4: Run `python -m pytest tests/test_project.py -q`; confirm PASS and inspect the generated TOML by loading it with `tomllib`.**
- [ ] **Step 5: Commit with `git add src/tcc_kit/project.py src/tcc_kit/cli.py tests/test_project.py; git commit -m "feat: add guided TCC project initializer"`.**

### Task 3: Add project assets and stage-by-stage prompt generation

**Files:**
- Create: `src/tcc_kit/assets/project/tcc.md`
- Create: `src/tcc_kit/assets/project/references.json`
- Create: `src/tcc_kit/assets/project/README.md`
- Create: `src/tcc_kit/assets/prompts/01-introducao.txt`
- Create: `src/tcc_kit/assets/prompts/02-referencial.txt`
- Create: `src/tcc_kit/assets/prompts/03-metodologia.txt`
- Modify: `pyproject.toml`
- Modify: `src/tcc_kit/project.py`
- Modify: `src/tcc_kit/cli.py`
- Test: `tests/test_prompts.py`

**Interfaces:** `build_prompt(project_dir: Path, section: str) -> str`; CLI `tcc-kit prompt --project PATH --section {introducao,referencial,metodologia}` prints the prompt without making network calls.

- [ ] **Step 1: Test that the three supported sections create prompts containing the project topic and an instruction not to invent sources; reject unknown sections.**

```python
def test_build_prompt_is_project_specific(tmp_path):
    answers = {"topic": "Acessibilidade digital", "course": "Sistemas", "institution": "IFC",
               "work_type": "monografia", "problem": "Ainda não definido", "objectives": "Ainda não definido",
               "method": "Ainda não definido"}
    create_project(tmp_path / "p", answers)
    prompt = build_prompt(tmp_path / "p", "introducao")
    assert "Acessibilidade digital" in prompt
    assert "não invente" in prompt.casefold()
```
- [ ] **Step 2: Run `python -m pytest tests/test_prompts.py -q`; confirm the tests fail before prompt packaging exists.**
- [ ] **Step 3: Add UTF-8 prompt assets with clear missing-data markers, load them with `importlib.resources`, and package them via setuptools package-data configuration.**
- [ ] **Step 4: Run `python -m pytest tests/test_prompts.py -q` and `python -m pip install -e .`; from a generated project run `tcc-kit prompt --project <path> --section introducao`; confirm the output is PT-BR and includes the entered topic.**
- [ ] **Step 5: Commit the assets and implementation as `feat: add reusable staged TCC prompts`.**

### Task 4: Verify the end-to-end clone-to-project path

**Files:**
- Create: `tests/test_first_run.py`
- Modify: `README.md`
- Modify: `.gitignore`

**Interfaces:** The documented first-run sequence is `git clone`, `python -m pip install -e .`, and `tcc-kit init ./meu-tcc`; running it must produce the assets from Task 3.

- [ ] **Step 1: Write a subprocess test that runs `python -m tcc_kit.cli init <tempdir> --answers-json <fixture>` and checks README, TOML, prompts, manuscript, and empty reference store.**
- [ ] **Step 2: Run `python -m pytest tests/test_first_run.py -q`; confirm failure before the non-interactive option is implemented.**
- [ ] **Step 3: Add `--answers-json` for deterministic onboarding/automation, refuse unknown keys, and document a beginner path with explicit Windows and macOS/Linux commands.**
- [ ] **Step 4: Run `python -m pytest -q`; follow the README commands in a clean temporary directory; confirm no API key or AI service is needed.**
- [ ] **Step 5: Commit with `feat: complete first-run project workflow`.**
