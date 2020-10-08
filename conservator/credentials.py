import os
import json

"""
Credentials allow you to connect to Conservator. There are a variety of
ways to create an instance of Credentials:
 - Standard input
 - Environment variables
 - Config File
 - Manually using constructor
"""


class Credentials:
    """
    Contains a user's Email and API Key (token), to be used
    when authenticating operations on an instance of :class:`Conservator`.

    :param email: The user's email.
    :param key: The user's API key or token.
    """
    EMAIL = "CONSERVATOR_EMAIL"
    API_KEY = "CONSERVATOR_API_KEY"

    def __init__(self, email, key):
        self.email = email
        self.key = key

    def save_to_file(self, path):
        data = {
            Credentials.EMAIL: self.email,
            Credentials.API_KEY: self.key,
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def save_to_default_config(self):
        self.save_to_file(Credentials.default_config_path())

    @staticmethod
    def from_dict(data):
        email = data.get(Credentials.EMAIL, None)
        key = data.get(Credentials.API_KEY, None)
        if email is None or key is None:
            return None
        return Credentials(email, key)

    @staticmethod
    def from_file(path):
        """
        Creates a :class:`Credentials` object from a JSON config file.

        :param path: The path to the JSON config file.
        """
        try:
            with open(path, 'r') as config:
                data = json.load(config)
            return Credentials.from_dict(data)
        except FileNotFoundError:
            return None

    @staticmethod
    def from_config():
        """
        Creates a :class:`Credentials` object from the JSON config file
        at the `default_config_path`.
        """
        return Credentials.from_file(Credentials.default_config_path())

    @staticmethod
    def from_environ():
        """
        Creates a :class:`Credentials` object from environment variables.
        """
        return Credentials.from_dict(os.environ)

    @staticmethod
    def from_input():
        """
        Creates a :class:`Credentials` object from standard input.
        """
        email = input("Conservator Email: ")
        key = input("Conservator API key: ")
        return Credentials(email, key)

    @staticmethod
    def default(save=True):
        """
        Gets the default credentials.

        This works by iterating through the various credential sources, and returning
        the first one that works. Sources are queried in this order:
         - Config file
         - Environment variables
         - User input

        :param save: If `True`, save the credentials for future use. This means a user
            won't need to type them again.
        """
        for source in [Credentials.from_config, Credentials.from_environ, Credentials.from_input]:
            creds = source()
            if creds is not None:
                if save and source != Credentials.from_config:
                    creds.save_to_default_config()
                return creds
        return None

    @staticmethod
    def default_config_path():
        """
        By default, your credentials are saved in ``~/.conservator_config.json``.
        """
        return os.path.join(os.path.expanduser("~"), ".conservator_config.json")

    @staticmethod
    def delete_saved_default_config():
        """
        Deletes default saved credentials, if they exist.
        """
        path = Credentials.default_config_path()
        if os.path.exists(path):
            os.remove(path)

    def __repr__(self):
        return f"<Credentials for {self.email}>"

    def __eq__(self, other):
        return isinstance(other, Credentials) \
               and other.email == self.email \
               and other.key == self.key
