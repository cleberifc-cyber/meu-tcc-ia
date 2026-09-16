"""Modelos normalizados de referências e proveniência."""

from dataclasses import dataclass


class DuplicateReferenceError(ValueError):
    """A chave de referência já existe no projeto."""


@dataclass(frozen=True)
class Provenance:
    provider: str
    record_id: str
    retrieved_at: str
    record_url: str | None = None


@dataclass(frozen=True)
class ReferenceRecord:
    key: str
    item_type: str
    fields: dict[str, object]
    provenance: dict[str, Provenance]
    user_overrides: dict[str, object]
