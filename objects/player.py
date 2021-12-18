import enum
from dataclasses import dataclass
from typing import Union


class Positions(enum.Enum):
    Striker = 'Tiền đạo'
    Midfielder = 'Tiền vệ'
    Defender = 'Hậu vệ'
    Goalkeeper = 'Thủ môn'


@dataclass
class Player:
    name: str
    alias: str
    yob: int
    number: int
    position: Positions
    photo: Union[str, None]
