from fastapi import APIRouter, Depends
from app.core.auth_dependencies import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/v1/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return {
        "email": current_user["email"],
        "role": current_user["role"],
        "created_at": current_user["created_at"],
    }
