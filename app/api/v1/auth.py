from fastapi import HTTPException, APIRouter, status
from app.schemas.auth import RegisterRequest, TokenResponse, LoginRequest
from app.db.mongo import db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.errors import api_error

router = APIRouter(prefix="/v1/auth", tags= ["auth"])

@router.post("/register", status_code= status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    if db.user.find_one({"email": payload.email}):
        api_error(
            status_code=401,
            code="AUTH_INVALID_CREDENTIALS",
            message="Invalid credentials"
        )

    user = User(
        email = payload.email,
        hashed_password=hash_password(payload.password),
        role = payload.role
    )

    db.users.insert_one(user.to_dict())
    return {"message": "User registered successfully"}

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = db.users.find_one({"email": payload.email})
    if not user:
        print("USER NOT FOUND")
        api_error(
            status_code=401,
            code="AUTH_INVALID_CREDENTIALS",
            message="Invalid credentials"
        )
    result = verify_password(payload.password, user["hashed_password"])
    if not result:
        api_error(
            status_code=401,
            code="AUTH_INVALID_CREDENTIALS",
            message="Invalid credentials"
        )
    token = create_access_token({
        "sub": user["email"],
        "role": user["role"],
    })
    return {"access_token": token}
