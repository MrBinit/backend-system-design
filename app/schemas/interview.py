from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class InterviewCreate(BaseModel):
    title: str
    interview_type: str
    scheduled_at: Optional[datetime] = None


class InterviewOut(BaseModel):
    id: str
    title: str
    interview_type: str
    status: str
    scheduled_at: Optional[datetime] = None
    created_by: str
    created_at: datetime

class InterviewStatusUpdate(BaseModel):
    status: str
