# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
"""
This tests the *actual* CLI using subprocess

Tests must use the default_conservator fixture, which sets Config.default(),
as used by the CLI commands.
"""
import subprocess


def cli(*args):
    return subprocess.run(
        ["conservator", *map(str, args)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def test_whoami(default_conservator):
    user = default_conservator.get_user()

    cli_response = cli("whoami")

    assert cli_response.returncode == 0
    assert user.email in cli_response.stdout.decode()
