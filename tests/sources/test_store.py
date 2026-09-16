import pytest

from tcc_kit.sources.models import DuplicateReferenceError, ReferenceRecord
from tcc_kit.sources.store import load_store, save_record


def test_reference_round_trip_and_duplicate_rejection(tmp_path):
    record = ReferenceRecord(key="silva2024", item_type="book", fields={"title": "Exemplo"},
                             provenance={}, user_overrides={})
    save_record(tmp_path, record)
    assert load_store(tmp_path) == [record]
    with pytest.raises(DuplicateReferenceError):
        save_record(tmp_path, record)
    assert load_store(tmp_path) == [record]


def test_user_override_does_not_destroy_imported_field(tmp_path):
    record = ReferenceRecord(key="x1", item_type="book", fields={"title": "Original"},
                             provenance={}, user_overrides={"title": "Corrigido"})
    save_record(tmp_path, record)
    restored = load_store(tmp_path)[0]
    assert restored.fields["title"] == "Original"
    assert restored.user_overrides["title"] == "Corrigido"
