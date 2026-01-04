from fastapi import APIRouter, status, HTTPException, Depends, Query
from app.schemas.message import MessageOut, MessageCreate
from app.core.auth_dependencies import get_current_user
from bson import ObjectId
from bson.errors import InvalidId
from app.db.mongo import db
from app.core.authorization import require_interview_access
from datetime import datetime, timezone
router = APIRouter(
    prefix="/v1/interviews/{interview_id}/messages",
    tags=["messages"]
)


@router.post("", status_code=status.HTTP_200_OK, response_model=MessageOut)
def create_message(
    interview_id: str,
    payload: MessageCreate,
    current_user=Depends(get_current_user)
):
    try:
        obj_id = ObjectId(interview_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail= "Invalid interview ID")

    interview = db.interviews.find_one({"_id": obj_id})
    if not interview:
        raise HTTPException(status_code = 404, detail= "Interview Not Found")

    require_interview_access(
        interview_id=interview_id,
        user_email=current_user["email"],
        user_role=current_user["role"]
        )

    doc = {
        "interview_id": interview_id,
        "sender_email": current_user["email"],
        "sender_role": current_user["role"],
        "content": payload.content,
        "created_at": datetime.now(timezone.utc),
    }
    db.message.insert_one(doc)
    return doc

# Get message (paginated)
def list_message(
    interview_id: str,
    current_user= Depends(get_current_user),
    limit: int = Query(20, le= 50),
    offset: str = Query(0, ge = 0)
):
    try:
        obj_id = ObjectId(interview_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid interview ID")

    interview = db.interviews.find_one({"_id": obj_id})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview Not Found")


    require_interview_access(
        interview_id=interview_id,
        user_email=current_user["email"],
        user_role=current_user["role"]
    )

    cursor = (
        db.messages
        .find({"interview_id": interview_id})
        .sort("created_at", 1)
        .skip(offset)
        .limit(limit)
    )

    return list(cursor)

