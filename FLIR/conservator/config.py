"""
A :class:`Config` object is required connect to Conservator. There are
a variety of ways to create an instance of config.

In general, use :func:`Config.default`.
"""

import os
import json
import logging
from collections import OrderedDict

import requests
from FLIR.conservator.connection import ConservatorConnection

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


class ConfigAttribute:
    def __init__(
        self, internal_name, friendly_name, default=None, type_=str, validator=None
    ):
        self.internal_name = internal_name
        self.friendly_name = friendly_name
        self.default = default
        self.type_ = type_
        self.validator = validator


"""
validators for config fields

input argument 'd' is dict of config data containing the field of interest
"""


def validate_max_retries(d):
    retries_ok = False
    try:
        max_retries = int(d["CONSERVATOR_MAX_RETRIES"])
        if max_retries > 0:
            retries_ok = True
        else:
            print("Error: invalid retries count, please try again")
    except Exception:
        print("Error: invalid retries count, please try again")
    return retries_ok


def validate_cache_path(d):
    cache_path = d["CONSERVATOR_CVC_CACHE_PATH"]
    dir_ok = False
    try:
        os.makedirs(cache_path, exist_ok=True)
        os.chmod(cache_path, 0o755)
        dir_ok = True
    except Exception:
        print("Error: invalid cache path, please try again")
    return dir_ok


def validate_url(d):
    url_ok = False
    try:
        # does url have graphql endpoint?
        check_url = ConservatorConnection.to_graphql_url(d["CONSERVATOR_URL"])
        r = requests.head(check_url)
        if r.status_code == 405:
            url_ok = True
    except Exception:
        pass

    if not url_ok:
        print("Error: invalid url, please try again")
    return url_ok


def validate_key(d):
    key_ok = False

    # check whether this is a valid config
    config = Config.from_dict(d)

    # is API key accepted by server?
    connection = ConservatorConnection(config)
    try:
        connection.get_email()
        key_ok = True
    except Exception:
        print("Error: invalid API Key, please try again")
    return key_ok


class Config:
    """
    Contains a user's API Key (token) and other settings, to be used when authenticating
    operations on an instance of :class:`~FLIR.conservator.conservator.Conservator`
    at a certain URL.

    Config attribute names (environment variables, dictionary keys):
     - ``CONSERVATOR_API_KEY``
     - ``CONSERVATOR_URL`` (default: https://flirconservator.com/)
     - ``CONSERVATOR_MAX_RETRIES`` (default: 5)
     - ``CONSERVATOR_CVC_CACHE_PATH`` (default: .cvc/cache)

    :param kwargs: A dictionary of (`str`: `str`) providing values for all of the Config attributes.
        Any attribute not in the dictionary, will use the default value. If no default value is defined,
        an error is raised.
    """

    DEFAULT_NAME = "default"
    ATTRIBUTES = OrderedDict(
        {
            "max_retries": ConfigAttribute(
                "CONSERVATOR_MAX_RETRIES",
                "Conservator Max Retries",
                default=5,
                type_=int,
                validator=validate_max_retries,
            ),
            "cvc_cache_path": ConfigAttribute(
                "CONSERVATOR_CVC_CACHE_PATH",
                "CVC Cache Path",
                default=os.path.join(".cvc", "cache"),
                validator=validate_cache_path,
            ),
            "url": ConfigAttribute(
                "CONSERVATOR_URL",
                "Conservator URL",
                default="https://flirconservator.com/",
                validator=validate_url,
            ),
            # from_input() needs 'key' to come after 'url'
            "key": ConfigAttribute(
                "CONSERVATOR_API_KEY", "Conservator API Key", validator=validate_key
            ),
        }
    )

    def __init__(self, **kwargs):
        for name, attr in Config.ATTRIBUTES.items():
            v = kwargs.get(attr.internal_name, None)
            if v is not None:
                v = attr.type_(v)
            if v is None:
                v = attr.default
            if v is None:
                raise ConfigError(f"Missing value for '{name}'")
            assert type(v) == attr.type_
            setattr(self, name, v)

    @staticmethod
    def from_dict(data):
        return Config(**data)

    @staticmethod
    def from_environ():
        """
        Creates a :class:`Config` object from environment variables.
        """
        return Config.from_dict(os.environ)

    @staticmethod
    def from_input():
        """
        Creates a :class:`Config` object from standard input.
        """

        # just show prompts, not errors from functions used to validate config
        logging.disable(logging.CRITICAL)

        d = {}
        for name, attr in Config.ATTRIBUTES.items():
            # loop until user supplies a config that actually works
            while True:
                if attr.default is None:
                    v = input(f"{attr.friendly_name}: ")
                else:
                    v = input(
                        f"{attr.friendly_name} (leave empty for {attr.default}): "
                    )
                v = v.strip()
                if len(v) == 0:
                    v = attr.default
                d[attr.internal_name] = v
                # move on to next field if validator passes
                if attr.validator(d):
                    break

        # restore logging level to normal
        logging.disable(logging.NOTSET)

        return Config.from_dict(d)

    @staticmethod
    def from_file(path):
        """
        Creates a :class:`Config` object from a JSON config file.

        .. note:: For security, this file's mode will be set to ``600``.

        :param path: The path to the JSON config file.
        """
        try:
            with open(path, "r") as config:
                data = json.load(config)
            if os.stat(path).st_mode & 0o777 != 0o600:
                logger.warning("Changing config file mode to 0600.")
                os.chmod(path, 0o600)
            return Config.from_dict(data)
        except FileNotFoundError:
            return None

    @classmethod
    def from_named_config_file(cls, name):
        return Config.from_file(Config.named_config_path(name))

    @staticmethod
    def from_name(name):
        return Config.from_named_config_file(name)

    @staticmethod
    def from_default_config_file():
        """
        Creates a :class:`Config` object from the JSON config file
        at the :func:`Config.default_config_path`.
        """
        # for previous installs that loaded the config to a different location:
        # eventually this check and warning can be removed.
        old_path = os.path.join(os.path.expanduser("~"), ".conservator_config.json")
        new_path = Config.default_config_path()
        if os.path.exists(old_path) and not os.path.exists(new_path):
            logger.warning(
                "Config files are now stored under ~/.config/conservator-cli, moving yours."
            )
            Config.from_file(old_path).save_to_default_config()
            os.remove(old_path)

        return Config.from_file(Config.default_config_path())

    def save_to_file(self, path):
        """
        Saves the :class:`Config` to as JSON

        This file can be loaded using :func:`Config.from_file`.

        .. note:: For security, this file's mode will be set to ``600``.

        :param path: The file path to save to.
        """
        directory = os.path.split(path)[0]
        os.makedirs(directory, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)
        if os.stat(path).st_mode & 0o777 != 0o600:
            logger.warning("Changing config file mode to 600.")
            os.chmod(path, 0o600)

    def to_dict(self):
        return {
            attr.internal_name: getattr(self, name)
            for name, attr in self.ATTRIBUTES.items()
        }

    def save_to_named_config(self, name):
        """
        Saves the :class:`Config` to the named config file, meaning
        this config can be loaded by :func:`Config.from_name`.
        """
        self.save_to_file(Config.named_config_path(name))

    def save_to_default_config(self):
        """
        Saves the :class:`Config` to the Default config file, meaning
        this config will be loaded by :func:`Config.default`.
        """
        self.save_to_file(Config.default_config_path())

    @staticmethod
    def named_config_path(name):
        """
        Configs are saved in ``~/.config/conservator-cli/`` as ``name.json``.
        """
        assert os.path.sep not in name
        return os.path.join(
            os.path.expanduser("~"), ".config", "conservator-cli", f"{name}.json"
        )

    @staticmethod
    def default_config_path():
        """
        The default config is saved in ``~/.config/conservator-cli/default.json``.
        """
        return Config.named_config_path(Config.DEFAULT_NAME)

    @staticmethod
    def saved_config_names():
        root_path = os.path.join(os.path.expanduser("~"), ".config", "conservator-cli")
        files = os.listdir(root_path)
        return [file[: -len(".json")] for file in files]

    @staticmethod
    def delete_saved_default_config():
        """
        Delete the default saved config, if it exists.
        """
        Config.delete_saved_named_config(Config.DEFAULT_NAME)

    @staticmethod
    def delete_saved_named_config(name):
        """
        Delete the config named `name`, if it exists.
        """
        path = Config.named_config_path(name)
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def default(save=True):
        """
        Gets the default config.
        This works by iterating through the various credential sources, and returning
        the first one that works. Sources are queried in this order:

         - Environment variables
         - Config file
         - User input

        :param save: If `True` and the source is stdin, save the config for future use.
            This means a user won't need to type them again.
        """
        for source in [
            Config.from_environ,
            Config.from_default_config_file,
            Config.from_input,
        ]:
            creds = None
            try:
                creds = source()
            except Exception:
                pass
            if creds is not None:
                logger.debug(f"Created config from source: {source}")
                if save and source == Config.from_input:
                    creds.save_to_default_config()
                return creds
        raise ConfigError("Couldn't find or create a config")

    def __str__(self):
        return f"""Config for {self.url}:""" + "".join(
            f"\n  {attribute.friendly_name}: {getattr(self, key)}"
            for key, attribute in Config.ATTRIBUTES.items()
        )

    def __repr__(self):
        return f"<Config for {self.url}>"

    def __eq__(self, other):
        return isinstance(other, Config) and all(
            getattr(other, name) == getattr(self, name)
            for name in Config.ATTRIBUTES.keys()
        )
