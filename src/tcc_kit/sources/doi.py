"""Normalização de DOI sem consultar a rede."""

import re
from urllib.parse import unquote


class DoiFormatError(ValueError):
    pass


class DoiNotFoundError(LookupError):
    pass


class SourceUnavailableError(ConnectionError):
    pass


def normalize_doi(value: str) -> str:
    doi = value.strip()
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = unquote(doi).strip().rstrip(".,;)")
    if not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
        raise DoiFormatError("DOI inválido. Informe um DOI como 10.1234/exemplo.")
    return doi.lower()
