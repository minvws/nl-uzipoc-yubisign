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

    def _find_objects(self, session: PyKCS11.Session):
        # This creates an dictionary of 4 items, with inside a dictionary of 3 items, all values to False
        # {
        #     0: {0: False, 1: False, 2: False},
        #     1: {0: False, 1: False, 2: False},
        #     2: {0: False, 1: False, 2: False},
        #     3: {0: False, 1: False, 2: False},
        # }
        finds = {index: {row: False for row in range(3)} for index in range(4)}

        cko_types_to_check = [
            PyKCS11.CKO_CERTIFICATE,
            PyKCS11.CKO_PUBLIC_KEY,
            PyKCS11.CKO_PRIVATE_KEY,
            PyKCS11.CKO_CERTIFICATE,
        ]
        # Iterate through the cryptographic objects to check and save the index
        for index, cko_type in enumerate(cko_types_to_check):
            # Find the objects in the session matching the selected CKO type
            # https://pkcs11wrap.sourceforge.io/api/api.html#PyKCS11.Session.findObjects
            all_objects = session.findObjects(
                [(PyKCS11.CKA_CLASS, cko_type)],
            )

            # Loop through every mapping with each key and value and save the index
            for row, (label_key, label_value) in enumerate(self.LABEL_MAPPING.items()):
                for obj in all_objects:
                    # For each found object, retrieve the CKA_LABEL
                    label = session.getAttributeValue(obj, [PyKCS11.CKA_LABEL])[0]

                    if label == self.HEADERS[index] + " for " + label_key and index < 3:
                        finds[index][row] = True
                        break

                    if label == "X.509 Certificate for PIV Attestation" + label_value and index == 3:
                        finds[index][row] = True
                        break

        return finds

    def check(self, yubikey: YubikeyDetails):
        session = self._pkcs.getsession(
            yubikey.slot,
        )
        finds = self._find_objects(session)

        self._pkcs.delsession(yubikey.slot)

        # Check if any of the finds are true
        return any(value for inner_dict in finds.values() for value in inner_dict.values())
