import PyKCS11

from app.yubikey_details import YubikeyDetails


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

    def check(self, yubikey: YubikeyDetails):
        finds = {x: {y: False for y in range(3)} for x in range(4)}

        selected_slot = yubikey.slot
        session = self.pkcs.getsession(selected_slot)
        for col, cko_type in enumerate(
            [
                PyKCS11.CKO_CERTIFICATE,
                PyKCS11.CKO_PUBLIC_KEY,
                PyKCS11.CKO_PRIVATE_KEY,
                PyKCS11.CKO_CERTIFICATE,
            ]
        ):
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

        self.pkcs.delsession(selected_slot)
        print(finds)
        return any(value for inner_dict in finds.values() for value in inner_dict.values())
