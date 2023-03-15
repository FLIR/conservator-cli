# pylint: disable=missing-module-docstring
import logging
import os.path as osp
from collections.abc import Callable


def read_subfolder_config(
    args, default_config_path: str, config_filename: str, show_help: Callable, logger: logging.Logger=None
) -> str:
    """
    Parse config from input arguments. Otherwise call show_help(..)

    example:
     default_config_path = "configs/some_application"
     args.config         = "my_preset"
     config_filename     = "settings.json"
     return "configs/some_application/my_preset/settings.json"

    :param args:
    :param default_config_path:
    :param config_filename:
    :param show_help: [optional] callable function that shows help. Takes two arguments: (default_config_root_path, config_filename)
    :param logger: [optional] logger to use instead of print
    :return: full path to configuration file (if found)
    """
    default_config_root_path = osp.expandvars(default_config_path)
    if args.config is None:
        message = f'Please select a confing with --config=CONFIG_NAME. Parsing list of configs from: "{default_config_root_path}"'
        if logger is not None:
            logger.info(message)
        else:
            print(message)

        if show_help is not None:
            show_help(default_config_root_path, config_filename)

    config_path = osp.expandvars(args.config)

    if not osp.exists(config_path):
        # In this case config is just a filename rather than a complete path
        config_path = osp.join(default_config_root_path, args.config, config_filename)

        if not osp.exists(config_path):
            message = f'Could not find any configs input: "{args.config}"'
            if logger is not None:
                logger.error(message)
            else:
                print(message)

            if show_help is not None:
                show_help(default_config_root_path, config_filename)

    # At this point config is a full path, and it exists, so we can use it

    return config_path
