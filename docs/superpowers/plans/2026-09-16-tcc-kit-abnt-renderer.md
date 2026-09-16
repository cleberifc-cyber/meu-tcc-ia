# TCC Kit ABNT Document Renderer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Export the complete supported manuscript as an editable DOCX, optionally convert it to PDF, and report the exact rule profile and any unverified coverage.

**Architecture:** Parse the documented Markdown subset plus project metadata and normalized reference records into a small document model. Apply an explicit, versioned profile through `python-docx`; keep PDF conversion in an optional adapter that detects a local LibreOffice installation.

**Tech Stack:** Python >=3.11, `python-docx>=1.1,<2`, standard-library TOML/JSON/XML/path APIs, LibreOffice optional.

**Spec:** `docs/superpowers/specs/2026-09-16-tcc-abnt-studio-design.md`

## Global Constraints

- DOCX is the primary editable output; PDF is optional when a local converter is installed.
- Rule profiles name their standard editions, official source, verification date, state, and supported structures.
- No profile may claim “current” or “fully ABNT compliant” until its edition and fixtures have been checked against authorized/official source material.
- An unverified profile remains visibly `preview` and its outputs include that warning.
- Source Markdown and metadata are never modified by `format`.
- Tests use small original examples and inspect generated DOCX structure without calling live services.

---

### Task 1: Add profile manifest loading and explicit verification state

**Files:**
- Create: `src/tcc_kit/formatting/__init__.py`
- Create: `src/tcc_kit/formatting/profile.py`
- Create: `src/tcc_kit/assets/profiles/abnt-br-preview.toml`
- Modify: `pyproject.toml`
- Test: `tests/formatting/test_profile.py`
- Test: `tests/formatting/conftest.py`

**Interfaces:** `RuleProfile.load(path: Path) -> RuleProfile`; fields are `id`, `display_name`, `status`, `standards: list[dict[str,str]]`, `official_catalog_url`, `verified_at: str | None`, `document: dict[str,object]`, `references: dict[str,object]`, and `supported_blocks: list[str]`. Accept status values `preview`, `verified`, and `stale`; reject `verified` when `verified_at` or a standard edition is absent.

- [ ] **Step 1: Test a valid preview manifest, a valid dated/editioned profile, an invalid status, and rejection of an undated verified profile.**

```python
from pathlib import Path
from tcc_kit.formatting.profile import RuleProfile

def test_unverified_profile_is_not_reported_as_current(profile_path):
    profile = RuleProfile.load(profile_path)
    assert profile.status == "preview"
    assert "não verificado" in profile.status_message().casefold()
```
- [ ] **Step 2: Run `python -m pytest tests/formatting/test_profile.py -q`; confirm the loader does not yet exist.**
- [ ] **Step 3: Implement strict TOML decoding and schema validation; package the profile asset with the wheel. The bundled starting profile must remain `preview` until the exact supported editions and outputs have been independently checked.**

```python
@dataclass(frozen=True)
class RuleProfile:
    id: str
    display_name: str
    status: str
    standards: list[dict[str, str]]
    official_catalog_url: str
    verified_at: str | None
    document: dict[str, object]
    references: dict[str, object]
    supported_blocks: list[str]
```

`conftest.py` creates `profile_path` from the packaged preview manifest and exposes `write_profile(tmp_path, **overrides)` for invalid-state tests.
- [ ] **Step 4: Run `python -m pytest tests/formatting/test_profile.py -q`; confirm PASS and assert that preview status produces a warning string in `profile.status_message()`.**
- [ ] **Step 5: Commit with `git add src/tcc_kit/formatting src/tcc_kit/assets/profiles pyproject.toml tests/formatting/test_profile.py; git commit -m "feat: add versioned ABNT profile registry"`.**

### Task 2: Parse the supported manuscript blocks without changing source files

**Files:**
- Create: `src/tcc_kit/formatting/markdown.py`
- Create: `src/tcc_kit/formatting/document.py`
- Test: `tests/formatting/test_markdown.py`

**Interfaces:** `parse_manuscript(text: str, project_dir: Path) -> list[Block]`; `Block(kind: str, text: str, line_number: int, level: int | None = None, items: list[str] | None = None, rows: list[list[str]] | None = None, image_path: Path | None = None, caption: str | None = None)` supports frontmatter, headings `#` through `###`, paragraphs, ordered/unordered lists, simple pipe tables, local `![caption](relative-path)` images, and citation markers `[@key]`. Unsupported raw HTML/remote images return a diagnostic. Local image paths that resolve outside the project directory are rejected.

- [ ] **Step 1: Test title metadata, three heading levels, paragraph joins, numbered/bulleted lists, table rows, a local image and caption, path traversal rejection, remote-image rejection, citation markers, and unsupported raw HTML diagnostics.**

```python
def test_parser_preserves_supported_block_order(project_dir):
    blocks = parse_manuscript("# Título\n\nTexto\n\n- Item\n", project_dir)
    assert [block.kind for block in blocks] == ["heading", "paragraph", "list"]
```
- [ ] **Step 2: Run `python -m pytest tests/formatting/test_markdown.py -q`; confirm the parser is absent.**
- [ ] **Step 3: Implement a bounded line parser for only the documented syntax; preserve order, raw text, and one-based source line numbers; parse pipe-table cells without interpreting Markdown inside cells; resolve image paths under project root only.**

```python
@dataclass(frozen=True)
class Block:
    kind: str
    text: str
    line_number: int
    level: int | None = None
    items: list[str] | None = None
    rows: list[list[str]] | None = None
    image_path: Path | None = None
    caption: str | None = None
```

`conftest.py` also creates `project_dir` and `sample_project` under pytest's `tmp_path`; the latter writes one original Markdown fixture and one source-store JSON file.
- [ ] **Step 4: Run the parser tests and add a byte-for-byte assertion that parsing does not mutate the input file.**
- [ ] **Step 5: Commit with `git add src/tcc_kit/formatting/markdown.py src/tcc_kit/formatting/document.py tests/formatting/test_markdown.py; git commit -m "feat: parse supported TCC manuscript blocks"`.**

### Task 3: Render versioned DOCX and a build report

**Files:**
- Create: `src/tcc_kit/formatting/docx.py`
- Create: `src/tcc_kit/formatting/report.py`
- Modify: `src/tcc_kit/cli.py`
- Test: `tests/formatting/test_docx.py`

**Interfaces:** `load_project_metadata(project_dir: Path) -> dict[str, object]`; `render_blocks(blocks: list[Block], metadata: dict[str, object], references: list[ReferenceRecord], output_path: Path, profile: RuleProfile) -> BuildReport`; `render_docx(project_dir: Path, output_path: Path, profile: RuleProfile) -> BuildReport`; `BuildReport` contains `output`, `profile_id`, `profile_status`, `standard_editions`, `tool_versions`, `warnings`, and `source_hashes`. `tcc-kit format PATH --output FILE.docx [--profile FILE.toml]` never overwrites manuscript inputs and refuses to overwrite an existing output without `--force`.

- [ ] **Step 1: Test that rendering an original sample creates a valid DOCX with title, section headings, paragraphs, list numbering, source-derived references, and an explicit profile warning.**

```python
from docx import Document

def test_render_docx_reports_profile_and_warnings(sample_project, tmp_path, preview_profile):
    report = render_docx(sample_project, tmp_path / "tcc.docx", preview_profile)
    document = Document(report.output)
    assert any(p.text == "Introdução" for p in document.paragraphs)
    assert report.profile_status == "preview"
    assert report.warnings
```
- [ ] **Step 2: Test that an existing output and a missing manuscript fail without modifying any file; test report JSON contains profile and source hashes.**
- [ ] **Step 3: Run `python -m pytest tests/formatting/test_docx.py -q`; confirm the renderer and report are absent.**
- [ ] **Step 4: Implement page dimensions, margins, font/heading styles, title page, running footer/page-number field, pipe tables, local images/captions, citations, bibliography, and supported reference renderings from profile fields only; add supported mappings for the reference types validated in `tests/sources/`. Unsupported types must be listed in `warnings`.**

```python
def render_docx(project_dir: Path, output_path: Path, profile: RuleProfile) -> BuildReport:
    source = (project_dir / "tcc.md").read_text(encoding="utf-8")
    blocks = parse_manuscript(source, project_dir)
    return render_blocks(blocks, load_project_metadata(project_dir), load_store(project_dir), output_path, profile)
```
- [ ] **Step 5: Run formatter tests, reopen the output with `python-docx`, inspect document sections/styles, and commit as `feat: render profiled TCC DOCX with build report`.**

### Task 4: Add optional PDF conversion and formatting integration tests

**Files:**
- Create: `src/tcc_kit/formatting/pdf.py`
- Modify: `src/tcc_kit/cli.py`
- Test: `tests/formatting/test_pdf.py`
- Test: `tests/formatting/test_full_export.py`

**Interfaces:** `convert_pdf(docx_path: Path, pdf_path: Path, executable: str | None = None) -> Path`; find `soffice`/`libreoffice` on PATH, call it without a shell, enforce timeout, and return a clear `PdfToolMissingError` if absent. CLI accepts `--format docx|pdf|both` and `--output PATH`; when PDF is requested, DOCX is created first and remains available if conversion fails.

- [ ] **Step 1: Test executable discovery, missing executable, nonzero converter exit, timeout, and successful mocked conversion; never launch a real converter in unit tests.**

```python
def test_missing_pdf_converter_leaves_docx_available(tmp_path, monkeypatch):
    docx_path = tmp_path / "tcc.docx"
    docx_path.write_bytes(b"docx fixture")
    monkeypatch.setattr("tcc_kit.formatting.pdf.find_converter", lambda: None)
    with pytest.raises(PdfToolMissingError):
        convert_pdf(docx_path, tmp_path / "tcc.pdf")
    assert docx_path.exists()
```
- [ ] **Step 2: Run `python -m pytest tests/formatting/test_pdf.py -q`; confirm the adapter is absent.**
- [ ] **Step 3: Implement the adapter using `subprocess.run([...], shell=False, timeout=120, check=False)` and capture only redacted command output.**
- [ ] **Step 4: Add an end-to-end fixture that creates a temporary project with an imported reference fixture, runs `check`, renders DOCX, and confirms the original Markdown/JSON hashes are unchanged. Run `python -m pytest -q`.**
- [ ] **Step 5: Commit with `git add src/tcc_kit/formatting src/tcc_kit/cli.py tests/formatting; git commit -m "feat: add optional PDF and end-to-end export"`.**

### Task 5: Establish the first verifiable profile and rule-change process

**Files:**
- Modify: `src/tcc_kit/assets/profiles/abnt-br-preview.toml`
- Create: `docs/abnt/profile-status.md`
- Create: `tests/formatting/fixtures/expected-profile-output.json`
- Modify: `docs/superpowers/specs/2026-09-16-tcc-abnt-studio-design.md`

**Interfaces:** A profile can change from `preview` to `verified` only when the manifest lists exact standard editions and a catalog URL, the changelog records reviewer/date, and the fixture suite covers every advertised block/reference type. Verification status is printed by `tcc-kit check` and stored in each build report.

- [ ] **Step 1: Record the exact standard editions and official catalog records available during this release review; do not copy norm text into the repository. If source access is incomplete, retain `preview`.**

```python
def test_verified_profile_requires_evidence_fields(tmp_path):
    profile_path = write_profile(tmp_path, status="verified", verified_at=None, standards=[])
    with pytest.raises(ProfileValidationError):
        RuleProfile.load(profile_path)
```
- [ ] **Step 2: Add original minimal fixture records/documents for each advertised content type and identify in `profile-status.md` which behavior each fixture tests.**
- [ ] **Step 3: Run the complete profile/formatter suite and verify the fixture names match profile support declarations.**
- [ ] **Step 4: Run `python -m pytest -q`; assert that `verified` state cannot be loaded unless the evidence fields and tests exist.**
- [ ] **Step 5: Commit profile data, status report, and tests as `docs: record supported ABNT profile evidence`.**
