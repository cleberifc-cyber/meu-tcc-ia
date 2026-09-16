# TCC Kit Source-Aware References Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import DOI metadata from Crossref/DataCite without hallucinating, retain field-level provenance, and validate citations against the local project store.

**Architecture:** A normalized `ReferenceRecord` is independent of the upstream API. Read-only API clients return candidates with provider metadata; a store persists them locally, and the CLI reports missing/ambiguous fields for student confirmation.

**Tech Stack:** Python >=3.11, standard-library `urllib`, `json`, `dataclasses`, `unittest.mock`; existing `pytest` dev dependency.

**Spec:** `docs/superpowers/specs/2026-09-16-tcc-abnt-studio-design.md`

## Global Constraints

- Crossref and DataCite lookups are anonymous read-only GETs; no source key is required.
- Every imported record includes provider, identifier, landing page if returned, and retrieval timestamp.
- A registry result is a candidate, not a verified scholarly claim; users can correct fields without losing original provenance.
- Timeouts, rate limits, missing metadata, and offline use must be explicit and recoverable.
- DOI lookup must not retrieve or copy publisher full text.

---

### Task 1: Define the normalized source record and local store

**Files:**
- Create: `src/tcc_kit/sources/__init__.py`
- Create: `src/tcc_kit/sources/models.py`
- Create: `src/tcc_kit/sources/store.py`
- Test: `tests/sources/test_store.py`

**Interfaces:** `Provenance(provider: str, record_id: str, retrieved_at: str, record_url: str | None)`; `ReferenceRecord(key: str, item_type: str, fields: dict[str, object], provenance: dict[str, Provenance], user_overrides: dict[str, object])`; `DuplicateReferenceError(ValueError)`; `load_store(project_dir: Path) -> list[ReferenceRecord]`; `save_record(project_dir: Path, record: ReferenceRecord, replace: bool = False) -> None` writes `references.json` atomically and raises `DuplicateReferenceError` unless `replace=True`.

- [ ] **Step 1: Test JSON round trip, non-destructive user overrides, duplicate rejection, and atomic preservation when serialization fails.**

```python
def test_duplicate_key_is_rejected(tmp_path):
    record = ReferenceRecord(key="silva2024", item_type="book", fields={"title": "Exemplo"},
                             provenance={}, user_overrides={})
    save_record(tmp_path, record)
    with pytest.raises(DuplicateReferenceError):
        save_record(tmp_path, record)
    assert load_store(tmp_path) == [record]
```
- [ ] **Step 2: Run `python -m pytest tests/sources/test_store.py -q`; confirm import/function errors.**
- [ ] **Step 3: Implement dataclasses, strict JSON shape checking, UTF-8 serialization to a sibling temporary file, and `Path.replace()` after complete encoding.**
- [ ] **Step 4: Run `python -m pytest tests/sources/test_store.py -q`; confirm PASS and check the project's `.gitignore` continues to exclude secrets but not its source register.**
- [ ] **Step 5: Commit with `git add src/tcc_kit/sources tests/sources/test_store.py; git commit -m "feat: add provenance-aware reference store"`.**

### Task 2: Implement DOI normalization and read-only metadata adapters

**Files:**
- Create: `src/tcc_kit/sources/doi.py`
- Create: `src/tcc_kit/sources/crossref.py`
- Create: `src/tcc_kit/sources/datacite.py`
- Test: `tests/sources/test_doi.py`
- Test: `tests/sources/test_providers.py`
- Test: `tests/sources/fixtures/crossref-article.json`
- Test: `tests/sources/fixtures/datacite-dataset.json`

**Interfaces:** `normalize_doi(value: str) -> str` accepts bare DOI, `doi:` prefix, and `https://doi.org/` URL; `fetch_crossref(doi: str, opener: Callable[..., object] = urllib.request.urlopen) -> ReferenceRecord`; `fetch_datacite(doi: str, opener: Callable[..., object] = urllib.request.urlopen) -> ReferenceRecord`; `lookup_doi(doi: str, opener=...) -> ReferenceRecord` queries Crossref agency first and then DataCite only if Crossref says the DOI is registered elsewhere.

- [ ] **Step 1: Add fixtures for a Crossref journal article, a DataCite dataset, a DOI URL, a malformed DOI, a 404, a timeout, and a metadata record with missing author/title.**

```python
def test_normalize_doi_accepts_resolver_url():
    assert normalize_doi("https://doi.org/10.1234/Ab.C") == "10.1234/ab.c"

def test_missing_crossref_author_stays_missing(fake_crossref_opener):
    record = fetch_crossref("10.1234/example", opener=fake_crossref_opener)
    assert "author" not in record.fields
```

`fake_crossref_opener` is defined in the test module and returns `io.BytesIO(json.dumps(fixture).encode("utf-8"))`; it never opens a socket. The fixture JSON files are minimal synthetic records and contain no copied abstracts.
- [ ] **Step 2: Test field mapping and exact GET URLs using a fake opener; assert no POST or Authorization header is sent. Run the provider tests and confirm failure.**
- [ ] **Step 3: Implement DOI normalization, fixed API roots, 10-second timeout, explicit User-Agent, provider-specific JSON parsing, and errors `DoiFormatError`, `DoiNotFoundError`, `SourceUnavailableError`; retry one 429/5xx response only when `Retry-After` fits within a 5-second ceiling.**
- [ ] **Step 4: Run `python -m pytest tests/sources/test_doi.py tests/sources/test_providers.py -q`; confirm PASS and that absent metadata is left absent.**
- [ ] **Step 5: Commit with `git add src/tcc_kit/sources tests/sources; git commit -m "feat: retrieve DOI metadata from Crossref and DataCite"`.**

### Task 3: Connect source lookup to the CLI and project record

**Files:**
- Modify: `src/tcc_kit/cli.py`
- Create: `src/tcc_kit/sources/service.py`
- Test: `tests/sources/test_source_command.py`
- Test: `tests/sources/fixtures/`
- Modify: `src/tcc_kit/assets/project/references.json`

**Interfaces:** `add_doi(project_dir: Path, raw_doi: str, opener=...) -> ReferenceRecord`; command `tcc-kit source add RAW_DOI --project PATH` prints each imported field, provenance, retrieval time, and missing-field list. The generated key is deterministic from author/year/title and is collision-checked before save.

- [ ] **Step 1: Test successful first lookup, duplicate DOI, same-key collision, provider timeout, malformed DOI, and missing required reference fields with mocked provider responses.**

```python
def test_add_doi_persists_provider_and_timestamp(project_dir, fake_lookup):
    record = add_doi(project_dir, "10.1234/example", opener=fake_lookup)
    saved = load_store(project_dir)[0]
    assert saved.key == record.key
    assert saved.provenance["title"].provider in {"crossref", "datacite"}
    assert saved.provenance["title"].retrieved_at
```

The test module defines `project_dir` with the existing `references.json` starter and `fake_lookup` as a fake opener that returns the Crossref agency response and a fixture record plus a fixed ISO timestamp; neither fixture performs network I/O.
- [ ] **Step 2: Run `python -m pytest tests/sources/test_source_command.py -q`; confirm failure before the service and command exist.**
- [ ] **Step 3: Implement candidate selection, key generation, collision suffixes, local save, duplicate-DOI local cache behavior, and concise PT-BR status output; do not auto-accept missing fields as verified.**
- [ ] **Step 4: Run the source tests and then the full offline suite `python -m pytest -q`; no test may call the public network.**
- [ ] **Step 5: Commit with `git add src/tcc_kit/cli.py src/tcc_kit/sources tests/sources; git commit -m "feat: add DOI lookup command with provenance"`.**

### Task 4: Validate citation keys and bibliography records

**Files:**
- Create: `src/tcc_kit/validation.py`
- Modify: `src/tcc_kit/cli.py`
- Test: `tests/test_validation.py`

**Interfaces:** `validate_project(project_dir: Path) -> list[Diagnostic]`; `Diagnostic(code: str, message: str, path: str, line: int | None, severity: str)`; `tcc-kit check PATH` exits 0 only when no error-severity diagnostics exist. Parse citation keys in the supported syntax `[@key]` and compare them with `references.json`.

- [ ] **Step 1: Test unknown citation, duplicate citation keys, missing required metadata, unsupported citation syntax, absent manuscript, and a fully resolved small project.**
- [ ] **Step 2: Run `python -m pytest tests/test_validation.py -q`; confirm errors are visible before code exists.**
- [ ] **Step 3: Implement deterministic line-aware scanning and field validation for the supported types `book`, `chapter`, `article-journal`, `thesis`, and `dataset`; unknown types produce warnings, not guessed conversions.**
- [ ] **Step 4: Run `python -m pytest tests/test_validation.py -q` and `python -m pytest -q`; confirm exact file/line diagnostics.**
- [ ] **Step 5: Commit with `git add src/tcc_kit/validation.py src/tcc_kit/cli.py tests/test_validation.py; git commit -m "feat: validate citations and reference records"`.**
