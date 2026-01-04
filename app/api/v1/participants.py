from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from app.db.mongo import db
from app.schemas.participant import ParticipantCreate, ParticipantOut
from app.core.permissions import require_roles

router = APIRouter(
    prefix="/v1/interviews/{interview_id}/participants",
    tags=["participants"]
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ParticipantOut
)
def add_participant(
    interview_id: str,
    payload: ParticipantCreate,
    current_user=Depends(require_roles("admin"))
):
    # Validate interview_id format
    try:
        interview_obj_id = ObjectId(interview_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid interview ID format"
        )

    # Ensure interview exists
    interview = db.interviews.find_one({"_id": interview_obj_id})
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    # Prevent duplicate participant
    existing = db.participants.find_one({
        "interview_id": interview_id,
        "user_email": payload.user_email
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already a participant"
        )

    # Create participant
    doc = {
        "interview_id": interview_id,
        "user_email": payload.user_email,
        "participant_role": payload.participant_role,
        "added_at": datetime.now(timezone.utc),
    }

    db.participants.insert_one(doc)
    return doc
