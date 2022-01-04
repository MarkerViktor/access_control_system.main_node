from datetime import datetime as Datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    surname: str
    extra_info: Optional[str]


class UserFaceDescriptor(BaseModel):
    id: int
    features: list[float]
    user_id: int


class RoomVisitReport(BaseModel):
    id: int
    room_id: int
    user_id: int
    datetime: Datetime
