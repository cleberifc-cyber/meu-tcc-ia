"""Coleta e persistência dos dados iniciais de um TCC."""

from __future__ import annotations

import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Callable


FIELDS = ("topic", "course", "institution", "work_type", "problem", "objectives", "method")
QUESTIONS = {
    "topic": "Tema provisório do TCC",
    "course": "Curso",
    "institution": "Instituição de ensino",
    "work_type": "Tipo de trabalho (monografia, artigo ou projeto)",
    "problem": "Problema de pesquisa (ou 'Ainda não definido')",
    "objectives": "Objetivo(s) (ou 'Ainda não definido')",
    "method": "Metodologia (ou 'Ainda não definida')",
}


def collect_answers(read: Callable[[str], str], write: Callable[[str], None]) -> dict[str, str]:
    answers: dict[str, str] = {}
    for key in FIELDS:
        while True:
            value = read(f"{QUESTIONS[key]}: ").strip()
            if value:
                answers[key] = value
                break
            write("Esse campo não pode ficar vazio. Se ainda não souber, escreva 'Ainda não definido'.")
    return answers


def validate_answers(answers: dict[str, str]) -> list[str]:
    errors: list[str] = []
    unknown = sorted(set(answers) - set(FIELDS))
    if unknown:
        errors.append("Campos desconhecidos: " + ", ".join(unknown))
    for key in FIELDS:
        if key not in answers or not str(answers[key]).strip():
            errors.append(f"Informe {QUESTIONS[key].split(' (')[0].lower()}.")
    return errors


def render_project_toml(answers: dict[str, str]) -> str:
    errors = validate_answers(answers)
    if errors:
        raise ValueError("; ".join(errors))
    lines = ["[project]"]
    lines.extend(f"{key} = {json.dumps(answers[key].strip(), ensure_ascii=False)}" for key in FIELDS)
    lines.extend(("", "[formatting]", 'profile = "abnt-br-preview"', 'profile_status = "preview"', ""))
    return "\n".join(lines)


def create_project(destination: Path, answers: dict[str, str]) -> list[Path]:
    if destination.exists():
        raise FileExistsError(destination)
    errors = validate_answers(answers)
    if errors:
        raise ValueError("; ".join(errors))
    destination.mkdir(parents=True, exist_ok=False)
    profile = destination / "tcc.toml"
    profile.write_text(render_project_toml(answers), encoding="utf-8")
    created = [profile]
    asset_root = files("tcc_kit").joinpath("assets", "project")
    for name in ("README.md", "tcc.md", "references.json"):
        target = destination / name
        target.write_text(asset_root.joinpath(name).read_text(encoding="utf-8"), encoding="utf-8")
        created.append(target)
    (destination / "prompts").mkdir()
    prompt_root = files("tcc_kit").joinpath("assets", "prompts")
    for name in ("01-introducao.txt", "02-referencial.txt", "03-metodologia.txt"):
        target = destination / "prompts" / name
        target.write_text(prompt_root.joinpath(name).read_text(encoding="utf-8"), encoding="utf-8")
        created.append(target)
    return created
