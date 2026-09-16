"""Serviço de importação e deduplicação de registros DOI."""

from __future__ import annotations

import re
import unicodedata
from typing import Callable

from tcc_kit.sources.crossref import fetch_crossref
from tcc_kit.sources.datacite import fetch_datacite
from tcc_kit.sources.doi import DoiFormatError, DoiNotFoundError, SourceUnavailableError, normalize_doi
from tcc_kit.sources.models import Provenance, ReferenceRecord
from tcc_kit.sources.store import load_store, save_record


def lookup_doi(doi: str, opener: Callable | None = None) -> ReferenceRecord:
    normalized = normalize_doi(doi)
    import json
    import urllib.error
    import urllib.request
    from urllib.parse import quote

    url = "https://api.crossref.org/works/" + quote(normalized, safe="/") + "/agency"
    request = urllib.request.Request(url, headers={"User-Agent": "tcc-kit/0.1 (DOI agency lookup)"}, method="GET")
    open_url = opener or urllib.request.urlopen
    try:
        with open_url(request, timeout=10) as response:
            agency = json.loads(response.read().decode("utf-8")).get("message", {}).get("agency", {}).get("id", "").casefold()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise DoiNotFoundError(f"DOI {normalized} não está registrado.") from exc
        raise SourceUnavailableError(f"A agência DOI respondeu HTTP {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SourceUnavailableError("Não foi possível identificar a agência do DOI.") from exc
    if agency == "crossref":
        record = fetch_crossref(normalized, opener=open_url)
    elif agency == "datacite":
        record = fetch_datacite(normalized, opener=open_url)
    else:
        raise SourceUnavailableError(f"Agência registradora não suportada: {agency or 'desconhecida'}.")
    fields = {**record.fields, "doi": normalized}
    provenance = dict(record.provenance)
    provenance["doi"] = Provenance(agency, normalized, next(iter(provenance.values())).retrieved_at if provenance else "", f"https://doi.org/{normalized}")
    return ReferenceRecord(record.key, record.item_type, fields, provenance, record.user_overrides)


def _slug(value: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
    result = re.sub(r"[^a-z0-9]+", "", ascii_text)
    return result or "fonte"


def add_doi(project_dir, raw_doi: str, opener=None, lookup: Callable | None = None) -> ReferenceRecord:
    normalized = normalize_doi(raw_doi)
    records = load_store(project_dir)
    for existing in records:
        if existing.fields.get("doi", "").casefold() == normalized:
            return existing
    candidate = (lookup or lookup_doi)(normalized, opener=opener)
    authors = candidate.fields.get("author") or []
    family = "fonte"
    if authors and isinstance(authors, list) and isinstance(authors[0], dict):
        family = authors[0].get("family") or authors[0].get("name") or family
    issued = candidate.fields.get("issued", [])
    year = str(issued[0] if isinstance(issued, list) and issued else "sdata")[:4]
    title = str(candidate.fields.get("title", ""))
    base = f"{_slug(str(family))}{year}{_slug(title)[:16]}"
    keys = {record.key.casefold() for record in records}
    key = base
    suffix = 2
    while key.casefold() in keys:
        key = f"{base}{suffix}"
        suffix += 1
    provenance = dict(candidate.provenance)
    if "doi" not in provenance:
        exemplar = next(iter(provenance.values()), Provenance("unknown", normalized, "", None))
        provenance["doi"] = Provenance(exemplar.provider, normalized, exemplar.retrieved_at, f"https://doi.org/{normalized}")
    record = ReferenceRecord(key, candidate.item_type, {**candidate.fields, "doi": normalized}, provenance, candidate.user_overrides)
    save_record(project_dir, record)
    return record
