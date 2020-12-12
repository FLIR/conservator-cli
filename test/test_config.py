import os
from FLIR.conservator.config import Config

TEST_DICT = {
    "CONSERVATOR_EMAIL": "test@example.com",
    "CONSERVATOR_API_KEY": "testAPIkey",
    "CONSERVATOR_URL": "https://myconservator.com",
}


def test_from_dict():
    c = Config.from_dict(TEST_DICT)

    assert c.email == "test@example.com"
    assert c.key == "testAPIkey"
    assert c.url == "https://myconservator.com"


def test_save_and_load_file():
    c1 = Config.from_dict(TEST_DICT)
    c1.save_to_file("/tmp/test.config")
    c2 = Config.from_file("/tmp/test.config")
    assert c1 == c2
    assert c2.email == "test@example.com"
    assert c2.key == "testAPIkey"
    assert c2.url == "https://myconservator.com"


def test_from_environ():
    os.environ.update(TEST_DICT)
    c = Config.from_environ()
    assert c.email == "test@example.com"
    assert c.key == "testAPIkey"
    assert c.url == "https://myconservator.com"


def test_default_url():
    c = Config.from_dict({
        "CONSERVATOR_EMAIL": "test@example.com",
        "CONSERVATOR_API_KEY": "testAPIkey",
    })

    assert c.email == "test@example.com"
    assert c.key == "testAPIkey"
    assert c.url == Config.attributes["url"].default
