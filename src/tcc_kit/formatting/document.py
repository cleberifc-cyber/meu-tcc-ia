"""Modelo intermediário simples do manuscrito."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Block:
    kind: str
    text: str
    line_number: int
    level: int | None = None
    items: list[str] | None = None
    rows: list[list[str]] | None = None
    image_path: Path | None = None
    caption: str | None = None
