from FLIR.conservator.config import Config

TEST_DICT = {
    "CONSERVATOR_API_KEY": "testAPIkey",
    "CONSERVATOR_URL": "https://myconservator.com",
    "CONSERVATOR_MAX_RETRIES": "2",
}


def test_from_dict():
    c = Config.from_dict(TEST_DICT)

    assert c.key == "testAPIkey"
    assert c.url == "https://myconservator.com"
    assert c.max_retries == 2


def test_save_and_load_file():
    c1 = Config.from_dict(TEST_DICT)
    c1.save_to_file("/tmp/test.config")
    c2 = Config.from_file("/tmp/test.config")
    assert c1 == c2
    assert c2.key == "testAPIkey"
    assert c2.url == "https://myconservator.com"
    assert c2.max_retries == 2


def test_defaults():
    c = Config.from_dict(
        {
            "CONSERVATOR_API_KEY": "testAPIkey",
        }
    )

    assert c.key == "testAPIkey"
    assert c.url == "https://flirconservator.com/"
    assert c.max_retries == 5

