#!/usr/bin/env python3
"""
Simple functions to run black, pytest, etc.
"""
import os
import subprocess
import click

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
COMMANDS = ["test", "black", "black:fix", "all"]


@click.group(help="Utility scripts for conservator-cli")
@click.pass_context
def cli(ctx):
    """
    Entrypoint function
    """
    ctx.ensure_object(dict)


@cli.command("test", help="Run conservator-cli unit tests")
def test() -> None:
    """
    Run unit tests only
    """
    test_result = subprocess.call(["pytest", os.path.join(BASE_DIR, "test", "unit")])
    if test_result == 0:
        click.secho("Unit tests passed", fg="green", bold=True)
    else:
        click.secho("Unit tests failed", fg="red", bold=True)
    return test_result


@cli.command("black", help="Run black check")
def black() -> None:
    """
    Run Black (check only)
    """
    black_result = subprocess.call(["black", "--check", BASE_DIR])
    if black_result == 0:
        click.secho("Black check passed", fg="green", bold=True)
    else:
        click.secho("Black check failed", fg="red", bold=True)
    return black_result


@cli.command("black:fix", help="Run black and fix any formatting issues")
def black_fix() -> None:
    """
    Run Black and fix any issues
    """
    black_fix_result = subprocess.call(["black", BASE_DIR])
    if black_fix_result == 0:
        click.secho("Black:fix succeeded", fg="green", bold=True)
    else:
        click.secho("Black:fix failed", fg="red", bold=True)
    return black_fix_result


@cli.command("all", help="Check formatting and run unit tests")
@click.pass_context
def run_all(ctx) -> None:
    """
    Run Black (check only) and unit tests
    """
    black_result = ctx.invoke(black)
    if black_result > 0:
        ctx.exit(black_result)
    test_result = ctx.invoke(test)
    if test_result > 0:
        ctx.exit(test_result)


if __name__ == "__main__":
    cli()
