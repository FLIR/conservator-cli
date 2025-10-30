import pytest


def test_cli():
    import FLIR.conservator.cli as cli

    # because this file was executed without arguments, the cli will
    # raise a SystemExit exception.
    with pytest.raises(SystemExit) as exits:
        cli.main()
    assert exits.type == SystemExit
