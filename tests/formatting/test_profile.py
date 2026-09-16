import pytest

from tcc_kit.formatting.profile import ProfileValidationError, RuleProfile


def test_bundled_profile_is_clearly_preview():
    profile = RuleProfile.bundled()
    assert profile.status == "preview"
    assert "não verificado" in profile.status_message().casefold()


def test_verified_profile_requires_date_and_edition(tmp_path):
    path = tmp_path / "profile.toml"
    path.write_text('id="x"\ndisplay_name="x"\nstatus="verified"\nverified_at=""\nstandards=[]\n', encoding="utf-8")
    with pytest.raises(ProfileValidationError):
        RuleProfile.load(path)
