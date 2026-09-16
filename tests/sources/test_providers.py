import io
import json

from tcc_kit.sources.crossref import fetch_crossref


def test_missing_crossref_author_stays_missing():
    payload = {"message": {"title": ["Artigo de exemplo"], "type": "journal-article", "DOI": "10.1234/exemplo"}}

    def opener(request, timeout):
        assert request.get_method() == "GET"
        assert timeout == 10
        return io.BytesIO(json.dumps(payload).encode())

    record = fetch_crossref("10.1234/exemplo", opener=opener)
    assert record.fields["title"] == "Artigo de exemplo"
    assert "author" not in record.fields
