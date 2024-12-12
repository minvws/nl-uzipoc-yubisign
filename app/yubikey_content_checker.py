import PyKCS11

from app.yubikey_details import YubikeyDetails
from app.pkcs import pkcs as PKCSWrapper


class YubikeyContentChecker:
    HEADERS = [
        "X.509 Certificate",
        "Public key",
        "Private key",
        "PIV Attestation",
        "UZI Certificate",
    ]

    LABEL_MAPPING = {
        "PIV Authentication": " 9a",
        "Digital Signature": " 9c",
        "Key Management": "9d",
        "Card Authentication": " 9e",
    }
    _pkcs: PKCSWrapper

    def __init__(self, pkcs_wrapper: PKCSWrapper):
        self._pkcs = pkcs_wrapper

    def _find_contents(self, session: PyKCS11.Session):
        # This creates an dictionary of 4 items, with inside a dictionary of 3 items, all values to False
        finds = {x: {y: False for y in range(3)} for x in range(4)}

        cko_types_to_check = [
            PyKCS11.CKO_CERTIFICATE,
            PyKCS11.CKO_PUBLIC_KEY,
            PyKCS11.CKO_PRIVATE_KEY,
            PyKCS11.CKO_CERTIFICATE,
        ]
        for col, cko_type in enumerate(cko_types_to_check):
            all_objects = session.findObjects([(PyKCS11.CKA_CLASS, cko_type)])

            for row, (x, y) in enumerate(self.LABEL_MAPPING.items()):
                for obj in all_objects:
                    label = session.getAttributeValue(obj, [PyKCS11.CKA_LABEL])[0]
                    if label == self.HEADERS[col] + " for " + x and col < 3:
                        finds[col][row] = True
                        break
                    if label == "X.509 Certificate for PIV Attestation" + y and col == 3:
                        finds[col][row] = True
                        break

        return finds

    def check(self, yubikey: YubikeyDetails):
        session = self._pkcs.getsession(
            yubikey.slot,
        )
        finds = self._find_contents(session)

        self._pkcs.delsession(yubikey.slot)

        return any(value for inner_dict in finds.values() for value in inner_dict.values())
