# Third-party components and data

- Python standard library: CLI, local JSON/TOML handling and HTTP client.
- `python-docx`: optional project dependency used to create editable DOCX documents; see the project metadata and upstream license.
- `pytest` and `build`: development/test extras.
- Crossref REST API and DataCite REST API: queried for DOI metadata only when the user requests a lookup. Their records are third-party deposited metadata and may be incomplete or incorrect.
- ABNT catalog: linked as the official place to consult standards; this repository does not bundle the standards or access their full normative text.

No third-party thesis text, ABNT standard text, or sample bibliography records are bundled in the generated project template.
