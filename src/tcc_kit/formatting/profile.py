"""Carregamento e validação de perfis versionados de formatação."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


class ProfileValidationError(ValueError):
    pass


@dataclass(frozen=True)
class RuleProfile:
    id: str
    display_name: str
    status: str
    standards: list[dict[str, str]]
    official_catalog_url: str
    verified_at: str | None
    document: dict[str, object]
    references: dict[str, object]
    supported_blocks: list[str]

    @classmethod
    def load(cls, path: Path) -> "RuleProfile":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        try:
            profile = cls(**data)
        except TypeError as exc:
            raise ProfileValidationError("Manifesto de perfil incompleto ou desconhecido.") from exc
        if profile.status not in {"preview", "verified", "stale"}:
            raise ProfileValidationError("Estado do perfil deve ser preview, verified ou stale.")
        if profile.status == "verified" and (not profile.verified_at or not profile.standards or any(not item.get("edition") for item in profile.standards)):
            raise ProfileValidationError("Perfil verificado exige data e edição definida para cada norma.")
        return profile

    @classmethod
    def bundled(cls) -> "RuleProfile":
        path = files("tcc_kit").joinpath("assets", "profiles", "abnt-br-preview.toml")
        return cls.load(Path(str(path)))

    def status_message(self) -> str:
        if self.status == "preview":
            return "Perfil preview: regras e cobertura ainda não verificado contra todas as edições normativas aplicáveis."
        if self.status == "stale":
            return "Perfil desatualizado: verifique as edições normativas antes de usar o resultado."
        return f"Perfil verificado em {self.verified_at}; confira também o manual da sua instituição."
