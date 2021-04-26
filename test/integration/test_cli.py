"""
This tests the *actual* CLI using subprocess

Tests must use the default_conservator fixture, which sets Config.default(),
as used by the CLI commands.
"""
import os
import subprocess
from time import sleep


def cli(*args):
    return subprocess.run(
        ["conservator", *map(str, args)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_whoami(default_conservator):
    user = default_conservator.get_user()

    p = cli("whoami")

    assert p.returncode == 0
    assert user.email in p.stdout.decode()
