import json
from pathlib import Path

from tcc_kit.project import create_project


def test_demo_answers_create_a_project_without_network_or_ai(tmp_path):
    answers = json.loads(Path("examples/demo/answers.json").read_text(encoding="utf-8"))
    created = create_project(tmp_path / "demo", answers)
    assert (tmp_path / "demo" / "tcc.md").exists()
    assert (tmp_path / "demo" / "references.json").exists()
    assert any(path.name == "tcc.toml" for path in created)
    assert "Ainda não definido" in (tmp_path / "demo" / "tcc.toml").read_text(encoding="utf-8")


def test_readme_links_to_social_preview():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "social-preview.png" in readme
    assert Path(".github/social-preview.png").is_file()
