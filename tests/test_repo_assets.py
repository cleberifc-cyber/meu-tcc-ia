from pathlib import Path


def test_ci_covers_supported_python_and_operating_systems():
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "windows-latest" in workflow and "ubuntu-latest" in workflow
    assert "python -m pytest -q" in workflow
    assert "python -m build" in workflow


def test_security_and_privacy_are_explicit():
    security = Path("SECURITY.md").read_text(encoding="utf-8").casefold()
    privacy = Path("docs/privacy.md").read_text(encoding="utf-8").casefold()
    assert "privately" in security
    assert "never include api keys" in security
    assert "doi" in privacy and "manuscrito" in privacy


def test_issue_forms_do_not_request_private_manuscripts_or_keys():
    bug = Path(".github/ISSUE_TEMPLATE/bug.yml").read_text(encoding="utf-8").casefold()
    rule = Path(".github/ISSUE_TEMPLATE/rule-profile.yml").read_text(encoding="utf-8").casefold()
    assert "api" in bug and "manuscrito" in bug
    assert "não anexe a norma" in rule
