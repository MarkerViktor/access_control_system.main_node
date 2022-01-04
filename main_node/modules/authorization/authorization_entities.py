from datetime import datetime

from pydantic import BaseModel


class RoomLoginToken(BaseModel):
    token: str
    room_id: int


class RoomTempToken(BaseModel):
    token: str
    room_id: int
    valid_before: datetime


class AdminToken(BaseModel):
    token: str
    admin_id: int
