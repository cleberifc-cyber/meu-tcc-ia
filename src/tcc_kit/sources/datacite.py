"""Adaptador somente GET para a REST API DataCite."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Callable
from urllib.parse import quote

from tcc_kit.sources.doi import DoiNotFoundError, SourceUnavailableError, normalize_doi
from tcc_kit.sources.models import Provenance, ReferenceRecord


def fetch_datacite(doi: str, opener: Callable = urllib.request.urlopen) -> ReferenceRecord:
    normalized = normalize_doi(doi)
    url = "https://api.datacite.org/dois/" + quote(normalized, safe="/")
    request = urllib.request.Request(url, headers={"User-Agent": "tcc-kit/0.1 (metadata lookup; no manuscript content)"}, method="GET")
    try:
        with opener(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise DoiNotFoundError(f"DOI {normalized} não encontrado no DataCite.") from exc
        raise SourceUnavailableError(f"DataCite respondeu HTTP {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SourceUnavailableError("Não foi possível consultar DataCite; tente novamente mais tarde.") from exc
    attributes = data.get("data", {}).get("attributes", {})
    if not isinstance(attributes, dict):
        raise SourceUnavailableError("Resposta inesperada do DataCite.")
    fields: dict[str, object] = {}
    titles = attributes.get("titles") or []
    if titles and titles[0].get("title"):
        fields["title"] = titles[0]["title"]
    creators = attributes.get("creators") or []
    if creators:
        fields["author"] = creators
    if attributes.get("publisher"):
        fields["publisher"] = attributes["publisher"]
    if attributes.get("publicationYear"):
        fields["issued"] = [attributes["publicationYear"]]
    if attributes.get("url"):
        fields["url"] = attributes["url"]
    resource_type = (attributes.get("types") or {}).get("resourceTypeGeneral", "other")
    item_type = {"Dataset": "dataset", "Text": "other", "Dissertation": "thesis"}.get(resource_type, "other")
    now = datetime.now(timezone.utc).isoformat()
    record_url = "https://api.datacite.org/dois/" + quote(normalized, safe="/")
    provenance = {key: Provenance("datacite", normalized, now, record_url) for key in fields}
    return ReferenceRecord(normalized, item_type, fields, provenance, {})
