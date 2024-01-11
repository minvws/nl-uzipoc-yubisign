from .acme import Acme


class ACME:
    nonce = None
    jwt_token = ""
    client = None
    status = None
    challengeurl = None
    challenges = [{}, {}, {}, {}]
    tokens = ["", "", "", ""]

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

    def order(self, keynum):
        order = {"identifiers": [{"type": "jwt", "value": "42-unused"}]}
        self.challengeurl = self.client.create_order(keynum, order)

    def getchallenge(self, num):
        challenges, self.status = self.client.challenge(self.challengeurl)
        challenge = challenges[0]
        print("Key challange", num)
        self.challenges[num] = challenge
        self.tokens[num] = challenge["token"]
        return challenge

    def gettoken(self):
        return self.jwt_token

    def send_request(self, hw_attest, uzi_jwt, num, f9cert):
        self.client.send_challenge_jwt(self.challenges[num], hw_attest, uzi_jwt, f9cert)

    def wait(self, num):
        self.status, _url = self.client.notify(self.challenges[num]["url"])

    def final(self, keynum, hw_csr):
        self.client.final(keynum, hw_csr)
        return self.client.getcert()
