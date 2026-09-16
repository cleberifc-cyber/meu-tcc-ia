from tcc_kit.sources.models import Provenance, ReferenceRecord
from tcc_kit.sources.service import add_doi
from tcc_kit.sources.store import load_store


def fake_lookup(doi, opener=None):
    return ReferenceRecord("temporary", "article-journal", {"title": "Um estudo", "author": [{"family": "Silva"}], "issued": [2024]},
                          {"title": Provenance("crossref", doi, "2026-01-01T00:00:00+00:00", f"https://doi.org/{doi}")}, {})


def test_add_doi_saves_deterministic_key_and_provenance(tmp_path):
    record = add_doi(tmp_path, "10.1234/exemplo", lookup=fake_lookup)
    saved = load_store(tmp_path)[0]
    assert record.key == saved.key
    assert record.fields["doi"] == "10.1234/exemplo"
    assert saved.provenance["title"].provider == "crossref"
