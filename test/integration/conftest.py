import pytest

from FLIR.conservator.config import Config
from FLIR.conservator.conservator import Conservator


@pytest.fixture()
def conservator():
    """
    Provides a Conservator connection to be used for testing.
    """
    return Conservator(Config.from_named_config_file("local"))
