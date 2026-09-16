"""Monta instruções contextualizadas sem invocar um provedor de IA."""

from __future__ import annotations

import tomllib
from importlib.resources import files
from pathlib import Path

SECTIONS = {"introducao": "01-introducao.txt", "referencial": "02-referencial.txt", "metodologia": "03-metodologia.txt"}


def build_prompt(project_dir: Path, section: str) -> str:
    if section not in SECTIONS:
        raise ValueError(f"Seção desconhecida: {section}")
    profile = tomllib.loads((project_dir / "tcc.toml").read_text(encoding="utf-8"))
    project = profile.get("project", {})
    template = files("tcc_kit").joinpath("assets", "prompts", SECTIONS[section]).read_text(encoding="utf-8")
    details = "\n".join(f"- {key}: {project.get(key, 'Ainda não definido')}" for key in
                          ("topic", "course", "institution", "work_type", "problem", "objectives", "method"))
    return f"{template.strip()}\n\nDados informados pelo estudante:\n{details}\n"
