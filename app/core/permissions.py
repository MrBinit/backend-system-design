# check whether the user role is allowed to access a route and blocks access if the role lacks permissions
from fastapi import Depends, HTTPException, status
from app.core.auth_dependencies import get_current_user

def require_roles(*allowed_roles: str):
    def checker(current_user=Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException (status_code= status.HTTP_403_FORBIDDEN,
                                 detail="Insufficient permissions")

        return current_user
    return checker