from tcc_kit.project import create_project
from tcc_kit.validation import validate_project


ANSWERS = {"topic": "Acessibilidade digital", "course": "Sistemas", "institution": "IFC",
           "work_type": "monografia", "problem": "Ainda não definido",
           "objectives": "Ainda não definido", "method": "Ainda não definido"}


def test_unknown_citation_has_line_diagnostic(tmp_path):
    project = tmp_path / "p"
    create_project(project, ANSWERS)
    (project / "tcc.md").write_text("# Introdução\n\nTexto [@desconhecida].\n", encoding="utf-8")
    diagnostics = validate_project(project)
    assert any(d.code == "unknown-citation" and d.line == 3 for d in diagnostics)


def test_clean_project_has_no_errors(tmp_path):
    project = tmp_path / "p"
    create_project(project, ANSWERS)
    assert not [d for d in validate_project(project) if d.severity == "error"]
