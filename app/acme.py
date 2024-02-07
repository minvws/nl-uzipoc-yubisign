import json
import pprint
from base64 import urlsafe_b64encode
import requests
from jwcrypto import jwk, jwt


class Acme:
    url = None
    key = None
    nonce = None
    kid = None
    order = None
    certurl = None
    finalize = {}

    def __init__(self, url):
        self.url = url

    def debugrequest(self, protected, payload):
        print("  protected")
        self.pprint(protected)
        print("  payload")
        self.pprint(payload)

    def debugresponse(self, response):
        print("- " * 40)
        print("  headers")
        self.pprint(self.clean_headers(response.headers))
        print("  response")
        self.pprint(response.json())
        print("=" * 80)

    def gen_key(self):
        """
        This does only generate a P-256 key for use with JWT.
        This key is only used during the session to request a certificate from ACME.
        """
        self.key = jwk.JWK.generate(
            kty="EC", crv="P-256", key_ops=["verify", "sign"], alg="ES256"
        )

    def get_nonce(self):
        """
        The acme protocol specifies a nonce to be used during communication
        to prevent replay attacks. This is the first, a complete fresh one,
        without having to use the previous nonce. This is stored in self.nonce
        as with all updates, as every request answers with a new nonce.
        """
        response = requests.get(self.url + "acme/new-nonce", timeout=60)
        self.nonce = response.headers["Replay-Nonce"]

    def account_request(self, request):
        """
        This is to request an account. The acme headers are pretty simple.
        kid is the key registered but since this is the first request
        you specify the jwk and it get's registered as the keyid.
        add the nonce (see above), url and alg and tada.wav.
        """
        print("Account Request")
        protected = {
            "alg": "ES256",
            "nonce": self.nonce,
            "url": self.url + "acme/new-acct",
            "jwk": self.key.export_public(True),
        }
        token = jwt.JWS(payload=json.dumps(request))
        token.add_signature(self.key, alg="ES256", protected=protected)
        self.debugrequest(protected, request)
        headers = {"Content-Type": "application/jose+json"}
        response = requests.post(
            self.url + "acme/new-acct",
            data=token.serialize(),
            headers=headers,
            timeout=60,
        )
        self.debugresponse(response)
        self.nonce = response.headers["Replay-Nonce"]
        self.kid = response.headers["Location"]
        assert response.json()["status"] == "valid"

    def create_order(self, keynum, order):
        """
        To let acme know you want a certificate first you have to
        create an order inside the system. All other stuff hangs on
        this order. This order gets a number and that gets encoded
        into the most URL's. Just call the right URL which is specified
        afterwards.
        """
        print("Order")
        protected = {
            "alg": "ES256",
            "nonce": self.nonce,
            "url": self.url + "acme/new-order",
            "kid": self.kid,
        }
        self.debugrequest(protected, order)
        token = jwt.JWS(payload=json.dumps(order))
        token.add_signature(self.key, alg="ES256", protected=protected)
        headers = {"Content-Type": "application/jose+json"}
        response = requests.post(
            self.url + "acme/new-order",
            data=token.serialize(),
            headers=headers,
            timeout=60,
        )
        self.debugresponse(response)
        self.nonce = response.headers["Replay-Nonce"]
        self.order = response.headers["Location"]
        self.finalize[keynum] = response.json()["finalize"]
        assert response.json()["status"] == "pending"
        return response.json()["authorizations"][0]

    def challenge(self, challengeurl):
        """
        ACME works with challenges. Normally you put them on a webserver
        or in DNS for example. We just request it and it should come back
        into the CSR as password. For now, just request it.  #FIXME
        """
        print("Challenge")
        print(f"  challengeurl: {challengeurl}")
        protected = {
            "alg": "ES256",
            "nonce": self.nonce,
            "url": challengeurl,
            "kid": self.kid,
        }
        print("  protected")
        self.pprint(protected)
        print("  payload")
        self.pprint("")
        token = jwt.JWS(payload="")
        token.add_signature(self.key, alg="ES256", protected=protected)
        headers = {"Content-Type": "application/jose+json"}
        response = requests.post(
            challengeurl, data=token.serialize(), headers=headers, timeout=60
        )
        self.debugresponse(response)
        self.nonce = response.headers["Replay-Nonce"]
        assert response.json()["status"] in ["pending", "valid"]
        return response.json()["challenges"], response.json()["status"]

    def send_challenge_jwt(self, challenge, hw_attestation, uzi_jwt, f9_cert):
        """
        We have a challenge, and a JWT to prove who we are.
        This JWT is from the central identification services for UZI.
        send the JWT to a jwt-v3 verify URL together with the challenge
        token and continue
        """
        print("Answer with JWT Challenge")
        challengeurl = challenge["url"]
        protected = {
            "alg": "ES256",
            "nonce": self.nonce,
            "url": challengeurl,
            "kid": self.kid,
        }
        payload = {}
        self.debugrequest(protected, payload)
        token = jwt.JWS(payload=json.dumps(payload))
        token.add_signature(self.key, alg="ES256", protected=protected)
        headers = {
            "Content-Type": "application/jose+json",
            "X-Acme-Jwt": uzi_jwt,
            "X-Acme-Cert": hw_attestation,
            "X-Acme-F9Cert": f9_cert,
        }
        print("  headers")
        print(headers)
        response = requests.post(
            challengeurl, data=token.serialize(), headers=headers, timeout=60
        )
        self.nonce = response.headers["Replay-Nonce"]
        self.debugresponse(response)

    def notify(self, notifyurl):
        """
        After sending the challenge and prove who we are it's within the protocol
        to update ACME that we provided the challenge. With HTTP/DNS Acme will do
        the lookup, with JWT it will do the lookup but internally
        """
        print("Notify")
        print(f"  notifyurl: {notifyurl}")
        protected = {
            "alg": "ES256",
            "nonce": self.nonce,
            "url": notifyurl,
            "kid": self.kid,
        }
        self.debugrequest(protected, {})
        token = jwt.JWS(payload=json.dumps({}))
        token.add_signature(self.key, alg="ES256", protected=protected)
        headers = {"Content-Type": "application/jose+json"}
        response = requests.post(
            notifyurl, data=token.serialize(), headers=headers, timeout=60
        )
        self.nonce = response.headers["Replay-Nonce"]
        self.debugresponse(response)
        assert response.json()["status"] in ["pending", "valid"]
        return response.json()["status"], response.json()["url"]

    def final(self, keynum, csr):
        """
        There is an order, we are correct. Now we get to request a certificate.
        To do this we provide a CSR and that gets signed with the root/sub-CA
        at the ACME service.
        """
        print("Request the Certificate")
        protected = {
            "alg": "ES256",
            "nonce": self.nonce,
            "url": self.finalize[keynum],
            "kid": self.kid,
        }
        payload = {
            #    "csr": b64encode(csr).decode().replace('+','-').replace('/','_'),
            "csr": urlsafe_b64encode(csr)
            .decode()
            .rstrip("="),
        }
        self.debugrequest(protected, payload)
        token = jwt.JWS(payload=json.dumps(payload))
        token.add_signature(self.key, alg="ES256", protected=protected)
        headers = {"Content-Type": "application/jose+json"}
        response = requests.post(
            self.finalize[keynum], data=token.serialize(), headers=headers, timeout=60
        )
        self.nonce = response.headers["Replay-Nonce"]
        self.debugresponse(response)
        assert response.json()["status"] == "valid"
        self.certurl = response.json()["certificate"]

    def getcert(self):
        """
        We got a URL where to download the cert.
        Let's do that.
        """
        print("Get Certificate")
        protected = {
            "alg": "ES256",
            "nonce": self.nonce,
            "url": self.certurl,
            "kid": self.kid,
        }
        self.debugrequest(protected, {})
        token = jwt.JWS(payload="")
        token.add_signature(self.key, alg="ES256", protected=protected)
        headers = {"Content-Type": "application/jose+json"}
        response = requests.post(
            self.certurl, data=token.serialize(), headers=headers, timeout=60
        )
        self.nonce = response.headers["Replay-Nonce"]
        self.debugresponse(response)
        return response.text

    def clean_headers(self, headers):
        """
        We are not a webbrowser, but a demo program. This deletes all
        the non-specific headers we don't want to print.
        """
        headers = dict(headers)
        for todel in [
            "Access-Control-Allow-Origin",
            "Access-Control-Expose-Headers",
            "Boulder-Requester",
            "Cache-Control",
            "Connection",
            "Content-Length",
            "Content-Security-Policy",
            "Content-Type",
            "Date",
            "Expect-CT",
            "Feature-Policy",
            "Keep-Alive",
            "Permissions-Policy",
            "Pragma",
            "Referrer-Policy",
            "Server",
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "X-Dns-Prefetch-Control",
            "X-Download-Options",
            "X-Frame-Options",
            "X-Permitted-Cross-Domain-Policies",
            "X-Xss-Protection",
        ]:
            if todel in headers:
                del headers[todel]
        return headers

    def pprint(self, data):
        """
        A simple hack to learn pprint to add some spaces upfront. Better for viewing
        """
        print(
            "\n".join(["    " + x for x in pprint.pformat(data, width=80).splitlines()])
        )
