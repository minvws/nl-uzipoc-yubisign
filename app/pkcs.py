from base64 import b64encode

from asn1crypto.x509 import Certificate, Name
from asn1crypto.keys import RSAPublicKey
from asn1crypto.csr import CertificationRequest, CertificationRequestInfo


from asn1crypto.core import Any, Sequence, ObjectIdentifier, Null
from asn1crypto.algos import SignedDigestAlgorithm
from asn1crypto import pem

import PyKCS11


class AlgorithmIdentifier(Sequence):
    _fields = [
        ("algorithm", ObjectIdentifier),
        ("parameters", Any, {"optional": False}),
    ]


class pkcs:
    sessions = {}
    attest = None
    attests = {}
    keys = {1: 1, 2: 2, 3: 3, 4: 4}

    pkcs11: PyKCS11.PyKCS11Lib
    _yubikey_pin: str

    def __init__(self, pykcs11lib: PyKCS11.PyKCS11Lib, yubikey_pin: str):
        self.pkcs11 = pykcs11lib
        self._yubikey_pin = yubikey_pin

    def getusersession(self, slot):
        print("User Open", slot)
        if slot not in self.sessions:
            self.sessions[slot] = self.pkcs11.openSession(slot)
            self.sessions[slot].login(self._yubikey_pin)
        return self.sessions[slot]

    def getsession(self, slot):
        print("Open", slot)
        if slot not in self.sessions:
            # self.sessions[slot] = self.pkcs11.openSession(slot)
            # self.sessions[slot].login("123456")
            self.sessions[slot] = self.pkcs11.openSession(slot, PyKCS11.CKF_RW_SESSION)
            self.sessions[slot].login(
                "010203040506070801020304050607080102030405060708",
                user_type=PyKCS11.CKU_SO,
            )
        return self.sessions[slot]

    def getadminsession(self, slot):
        print("Open", slot)
        if slot not in self.sessions:
            self.sessions[slot] = self.pkcs11.openSession(slot, PyKCS11.CKF_RW_SESSION)
            self.sessions[slot].login(
                "010203040506070801020304050607080102030405060708",
                user_type=PyKCS11.CKU_SO,
            )
        return self.sessions[slot]

    def delsession(self, slot):
        print("Close", slot)
        if slot not in self.sessions:
            return
        self.sessions[slot].closeSession()
        del self.sessions[slot]

    def listattest(self, slot):
        session = self.getsession(slot)
        all_objects = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE)])
        for obj in all_objects:
            label = session.getAttributeValue(obj, [PyKCS11.CKA_LABEL])[0]
            value = session.getAttributeValue(obj, [PyKCS11.CKA_VALUE])[0]
            if label.startswith("X.509 Certificate for PIV Attestation"):
                if label.endswith("X.509 Certificate for PIV Attestation"):
                    self.attest = b64encode(bytes(value))
                else:
                    slot = label.split(" ")[5]
                    self.attests[slot] = b64encode(bytes(value))
        self.delsession(slot)

    def getattest(self, slot, num):
        labels = {
            1: "X.509 Certificate for PIV Attestation 9a",
            2: "X.509 Certificate for PIV Attestation 9c",
            3: "X.509 Certificate for PIV Attestation 9d",
            4: "X.509 Certificate for PIV Attestation 9e",
        }
        session = self.getsession(slot)
        attestcrt = session.findObjects(
            [
                (PyKCS11.CKA_CERTIFICATE_TYPE, PyKCS11.CKC_X_509),
                (PyKCS11.CKA_LABEL, labels[num]),
            ]
        )
        if not attestcrt:
            return None
        crt = session.getAttributeValue(attestcrt[0], [PyKCS11.CKA_VALUE])[0]
        b64crt = b64encode(bytes(crt))
        self.delsession(slot)
        return b64crt

    def listprivatekeys(self, slot):
        session = self.getsession(slot)
        all_objects = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY)])
        print(all_objects)
        self.delsession(slot)

    def getf9(self, slot):
        session = self.getsession(slot)
        attestcrt = session.findObjects(
            [
                (PyKCS11.CKA_CERTIFICATE_TYPE, PyKCS11.CKC_X_509),
                (PyKCS11.CKA_LABEL, "X.509 Certificate for PIV Attestation"),
            ]
        )
        if not attestcrt:
            return None
        crt = session.getAttributeValue(attestcrt[0], [PyKCS11.CKA_VALUE])[0]
        b64crt = b64encode(bytes(crt))
        self.delsession(slot)
        return b64crt

    def makecsr(self, session, private_key, public_key):
        from asn1crypto import csr as csr_module, x509

        san = x509.GeneralNames(
            [
                x509.GeneralName("dns_name", "example.com"),
                x509.GeneralName("dns_name", "www.example.com"),
            ]
        )
        extensions = [
            csr_module.CRIAttribute(
                {
                    "type": "extension_request",
                    "values": [
                        x509.Extensions(
                            [
                                x509.Extension(
                                    {
                                        "extn_id": "subject_alt_name",
                                        "critical": False,
                                        "extn_value": san,
                                    }
                                )
                            ]
                        )
                    ],
                }
            )
        ]
        info = CertificationRequestInfo(
            {
                "version": 0,
                "subject": Name.build(
                    {
                        "common_name": "Mieke Medewerker",
                        "given_name": "Mieke",
                        "surname": "Medewerker",
                        "serial_number": "1337",
                        "country_name": "NL",
                        "organization_name": "CIBG",
                    }
                ),
                "subject_pk_info": {
                    "algorithm": {
                        "algorithm": "rsa",
                        "parameters": Null,
                    },
                    "public_key": RSAPublicKey(
                        {
                            "modulus": int.from_bytes(session.getAttributeValue(public_key, [PyKCS11.CKA_MODULUS])[0]),
                            "public_exponent": int.from_bytes(
                                session.getAttributeValue(public_key, [PyKCS11.CKA_PUBLIC_EXPONENT])[0]
                            ),
                        }
                    ),
                },
                "attributes": extensions,
            }
        )
        value = session.sign(
            private_key,
            info.dump(),
            mecha=PyKCS11.Mechanism(PyKCS11.CKM_SHA256_RSA_PKCS),
        )
        csr = CertificationRequest(
            {
                "certification_request_info": info,
                "signature_algorithm": SignedDigestAlgorithm(
                    {
                        "algorithm": "1.2.840.113549.1.1.11",
                        "parameters": Null,
                    }
                ),
                "signature": bytes(value),
            }
        )
        return csr.dump()

    def getcsr(self, slot, keyid):
        csr = None
        session = self.getusersession(slot)
        privkey = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY), (PyKCS11.CKA_ID, [keyid])])
        pubkey = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PUBLIC_KEY), (PyKCS11.CKA_ID, [keyid])])
        if privkey and pubkey:
            privkey = privkey[0]
            pubkey = pubkey[0]
            csr = self.makecsr(session, privkey, pubkey)
            print(csr)
        else:
            print(privkey, pubkey)
        self.delsession(slot)
        return csr

    def savecert(self, slot, keyid, pemcerts):
        usercert, _rootcert = pemcerts.split("\n-----BEGIN CERTIFICATE-----\n")
        cert = pem.unarmor(usercert.encode())[2]
        x509 = Certificate.load(cert)
        subject = x509.subject
        issuer = x509.issuer
        serial = x509["tbs_certificate"]["serial_number"]

        cert_template = [
            (PyKCS11.CKA_CERTIFICATE_TYPE, PyKCS11.CKC_X_509),
            (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
            (PyKCS11.CKA_ID, (self.keys[keyid],)),
            (PyKCS11.CKA_ISSUER, issuer.dump()),
            (PyKCS11.CKA_SERIAL_NUMBER, serial.dump()),
            (PyKCS11.CKA_SUBJECT, subject.dump()),
            (PyKCS11.CKA_VALUE, x509.dump()),
        ]
        session = self.getsession(slot)
        session.createObject(cert_template)
        self.delsession(slot)
