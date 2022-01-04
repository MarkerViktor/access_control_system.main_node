from enum import Enum

from pydantic import BaseModel


class Task(BaseModel):
    id: int
    room_id: int
    manager_id: int
    body: str
    status: str


class Status(str, Enum):
    UNDONE = 'UNDONE'
    DONE = 'DONE'
    CANCELLED = 'CANCELLED'
    ERROR = 'ERROR'
