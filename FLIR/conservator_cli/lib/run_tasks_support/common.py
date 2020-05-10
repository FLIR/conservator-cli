import argparse
import os
import subprocess
import sys

import blessed

t = blessed.Terminal()


def report_task(task):
    print(t.bold_white("[{}] {}".format(task.name, task.description)) + t.white(" ({})".format(task.task_type)))


def get_env_defaults():
    return {
        # TODO change to NTK OUTPUT ROOT
        "NNTC_TEST_OUTPUT_ROOT": ("Location to place results", "/mnt/data/external-cortex-data/nntc_nntc_results"),
    }


def parse_args():
    # Two kinds of args.
    # (1) Environment variable args. These will make their way into a 'setup_environment' task.
    # (2) Optional args. These will make their way into a 'define_config' task.

    # Add environment variables
    parser = argparse.ArgumentParser()
    env_defaults = get_env_defaults()
    for env_var, (description, default_value) in env_defaults.items():
        lower = "--{}".format(env_var.lower())
        if env_var in os.environ:
            default_value = os.environ[env_var]
        parser.add_argument(lower, lower, help=description, default=default_value)

    parser.add_argument("--config", help="Performance test configuration", required=True)

    # Divide up args into env_vars and config_vars
    env_vars = {}
    config_vars = {}
    args = parser.parse_args(sys.argv[1:])
    for arg, value in args.__dict__.items():
        upper = arg.upper()
        if upper in env_defaults:
            env_vars[upper] = value
            os.environ[upper] = value
        elif value is not None:
            config_vars[arg] = value

    return env_vars, config_vars


""" Adds a setup_environment task to the task list """


def add_define_environment_task(config, env_vars):
    print(t.bold_white("Auto-generate _setup-environment task"))
    config["tasks"].insert(0, {
        "name": "_setup-environment",
        "description": "Setup environment variables (auto-generated task)",
        "task_type": "setup_environment",
        "task_config": {
            "env": env_vars
        }
    })


""" Adds a define_config task to the task list """


def add_define_config_task(config, config_vars):
    print(t.bold_white("Auto-generate _command-line-arguments task"))
    config["tasks"].insert(0, {
        "name": "_command-line-arguments",
        "description": "Extract configuration variables from command-line (auto-generated task)",
        "task_type": "define_config",
        "task_config": {
            "config_out": config_vars
        }
    })
