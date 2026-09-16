import pytest

from tcc_kit.cli import main


def test_help_lists_supported_commands(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])

    assert exc.value.code == 0
    output = capsys.readouterr().out
    for command in ("init", "prompt", "source", "check", "format"):
        assert command in output
