from tcc_kit.project import create_project
from tcc_kit.prompts import build_prompt


ANSWERS = {
    "topic": "Acessibilidade digital", "course": "Sistemas", "institution": "IFC",
    "work_type": "monografia", "problem": "Ainda não definido",
    "objectives": "Ainda não definido", "method": "Ainda não definido",
}


def test_build_prompt_is_project_specific(tmp_path):
    create_project(tmp_path / "p", ANSWERS)
    prompt = build_prompt(tmp_path / "p", "introducao")
    assert "Acessibilidade digital" in prompt
    assert "não invente" in prompt.casefold()


def test_unknown_section_is_rejected(tmp_path):
    create_project(tmp_path / "p", ANSWERS)
    try:
        build_prompt(tmp_path / "p", "conclusao")
    except ValueError as exc:
        assert "seção" in str(exc).casefold()
    else:
        raise AssertionError("seção desconhecida foi aceita")
