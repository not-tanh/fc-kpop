from dataclasses import dataclass
from datetime import datetime
from bson.objectid import ObjectId


@dataclass
class Debt:
    player_id: ObjectId
    date: datetime
    value: int
    desc: str
