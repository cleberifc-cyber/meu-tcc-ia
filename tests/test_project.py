import tomllib

import pytest

from tcc_kit.project import create_project, validate_answers


ANSWERS = {
    "topic": "Acessibilidade digital",
    "course": "Sistemas",
    "institution": "IFC",
    "work_type": "monografia",
    "problem": "Ainda não definido",
    "objectives": "Ainda não definido",
    "method": "Ainda não definido",
}


def test_create_project_writes_answers_without_overwriting(tmp_path):
    destination = tmp_path / "meu-tcc"
    created = create_project(destination, ANSWERS)

    config = tomllib.loads((destination / "tcc.toml").read_text(encoding="utf-8"))
    assert config["project"]["topic"] == ANSWERS["topic"]
    assert destination / "tcc.toml" in created
    assert destination / "tcc.md" in created
    assert destination / "references.json" in created
    assert (destination / "prompts" / "01-introducao.txt").exists()
    with pytest.raises(FileExistsError):
        create_project(destination, ANSWERS)


def test_topic_must_not_be_blank():
    errors = validate_answers({**ANSWERS, "topic": "  "})
    assert any("tema" in error.casefold() for error in errors)


def test_unknown_fields_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="desconhecido"):
        create_project(tmp_path / "meu-tcc", {**ANSWERS, "secret": "x"})
