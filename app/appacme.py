from .acme import Acme


class ACME:
    nonce = None
    jwt_token = ""
    client = None
    status = None
    challengeurl = None
    challenges = []

    def __init__(self, url):
        self.client = Acme(url)
        """
        Get the first nonce.
        """
        self.client.get_nonce()

        """
        Generate a key for the acme instance. This is a key used only for
        the acme session. No real requirements except not to leak it
        during (and after) the session.
        """
        self.client.gen_key()

        """
        Create an account. As per acme standard an email needs
        to be provided.
        """
        areq = {"termsOfServiceAgreed": True, "contacts": ["email@example.com"]}
        self.client.account_request(areq)

    def order(self):
        order = {"identifiers": [{"type": "jwt", "value": "42-unused"}]}
        self.challengeurl = self.client.create_order(order)

    def getchallenge(self):
        self.challenges, self.status = self.client.challenge(self.challengeurl)
        challenge = self.challenges[0]
        return challenge

    def gettoken(self):
        return self.jwt_token

    def send_request(self, hw_attest, uzi_jwt):
        self.client.send_challenge_jwt(self.challenges[0], hw_attest, uzi_jwt)

    def wait(self):
        self.status, _url = self.client.notify(self.challenges[0]["url"])

    def final(self, hw_csr):
        self.client.final(hw_csr)
        return self.client.getcert()
