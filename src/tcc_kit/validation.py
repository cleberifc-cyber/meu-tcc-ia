"""Valida referências e citações locais, sem inferir bibliografia."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tcc_kit.sources.store import load_store


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    path: str
    line: int | None
    severity: str


_CITATION = re.compile(r"\[@([A-Za-z0-9_.:-]+)\]")
_REQUIRED = {
    "book": ("author", "title", "publisher", "issued"),
    "chapter": ("author", "title", "container_title"),
    "article-journal": ("author", "title", "container_title", "issued"),
    "thesis": ("author", "title", "institution", "issued"),
    "dataset": ("author", "title", "publisher", "issued"),
}


def validate_project(project_dir: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    manuscript = project_dir / "tcc.md"
    if not manuscript.is_file():
        return [Diagnostic("missing-manuscript", "Arquivo tcc.md não encontrado.", "tcc.md", None, "error")]
    references = load_store(project_dir)
    by_key: dict[str, object] = {}
    for record in references:
        if record.key in by_key:
            diagnostics.append(Diagnostic("duplicate-reference-key", f"Chave repetida: {record.key}", "references.json", None, "error"))
        by_key[record.key] = record
        required = _REQUIRED.get(record.item_type)
        if required is None:
            diagnostics.append(Diagnostic("unsupported-reference-type", f"Tipo sem mapeamento: {record.item_type}", "references.json", None, "warning"))
        else:
            effective = {**record.fields, **record.user_overrides}
            missing = [field for field in required if not effective.get(field)]
            if missing:
                diagnostics.append(Diagnostic("incomplete-reference", f"{record.key}: faltam {', '.join(missing)}.", "references.json", None, "warning"))
    text = re.sub(r"<!--.*?-->", "", manuscript.read_text(encoding="utf-8"), flags=re.S)
    used = set()
    for line_number, line in enumerate(text.splitlines(), 1):
        for match in _CITATION.finditer(line):
            used.add(match.group(1))
            if match.group(1) not in by_key:
                diagnostics.append(Diagnostic("unknown-citation", f"Citação sem registro: {match.group(1)}", "tcc.md", line_number, "error"))
        if "[@" in line and not _CITATION.search(line):
            diagnostics.append(Diagnostic("unsupported-citation-syntax", "Sintaxe de citação não reconhecida; use [@chave].", "tcc.md", line_number, "warning"))
    return diagnostics
