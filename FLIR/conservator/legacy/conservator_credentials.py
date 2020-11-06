class ConservatorCredentials:
    def __init__(self, email, token):
        self.email = email
        self.token = token

    def get_email_for_url(self):
        return self.email.replace("@", "%40")

    def get_token_for_url(self):
        return (":" + self.token) if self.token else ""

    def get_url_format(self):
        return self.get_email_for_url() + self.get_token_for_url()
