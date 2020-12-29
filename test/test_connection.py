from FLIR.conservator.conservator import Conservator


def test_credentials():
    conservator = Conservator.default(save=False)
    assert conservator.get_user() is not None
