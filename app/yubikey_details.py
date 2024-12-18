from dataclasses import dataclass


@dataclass
class YubikeyDetails:
    slot: str
    serial: str
    name: str
