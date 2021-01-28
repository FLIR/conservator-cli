"""
A :class:`Config` object is required connect to Conservator. There are
a variety of ways to create an instance of config.

In general, use :func:`Config.default`.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


class ConfigAttribute:
    def __init__(self, internal_name, friendly_name, default=None, type_=str):
        self.internal_name = internal_name
        self.friendly_name = friendly_name
        self.default = default
        self.type_ = type_


class Config:
    """
    Contains a user's Email and API Key (token), to be used
    when authenticating operations on an instance of :class:`~FLIR.conservator.conservator.Conservator`
    at a certain URL.

    Attributes:
        - CONSERVATOR_API_KEY
        - CONSERVATOR_URL (default: https://flirconservator.com/)
        - CONSERVATOR_MAX_RETRIES (default: 5)
        - CONSERVATOR_CVC_CACHE_PATH (default: .cvc/cache)

    :param kwargs: A dictionary of (str: str) providing values for all of the Config attributes.
        Any attribute not in the dictionary, will use the default value. If no default value is defined,
        an error is raised.
    """

    attributes = {
        "key": ConfigAttribute("CONSERVATOR_API_KEY", "Conservator API Key"),
        "url": ConfigAttribute(
            "CONSERVATOR_URL", "Conservator URL", default="https://flirconservator.com/"
        ),
        "max_retries": ConfigAttribute(
            "CONSERVATOR_MAX_RETRIES", "Conservator Max Retries", default=5, type_=int
        ),
        "cvc_cache_path": ConfigAttribute(
            "CONSERVATOR_CVC_CACHE_PATH", "CVC Cache Path", default=".cvc/cache"
        ),
    }

    def __init__(self, **kwargs):
        for name, attr in Config.attributes.items():
            v = kwargs.get(attr.internal_name, None)
            if v is not None:
                v = attr.type_(v)
            if v is None:
                v = attr.default
            if v is None:
                raise ConfigError(f"Missing value for '{name}'")
            assert type(v) == attr.type_
            setattr(self, name, v)

    def save_to_file(self, path):
        """
        Saves the :class:`Config` to as JSON

        This file can be loaded using :func:`Config.from_file`.

        .. note:: For security, this file's mode will be set to ``0600``.

        :param path: The file path to save to.
        """
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)
        os.chmod(path, 0o600)

    def to_dict(self):
        return {
            attr.internal_name: getattr(self, name)
            for name, attr in self.attributes.items()
        }

    def save_to_default_config(self):
        """
        Saves the :class:`Config` to the Default config file, meaning
        this config will be loaded by :func:`Config.default`.
        """
        self.save_to_file(Config.default_config_path())

    @staticmethod
    def from_dict(data):
        return Config(**data)

    @staticmethod
    def from_file(path):
        """
        Creates a :class:`Config` object from a JSON config file.

        .. note:: For security, this file's mode will be set to ``0600``.

        :param path: The path to the JSON config file.
        """
        try:
            with open(path, "r") as config:
                data = json.load(config)
            os.chmod(path, 0o600)
            return Config.from_dict(data)
        except FileNotFoundError:
            return None

    @staticmethod
    def from_default_config_file():
        """
        Creates a :class:`Config` object from the JSON config file
        at the :func:`Config.default_config_path`.
        """
        return Config.from_file(Config.default_config_path())

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
        d = {}
        for name, attr in Config.attributes.items():
            if attr.default is None:
                v = input(f"{attr.friendly_name}: ")
            else:
                v = input(f"{attr.friendly_name} (leave empty for {attr.default}): ")
            v = v.strip()
            if len(v) == 0:
                v = None
            d[attr.internal_name] = v
        return Config.from_dict(d)

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

    @staticmethod
    def default_config_path():
        """
        By default, your config is saved in ``~/.conservator_config.json``.
        """
        return os.path.join(os.path.expanduser("~"), ".conservator_config.json")

    @staticmethod
    def delete_saved_default_config():
        """
        Delete the default saved config, if it exists.
        """
        path = Config.default_config_path()
        if os.path.exists(path):
            os.remove(path)

    def __repr__(self):
        return f"<Config for {self.url}>"

    def __eq__(self, other):
        return isinstance(other, Config) and all(
            getattr(other, name) == getattr(self, name)
            for name in Config.attributes.keys()
        )
