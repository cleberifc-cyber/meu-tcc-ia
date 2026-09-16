"""Parser limitado e seguro do subconjunto Markdown documentado."""

from __future__ import annotations

import re
from pathlib import Path

from tcc_kit.formatting.document import Block


def parse_manuscript(text: str, project_dir: Path) -> list[Block]:
    lines = text.splitlines()
    blocks: list[Block] = []
    index = 0
    if lines and lines[0].strip() == "---":
        try:
            end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        except StopIteration:
            return [Block("diagnostic", "Frontmatter sem delimitador de fechamento (linha 1).", 1)]
        blocks.append(Block("frontmatter", "\n".join(lines[1:end]), 1))
        index = end + 1
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        line_number = index + 1
        if not stripped or stripped == "---":
            index += 1
            continue
        if stripped.startswith("#") and stripped.lstrip("#").startswith(" "):
            level = len(stripped) - len(stripped.lstrip("#"))
            blocks.append(Block("heading", stripped[level:].strip(), line_number, level=min(level, 3)))
            index += 1
            continue
        if re.search(r"<[^>]+>", stripped):
            blocks.append(Block("diagnostic", f"HTML não suportado (linha {line_number}).", line_number))
            index += 1
            continue
        image = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", stripped)
        if image:
            target = image.group(2)
            if re.match(r"https?://", target, re.I):
                blocks.append(Block("diagnostic", f"Imagem remota não suportada (linha {line_number}).", line_number))
            else:
                root = project_dir.resolve()
                path = (project_dir / target).resolve()
                if root not in path.parents:
                    blocks.append(Block("diagnostic", f"Caminho de imagem fora do projeto recusado (linha {line_number}).", line_number))
                elif not path.is_file():
                    blocks.append(Block("diagnostic", f"Imagem local não encontrada: {target} (linha {line_number}).", line_number))
                else:
                    blocks.append(Block("image", "", line_number, image_path=path, caption=image.group(1)))
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and re.fullmatch(r"\|?[\s:|-]+\|?", lines[index + 1].strip()):
            rows = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in [stripped]]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            blocks.append(Block("table", "", line_number, rows=rows))
            continue
        marker = re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)(.*)$", raw)
        if marker:
            items = []
            while index < len(lines):
                match = re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)(.*)$", lines[index])
                if not match:
                    break
                items.append(match.group(1).strip())
                index += 1
            blocks.append(Block("list", "", line_number, items=items))
            continue
        paragraph = [stripped]
        index += 1
        while index < len(lines) and lines[index].strip() and not lines[index].lstrip().startswith(("#", "- ", "* ", "+ ", "|", "![", "<")):
            paragraph.append(lines[index].strip())
            index += 1
        blocks.append(Block("paragraph", " ".join(paragraph), line_number))
    return blocks
