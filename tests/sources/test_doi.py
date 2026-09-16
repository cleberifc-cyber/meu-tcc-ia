import pytest

from tcc_kit.sources.doi import DoiFormatError, normalize_doi


def test_normalize_doi_accepts_resolver_url():
    assert normalize_doi("https://doi.org/10.1234/Ab.C") == "10.1234/ab.c"


def test_normalize_doi_rejects_non_doi():
    with pytest.raises(DoiFormatError):
        normalize_doi("not a DOI")
