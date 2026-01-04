from pydantic import BaseModel, EmailStr
from datetime import datetime


class ParticipantCreate(BaseModel):
    user_email: EmailStr
    participant_role: str 


class ParticipantOut(BaseModel):
    interview_id: str
    user_email: EmailStr
    participant_role: str
    added_at: datetime
