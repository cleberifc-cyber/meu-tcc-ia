# TCC Studio: guided, source-aware ABNT workflow

**Status:** design draft for Cleber's review

**Date:** 2026-09-16

**Repository:** `cleberifc-cyber/meu-tcc-ia`

## 1. Product intent

Turn this repository from a set of starter files into a cloneable, approachable open-source toolkit that helps a student move from a few grounded project details to a structured, reviewable TCC workspace and a consistently formatted document.

The standout capability is a whole-document ABNT formatting workflow connected to traceable bibliographic metadata lookup. The first-run experience must be understandable to a person who has never used the repository or a command line before. Power users may still use the CLI and edit Markdown/BibTeX directly.

The project assists academic work; it does not promise a grade, originality, acceptance, complete research, or universal institutional compliance. A student remains responsible for the argument, evidence, source checks, research decisions, and rules of their institution.

## 2. Users and first-run outcome

Primary users are students in Brazil who need to organize and format a course-completion project. The repository should be useful to a person who:

- clones the public repository and follows a short Portuguese quick start;
- supplies the course, institution, type of work, topic, problem, objectives, methodology status, and sources they actually have;
- receives a structured project folder, a tailored work plan, staged writing prompts, and explicit missing-information questions;
- can format and validate the document locally without uploading academic content;
- can optionally configure an AI provider for direct generation, or copy the generated prompt/context into an assistant of their choice.

PT-BR is the canonical onboarding language for the initial release. A concise English README is included for discoverability; translated academic rule explanations must point back to the same versioned rule profile rather than silently diverging.

## 3. Proposed user journey

1. **Clone and start:** README shows a three-step quick start, prerequisite check, one small demo, and a clear privacy statement.
2. **Initialize:** `tcc-kit init` starts a guided questionnaire. It accepts command-line options for automation and interactive answers for new users. It explains why each field matters and allows “ainda não sei” where that is a legitimate project state.
3. **Create a plan:** generate a project profile, chapter outline, staged prompt files, source register, and review checklist. Do not fabricate a problem statement, method, data, findings, or references to fill blanks.
4. **Draft in controlled stages:** `tcc-kit next` prepares the next section's context/prompt from confirmed project data and sources. In no-provider mode it saves a copy-ready prompt. With an explicitly configured provider, it shows what will be sent and requires the user to opt in.
5. **Resolve references:** `tcc-kit source add <DOI-or-identifier>` retrieves available metadata from the DOI registration agency, creates a candidate record with field-level provenance, and asks the user to confirm or correct it. Missing metadata remains visibly missing.
6. **Check and format:** `tcc-kit check` reports structural, citation-key, and reference-field problems. `tcc-kit format` creates DOCX and/or PDF from the project source using the selected, versioned profile; it never describes an unchecked file as guaranteed compliant.
7. **Review:** show a concise report: profile and standard editions applied, sources looked up and lookup dates, user-edited fields, warnings, unavailable checks, tool versions, and output paths.

The first-run flow is local and works without an AI key. Direct AI generation is optional and requires the user to configure a provider. Provider-specific access, model availability, cost, and retention remain the user's choice and are disclosed before content is transmitted.

## 4. Product components

### 4.1 Cloneable starter and guided project initializer

- Keep the repository itself as the reusable upstream template; `init` creates a separate project directory and does not modify the installation.
- Capture only the information needed to produce a useful next step. Distinguish confirmed facts, user choices, open questions, and suggestions in generated project files.
- Generate an editable `tcc.yml` profile, Markdown manuscript skeleton, BibTeX/CSL-JSON source store, staged prompts, and a progress/checklist file.
- Support undergraduate TCC and configurable work type; avoid hard-coding a single department's structure as universal.
- Offer accessible messages, examples, and recovery from interrupted questionnaires.

### 4.2 Bibliographic source adapters

Implement a provider interface with explicit source and retrieval timestamp. Initial DOI adapters:

- **Crossref REST API** for DOI metadata deposited by its members.
- **DataCite REST API** for DataCite DOI records.
- Preserve the source record identifier and link for every imported field where available; record user corrections separately from imported values.
- Do not claim that returned metadata is complete or correct. Crossref explicitly describes its API as member-deposited metadata and provides a route for reporting errors; DataCite exposes its DOI metadata and metadata version through its REST API.
- Resolve metadata before styling. The reference renderer maps typed fields to a versioned rule profile; provider-specific JSON must not be embedded in formatter logic.
- ISBN and arbitrary URL/publisher/catalog adapters are follow-on adapters. Do not label a search-engine result as the source of record. If the provider is ambiguous, show candidates and ask the student to choose.
- Public lookup requires no account where the provider's public API supports it. Use respectful rate limits, timeouts, caching, retry/backoff, and clear offline/error handling.

### 4.3 Versioned ABNT formatting engine

Formatting is a first-class subsystem, not a README promise. It has three distinct layers:

1. **Content model:** typed document structure, citation keys, bibliography metadata, tables/figures, headings, and front-matter fields.
2. **Rule profiles:** versioned implementation of the supported presentation/citation/reference rules, with explicit standard identifier and edition, last-verified date, official catalog link, status, supported resource types, and known limitations.
3. **Renderers:** create DOCX and PDF using reproducible templates and locally installed tools. A user can select a versioned institutional override without overwriting the underlying ABNT profile.

Initial profile scope: work presentation (NBR 14724), citations (NBR 10520), and references (NBR 6023); NBR 6022 is supported only when the selected work type is an article and the profile's coverage has been verified. The normative standard edition and institution-specific manual are separate configuration inputs. The CLI must print the editions actually applied instead of a generic “ABNT updated” badge.

Every profile change requires a dated changelog entry, rule-specific fixtures, and a review of representative outputs. Tests use brief original examples, not copied passages or bundled scans of normative documents. The repository will not bundle purchased standards or scrape gated material. If ABNT offers an authorized machine-readable feed or API, integration is a separate capability requiring terms/access verification. Until then, monitor the official catalog and update profiles through a transparent maintainer-reviewed release; show a stale/verification warning whenever the last check exceeds the documented freshness window.

Formatting coverage is explicit. Unsupported source types, unverified typography details, inaccessible PDF tools, local manual conflicts, and ambiguous citations produce warnings or blocking errors; they must not be silently “fixed” by guessed rules.

### 4.4 Document build

Use a single Markdown-based source of truth and a tested export pipeline. The local implementation environment already has `python-docx` and does not have Pandoc, so `python-docx` is the leading candidate for editable DOCX output and simple installation. Its ability to express the needed profile and fixtures must be verified before the renderer is considered established. PDF is an optional reproducible build through LibreOffice or another explicitly detected local converter; never make PDF conversion a hidden requirement for the clone-first path. Pandoc remains an alternative only if a concrete fixture comparison shows a clear benefit.

The exported document includes only content present in the project source. It must not invent title-page facts, page numbers for citations, tables, figures, appendices, or research results. Build output includes a machine-readable report listing inputs, profile version, renderer version, and warnings.

### 4.5 AI-assisted drafting boundary

- The default experience is provider-neutral and does not transmit user work.
- Prompts direct the model to ask for missing evidence, label unsupported claims, preserve source traceability, and draft one section at a time.
- Optional providers use a narrow adapter interface. Credentials come from environment variables or a local ignored configuration file; never commit credentials or send them to the repository.
- Before a request, display the provider, model if known, files/fields to be sent, and an explicit confirmation. Provide a prompt-only path that requires no account or key.
- Model output is an unreviewed draft. Never mark AI text as a verified source, a completed research procedure, or institution-approved work.

## 5. Architecture and boundaries

Suggested package layout (names may change during implementation without changing the user contract):

```text
src/tcc_kit/
  cli/                 # command parsing and terminal UX
  project/              # questionnaire, project profile, scaffold generation
  sources/              # DOI adapters, normalized metadata, provenance
  rules/abnt/           # versioned profiles, validation and formatting rules
  document/              # manuscript model, Pandoc adapter, render report
  providers/             # optional AI-provider adapters
tests/
  fixtures/              # original synthetic and permission-cleared examples
templates/
  project/               # generated-workspace starter files
  abnt/<profile-version>/# versioned templates and profile metadata
docs/
  quickstart/             # PT-BR first-run guide and English entrypoint
```

The core orchestrates interfaces and local files. It does not depend on a hosted database, account system, telemetry, or vendor AI SDK. Network clients are isolated and opt-in per operation. Provider APIs, style profiles, and renderers can be replaced independently.

## 6. Failure, privacy, and integrity behavior

- Network unavailable: retain typed user-entered metadata; explain that lookup could not be completed; allow later refresh.
- DOI unknown or multiple candidate records: return a non-destructive error/candidate list; never invent a record.
- Missing metadata: generate a partial draft only if the user approves; mark missing fields and keep the result out of the “verified” state.
- Stale/unverified ABNT profile: display edition and verification date prominently; allow output only with a warning or fail according to the user's selected strictness, never silently imply currency.
- Institution-specific conflict: preserve both profile values and ask the user to select/record an override.
- AI-provider failure or missing key: continue with prompt-only mode; redact secrets from logs and errors.
- Validation errors: point to file, section, field, and suggested next action. Never overwrite source manuscripts during formatting.
- No default telemetry. Source lookup and AI transmission are disclosed separately. Provide a `.gitignore` that excludes keys, drafts marked private if opted in, caches, and generated binaries.

## 7. Open-source presentation and adoption

Make the repository welcoming and credible rather than relying on star requests:

- README with PT-BR/English language links, quick-start copy/paste commands, supported-format matrix, honest status badges, short terminal/demo recording, architecture summary, privacy statement, and limitations.
- `CONTRIBUTING.md`, a clear code-of-conduct, issue forms for bugs/rule changes/providers, security reporting instructions, changelog, roadmap, license decision, and a reproducible release checklist.
- Demo project uses fictional names, original example sources/data, and is clearly labelled as a demonstration, not a submission-ready thesis.
- Search-friendly description/topics and a release note that names what the profile does and does not support.
- No automated star-gating, self-star requests, fabricated user testimonials, or claims such as “guaranteed grade/100% ABNT”.

## 8. Delivery phases

### Phase 0 — foundation and acceptance fixtures

Confirm the legal/operational source access boundary; define normalized source record and profile manifest; produce original test cases for supported reference types and whole-document output; establish install and CI matrix. Do not market compliance before these pass.

### Phase 1 — first useful clone

Ship beginner quick start, PT-BR initializer, project profile/templates, local `check`, DOI lookup for Crossref/DataCite with provenance, prompt-only staged drafting, and one validated DOCX/PDF profile path. Add offline-friendly behavior and tests.

### Phase 2 — broader coverage

Add further source types/providers (ISBN/catalog/publisher as independently verified), article-type profile, improved PDF renderer and institution overrides, English guides, accessible UI refinements, and routine profile-change governance.

### Phase 3 — optional AI automation and community integrations

Add selected provider adapters only when consent display, secret handling, cost disclosure, and tests are in place. Evaluate Zotero-compatible interchange and additional exporters based on community demand; do not add a hosted service without a separate privacy/security design.

## 9. Acceptance criteria for the first release

1. A new user can clone, follow one tested quick-start path on Windows and Linux/macOS, answer the minimum questionnaire, and receive a ready-to-edit project without an AI key.
2. A user can add a known Crossref DOI and a known DataCite DOI; normalized metadata matches fixed, permission-cleared fixtures; each imported field has source/provenance or is clearly marked as user-supplied/unresolved.
3. A bad DOI, API timeout, rate limit, missing field, duplicate candidate, or invalid reference produces actionable output, never fabricated metadata.
4. Supported citations resolve to bibliography records; unresolved keys and unused/missing fields are reported with file/line context.
5. DOCX and PDF exports are compared against versioned structural/layout fixtures: page geometry, heading hierarchy, front matter, citation/reference render, and table/figure behavior for the explicitly supported cases.
6. Every export records the exact ABNT profile/edition, institutional override, renderer, and verification timestamp. Stale or unsupported states are visible in both CLI output and report.
7. Offline tests run without live APIs; optional integration tests use recorded/approved fixtures. No source manuscript is overwritten by check/format.
8. Default mode makes zero AI-provider calls and sends no manuscript content over the network. AI mode cannot run until a user configures a provider and confirms the exact outgoing context.
9. README, examples, screenshots/demo, issue templates, contribution path, and release status are accurate; CI failures are reported honestly and do not turn blocked infrastructure into a pass.

## 10. Risks and decision log

| Risk | Design response |
|---|---|
| Bibliographic registry record is incomplete or inaccurate | Field-level provenance, discrepancy/missing-field warnings, student confirmation and correction log. |
| ABNT rule changes but no public machine-readable rules feed is available | Official-catalog monitoring, explicit verified-at date, versioned rule profiles and reviewed releases; do not auto-claim real-time normative coverage. |
| Institutional manual varies from ABNT or across program types | Separate institution override/profile and expose the exact sources/choices applied. |
| Full-document formatting is more complex than reference-list formatting | Acceptance fixtures and one narrow supported profile first; explicitly mark uncovered structures. |
| LLM generates plausible but unsupported citations/claims | Separate generation from source validation; require source-backed evidence and human review; never allow AI output to create a verified reference automatically. |
| Install complexity reduces adoption | One-command bootstrap, Python prerequisite checks, platform smoke tests, and clear optional PDF tool installation. |
| GitHub Actions cannot run in the owner's account | Run checks locally and keep workflow definitions; surface account/billing block as external/pending rather than claim CI success. |

### Source references checked while preparing this design

- Crossref REST API documentation (member-deposited scholarly metadata, public API, and metadata-use details): <https://www.crossref.org/documentation/retrieve-metadata/rest-api/>
- Crossref REST API tips (selective/reliable API use and record-quality considerations): <https://www.production.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/>
- DataCite REST API guide (public DOI metadata retrieval and provenance): <https://support.datacite.org/docs/rest-api>
- DataCite single-DOI endpoint (metadata version/source fields): <https://support.datacite.org/docs/api-get-doi>
- ABNT official catalog for standards search/status/access: <https://www.abntcatalogo.com.br/>
- `python-docx` project and documentation for creating/editing OOXML DOCX files: <https://python-docx.readthedocs.io/>
- Pandoc official manual (evaluated as an alternative for reference DOCX, citations/CSL and PDF output): <https://pandoc.org/MANUAL.html>
- GitHub Actions billing and usage documentation: <https://docs.github.com/en/actions/concepts/billing-and-usage>

## 11. Self-review checklist

- No unresolved placeholders or TBD requirements remain.
- “Live bibliographic source lookup” is distinct from “live access to the full normative text”.
- Automatic profile revision is explicitly gated on official source verification and authorized access; profile version and last-check date are required outputs.
- DOCX is the editable primary deliverable; PDF prerequisites are explicit.
- Renderer choice is based on an installable local spike; DOCX fixtures determine whether `python-docx` meets the intended output contract.
- A no-AI-key path remains usable, while automated generation clearly requires user-provided provider access.
- Tests cover source data, failure modes, profile versions, and rendered output before compliance claims are made.
- User-facing promise is high-quality guided assistance, not guaranteed academic success or universal compliance.
