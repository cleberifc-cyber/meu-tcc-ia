# Contributing

Issues and pull requests are welcome. Before a larger change, open an issue describing the user problem and proposed scope. Keep changes focused and avoid introducing claims of automatic norm compliance without source-backed evidence.

## Local checks

```sh
python -m pip install -e ".[test]"
python -m pytest -q
python -m build
```

Tests must not depend on live network access. Use synthetic fixtures for source API responses and do not include copyrighted standards, real student submissions, tokens, or private research data. For ABNT profile proposals, identify the official source and edition, describe the smallest reproducible discrepancy, and state whether access is authorized.

## Pull requests

Explain the behavior changed, tests run, limitations, and any user-facing documentation update. New external requests must disclose exactly what is transmitted and remain opt-in.
