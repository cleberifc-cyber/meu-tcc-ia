# TCC Kit Public Release Readiness Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the public repository easy to discover, clone, install, understand, contribute to, and evaluate without overstating its ABNT or CI status.

**Architecture:** Human-facing documentation and community policy stay in focused Markdown files; GitHub issue forms capture reproducible feedback; CI installs the same package and runs the same offline tests across supported operating systems.

**Tech Stack:** GitHub Markdown/issue forms/Actions, Python package/test commands already defined by the core plans.

**Spec:** `docs/superpowers/specs/2026-09-16-tcc-abnt-studio-design.md`

## Global Constraints

- The documented Windows and Linux/macOS clone paths must be exercised locally.
- Never show a green passing badge unless a real workflow run has passed.
- Explain the profile's exact supported and unverified scope in README and release notes.
- Do not ask users for stars in exchange for functionality or use fabricated testimonials.
- Do not put tokens or academic manuscript content in issue forms or logs.

---

### Task 1: Rewrite the PT-BR README around the first successful use

**Files:**
- Modify: `README.md`
- Create: `docs/quickstart.md`
- Create: `docs/privacy.md`
- Create: `docs/abnt/profile-status.md`

**Interfaces:** README documents `git clone`, `python -m pip install -e .`, `tcc-kit init ./meu-tcc`, `tcc-kit source add <DOI> --project ./meu-tcc`, `tcc-kit check ./meu-tcc`, and `tcc-kit format ./meu-tcc --format docx`.

- [ ] **Step 1: Add a documentation acceptance checklist test that searches for clone/install/initialize/reference/check/format commands, version-warning language, privacy default, and PDF prerequisite.**

```python
def test_readme_has_real_quick_start_commands():
    readme = Path("README.md").read_text(encoding="utf-8")
    for command in ("git clone", "pip install -e .", "tcc-kit init", "tcc-kit check", "tcc-kit format"):
        assert command in readme
```
- [ ] **Step 2: Run `python -m pytest tests/test_docs.py -q`; confirm the current README fails the product quick-start checks.**
- [ ] **Step 3: Write concise PT-BR problem/benefit summary, quick start, supported platform table, demo GIF/link only when the demo asset exists, profile status, limitations, architecture, contribution, privacy, and troubleshooting sections.**
- [ ] **Step 4: Run the docs test; manually follow every command in a clean temporary folder on Windows and the Linux/macOS shell commands in CI; fix any mismatch with actual CLI signatures.**
- [ ] **Step 5: Commit with `docs: create beginner-first Portuguese quick start`.**

### Task 2: Add English entrypoint and open-source contribution/security files

**Files:**
- Create: `README.en.md`
- Create: `CONTRIBUTING.md`
- Create: `CODE_OF_CONDUCT.md`
- Create: `SECURITY.md`
- Create: `CHANGELOG.md`
- Create: `ROADMAP.md`
- Create: `LICENSE`
- Create: `THIRD_PARTY.md`
- Modify: `README.md`

**Interfaces:** Language links switch between `/` and `/README.en.md`; all contribution rules route to `CONTRIBUTING.md`; security reports are requested privately through GitHub's security advisory mechanism, never through public issue forms. Apply MIT to the toolkit code and original project documentation only; third-party/normative materials remain excluded and retain their respective rights.

- [ ] **Step 1: Test that language links resolve, security instructions avoid exposing secrets, the changelog contains the current version, and THIRD_PARTY records Python/python-docx/DataCite/Crossref/Pandoc roles and links.**

```python
def test_security_doc_never_requests_public_secret_reports():
    security = Path("SECURITY.md").read_text(encoding="utf-8").casefold()
    assert "private" in security
    assert "never include api keys" in security
```
- [ ] **Step 2: Run `python -m pytest tests/test_docs.py -q`; confirm the new paths do not yet exist.**
- [ ] **Step 3: Add the English quick start, contribution/test instructions, contributor conduct, private security-report route, initial changelog/roadmap, SPDX MIT license text, and source/third-party inventory.**
- [ ] **Step 4: Validate Markdown links locally and run `python -m pytest tests/test_docs.py -q`; confirm all paths exist and no fabricated contributor/community claims appear.**
- [ ] **Step 5: Commit with `docs: add bilingual community and security guidance`.**

### Task 3: Add accurate public issue forms and CI

**Files:**
- Create: `.github/ISSUE_TEMPLATE/bug.yml`
- Create: `.github/ISSUE_TEMPLATE/rule-profile.yml`
- Create: `.github/ISSUE_TEMPLATE/provider-request.yml`
- Create: `.github/workflows/ci.yml`
- Modify: `pyproject.toml`
- Test: `tests/test_repo_assets.py`

**Interfaces:** Bug reports collect OS, Python/tool versions, exact command, redacted output, and expected/actual result; rule reports collect source/edition and a short minimal example without asking for copyrighted standards or private manuscripts. CI runs on Ubuntu and Windows, installs editable package plus test extras, runs `pytest`, and builds the wheel.

- [ ] **Step 1: Test YAML parses, issue forms do not request API keys or full TCC files, workflow contains Ubuntu/Windows, test, and build jobs, and package metadata declares the test extra.**

```python
def test_ci_matrix_covers_windows_and_linux():
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "windows-latest" in workflow and "ubuntu-latest" in workflow
    assert "python -m pytest -q" in workflow
```
- [ ] **Step 2: Run `python -m pytest tests/test_repo_assets.py -q`; confirm the files are absent.**
- [ ] **Step 3: Implement issue forms and CI with `actions/checkout@v4`, `actions/setup-python@v5`, and pinned Python matrix `3.11`, `3.12`, `3.13`; use `python -m pip install -e ".[test]"`, `python -m pytest -q`, and `python -m build`.**
- [ ] **Step 4: Run all local tests, `python -m build`, and available YAML validation; clearly record GitHub-hosted workflow as pending until the owner account can start Actions.**
- [ ] **Step 5: Commit with `ci: add cross-platform tests and repository issue forms`.**

### Task 4: Publish accurate discoverability metadata after tests

**Files:**
- Modify: GitHub repository description/topics (remote metadata only)
- Verify: GitHub README rendering and unauthenticated clone

**Interfaces:** Repository description states that this is a source-aware, guided TCC/ABNT toolkit in PT-BR; topics use established terms such as `abnt`, `tcc`, `academic-writing`, `citation`, `bibliography`, and `python`. No metadata says “guaranteed ABNT” or “AI writes a complete thesis automatically”.

- [ ] **Step 1: Verify all code/docs commits are on the release branch, all local tests/build pass, and README links resolve before changing remote metadata.**
- [ ] **Step 2: Set the GitHub repository description and topics through the GitHub repository API; verify their values with a read-only API request.**
- [ ] **Step 3: From a clean temporary directory, clone the public repository anonymously and run the documented installation and initializer path.**
- [ ] **Step 4: Record the exact commit, local test/build results, actual Actions status, profile verification state, supported output formats, and known limitations in the release notes.**
- [ ] **Step 5: Commit the release note; do not tag a stable version until the ABNT fixture gate and an actual public workflow run pass.**
