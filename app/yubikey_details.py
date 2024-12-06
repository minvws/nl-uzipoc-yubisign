from dataclasses import dataclass


@dataclass
class YubikeyDetails:
    slot: str
    name: str
    serial: str
