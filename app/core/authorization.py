from fastapi import HTTPException, status
from app.db.mongo import db


def require_interview_access(
    interview_id: str,
    user_email: str,
    user_role: str
):
    # admin bypass
    if user_role == "admin":
        return

    participant = db.participants.find_one({
        "interview_id": interview_id,
        "user_email": user_email
    })

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Interview Not found"
        )

