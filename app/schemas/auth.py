from pydantic import BaseModel, EmailStr, StringConstraints
from typing_extensions import Annotated

PasswordStr = Annotated[
    str,
    StringConstraints(min_length=8, max_length=72)
]

class RegisterRequest(BaseModel):
    email: EmailStr
    password: PasswordStr
    role: str  # admin/ interviewer / candidates

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


