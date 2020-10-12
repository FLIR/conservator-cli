import os
from conservator import Config

TEST_DICT = {
    Config.EMAIL: "test@example.com",
    Config.API_KEY: "testAPIkey",
    Config.URL: "https://myconservator.com",
}


def test_from_dict():
    c = Config.from_dict(TEST_DICT)

    assert c.email == "test@example.com"
    assert c.key == "testAPIkey"
    assert c.key == "https://myconservator.com"


def test_save_and_load_file():
    c1 = Config.from_dict(TEST_DICT)
    c1.save_to_file("/tmp/test.config")
    c2 = Config.from_file("/tmp/test.config")
    assert c1 == c2
    assert c2.email == "test@example.com"
    assert c2.key == "testAPIkey"
    assert c2.key == "https://myconservator.com"


def test_from_environ():
    os.environ.update(TEST_DICT)
    c = Config.from_environ()
    assert c.email == "test@example.com"
    assert c.key == "testAPIkey"
    assert c.key == "https://myconservator.com"

