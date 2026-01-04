from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    interview_id: str
    sender_email: str
    sender_role: str
    content: str
    created_at: str


