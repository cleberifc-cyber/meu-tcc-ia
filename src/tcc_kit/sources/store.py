"""Armazenamento local e atômico de referências."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from tcc_kit.sources.models import DuplicateReferenceError, Provenance, ReferenceRecord


def load_store(project_dir: Path) -> list[ReferenceRecord]:
    path = project_dir / "references.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("references"), list):
        raise ValueError("Formato inválido em references.json.")
    records = []
    for item in data["references"]:
        if not isinstance(item, dict) or not {"key", "item_type", "fields", "provenance", "user_overrides"} <= item.keys():
            raise ValueError("Registro de referência inválido.")
        prov = {field: Provenance(**value) for field, value in item["provenance"].items()}
        records.append(ReferenceRecord(item["key"], item["item_type"], item["fields"], prov, item["user_overrides"]))
    return records


def save_record(project_dir: Path, record: ReferenceRecord, replace: bool = False) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    path = project_dir / "references.json"
    records = load_store(project_dir)
    matches = [index for index, existing in enumerate(records) if existing.key.casefold() == record.key.casefold()]
    if matches and not replace:
        raise DuplicateReferenceError(f"A chave '{record.key}' já existe.")
    if matches:
        records[matches[0]] = record
    else:
        records.append(record)
    payload = {"schema_version": 1, "references": [asdict(item) for item in records]}
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    fd, temporary = tempfile.mkstemp(prefix="references-", suffix=".tmp", dir=project_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        Path(temporary).replace(path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
