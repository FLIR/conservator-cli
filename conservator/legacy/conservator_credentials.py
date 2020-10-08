"""
Conservator Credentials
=======================
Managing credentials used to connect to a Conservator instance.
"""


class ConservatorCredentials:
    """Defines credentials used to connect to a Conservator instance.

    There are a variety of methods for getting credentials.

    .. automethod:: get_from_environ

    ``get_from_config_file`` - Get credentials from the config file `.conservator_config.json`.
    `get_from_input` - Get credentials from stdin, with a prompt.

    By default, you should get an instance using `ConservatorCredentials.default()`.  This will go
    through the methods above and .
    """

    def __init__(self, email, token):
        """
        :meta: private
        """
        self.email = email
        self.token = token

    def get_email_for_url(self):
        return self.email.replace("@", "%40")

    def get_token_for_url(self):
        return (":" + self.token) if self.token else ""

    def get_url_format(self):
        return self.get_email_for_url() + self.get_token_for_url()

    @staticmethod
    def get_from_environ():
        """Get credentials from environment variables."""
        pass



