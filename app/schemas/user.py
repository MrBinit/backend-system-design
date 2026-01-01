from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserResponse(BaseModel):
    email: EmailStr
    role: str
    created_at: datetime