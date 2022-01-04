from datetime import datetime

from pydantic import BaseModel


class VisitInfo(BaseModel):
    datetime: datetime
    user_id: int


class FaceDescriptor(BaseModel):
    features: list[float]


class TaskPerformingReport(BaseModel):
    task_id: int
    new_status: str


class DescriptorAdding(BaseModel):
    user_id: int
    descriptor: FaceDescriptor
