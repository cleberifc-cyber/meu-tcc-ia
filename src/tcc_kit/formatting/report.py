"""Relatório reproduzível da geração do documento."""

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class BuildReport:
    output: str
    profile_id: str
    profile_status: str
    standard_editions: list[str]
    tool_versions: dict[str, str]
    warnings: list[str]
    source_hashes: dict[str, str]

    def write_json(self, path: Path) -> None:
        import json

        path.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
