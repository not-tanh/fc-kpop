from dataclasses import dataclass
from datetime import datetime
from bson.objectid import ObjectId


@dataclass
class Match:
    date: datetime
    time: str
    opponent: str
    stadium: str
    uniform: str
    scored: int
    conceded: int
    score_list: list[ObjectId]
    assist_list: list[ObjectId]
    cost: int = 0
    player_num: int = 0
