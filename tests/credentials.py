import unittest
import os
from conservator import Credentials

class CredentialsTest(unittest.TestCase):
    TEST_DICT = {
        Credentials.EMAIL: "test@example.com",
        Credentials.API_KEY: "testAPIkey",
    }

    def test_from_dict(self):
        c = Credentials.from_dict(CredentialsTest.TEST_DICT)

        assert c.email == "test@example.com"
        assert c.key == "testAPIkey"

    def test_save_and_load_file(self):
        c1 = Credentials.from_dict(CredentialsTest.TEST_DICT)
        c1.save_to_file("/tmp/test.config")
        c2 = Credentials.from_file("/tmp/test.config")
        assert c1 == c2
        assert c2.email == "test@example.com"
        assert c2.key == "testAPIkey"

    def test_from_environ(self):
        os.environ.update(CredentialsTest.TEST_DICT)
        c = Credentials.from_environ()
        assert c.email == "test@example.com"
        assert c.key == "testAPIkey"


if __name__ == '__main__':
    unittest.main()
