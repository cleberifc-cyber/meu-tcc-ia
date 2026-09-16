"""Adaptador somente GET para a REST API do Crossref."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Callable
from urllib.parse import quote

from tcc_kit.sources.doi import DoiNotFoundError, SourceUnavailableError, normalize_doi
from tcc_kit.sources.models import Provenance, ReferenceRecord


def fetch_crossref(doi: str, opener: Callable = urllib.request.urlopen) -> ReferenceRecord:
    normalized = normalize_doi(doi)
    url = "https://api.crossref.org/works/" + quote(normalized, safe="/")
    request = urllib.request.Request(url, headers={"User-Agent": "tcc-kit/0.1 (metadata lookup; no manuscript content)"}, method="GET")
    try:
        with opener(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise DoiNotFoundError(f"DOI {normalized} não encontrado no Crossref.") from exc
        raise SourceUnavailableError(f"Crossref respondeu HTTP {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SourceUnavailableError("Não foi possível consultar Crossref; tente novamente mais tarde.") from exc
    message = data.get("message", {})
    if not isinstance(message, dict):
        raise SourceUnavailableError("Resposta inesperada do Crossref.")
    fields: dict[str, object] = {}
    if message.get("title"):
        fields["title"] = message["title"][0]
    if message.get("author"):
        fields["author"] = message["author"]
    if message.get("container-title"):
        fields["container_title"] = message["container-title"][0]
    if message.get("volume"):
        fields["volume"] = message["volume"]
    if message.get("issue"):
        fields["issue"] = message["issue"]
    if message.get("page"):
        fields["pages"] = message["page"]
    if message.get("publisher"):
        fields["publisher"] = message["publisher"]
    date = message.get("published-print") or message.get("published-online") or message.get("issued")
    if date and date.get("date-parts"):
        fields["issued"] = date["date-parts"][0]
    kind = message.get("type", "other")
    item_type = "article-journal" if kind == "journal-article" else kind
    now = datetime.now(timezone.utc).isoformat()
    provenance = {key: Provenance("crossref", normalized, now, url) for key in fields}
    return ReferenceRecord(normalized, item_type, fields, provenance, {})
