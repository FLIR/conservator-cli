import os.path as osp
from collections.abc import Callable


def read_config(args, default_config_path: str, show_help: Callable) -> str:
    """
     Parse config from input arguments. Otherwise call show_help(..)

     example 1:
      default_config_path = "configs/some_application"
      args.config         = "my_config"
      return "configs/some_application/my_config.json"

    example 2:
      default_config_path = "configs/some_application"
      args.config         = "my_config.json"
      return "configs/some_application/my_config.json"

     :param args:
     :param default_config_path:
     :param show_help:
     :return: full path to configuration file (if found)
    """
    default_config_root_path = osp.expandvars(default_config_path)
    if args.config is None:
        print(
            f"ERROR: Config not provided... This is the default config path that was provided: {default_config_root_path}"
        )
        if show_help is not None:
            show_help(default_config_root_path)

    config_path = osp.expandvars(args.config)
    if not osp.exists(config_path):
        # In this case config is just a filename rather than a complete path
        config_path = osp.join(
            default_config_root_path, args.config
        )  # Try it as a filename

        if not osp.exists(config_path):
            config_path = osp.join(
                default_config_root_path, f"{args.config}.json"
            )  # Try to put a json extension

            if not osp.exists(config_path):
                print(f'ERROR: Could not find any configs input: "{args.config}"')
                if show_help is not None:
                    show_help(default_config_root_path)

    # At this point config is a full path and it exists so we can use it

    return config_path


def read_subfolder_config(
    args, default_config_path: str, config_filename: str, show_help: Callable
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
    :param show_help:
    :return: full path to configuration file (if found)
    """
    default_config_root_path = osp.expandvars(default_config_path)
    if args.config is None:
        print(
            f"ERROR: Config not provided... This is the default config path that was provided: {default_config_root_path}"
        )
        if show_help is not None:
            show_help(default_config_root_path, config_filename)

    config_path = osp.expandvars(args.config)

    if not osp.exists(config_path):
        # In this case config is just a filename rather than a complete path
        config_path = osp.join(default_config_root_path, args.config, config_filename)

        if not osp.exists(config_path):
            print('ERROR: Could not find any configs input: "{}"'.format(args.config))
            if show_help is not None:
                show_help(default_config_root_path, config_filename)

    # At this point config is a full path and it exists so we can use it

    return config_path
