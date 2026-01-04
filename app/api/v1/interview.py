from fastapi import Depends, APIRouter, status, HTTPException
from datetime import datetime, timezone
from app.schemas.interview import InterviewOut, InterviewCreate, InterviewStatusUpdate
from app.core.permissions import require_roles
from app.db.mongo import db
from app.core.auth_dependencies import get_current_user
from bson import ObjectId
from bson.errors import InvalidId
from app.core.authorization import require_interview_access
from app.core.interview_lifecycle import is_valid_transition


router = APIRouter(prefix = "/v1/interviews", tags = ["interviews"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=InterviewOut)
def create_interview(
    payload: InterviewCreate,
    current_user=Depends(require_roles("admin"))
):
    doc = {
        "title": payload.title,
        "interview_type": payload.interview_type,
        "status": "scheduled",
        "scheduled_at": payload.scheduled_at,
        "created_by": current_user["email"],
        "created_at": datetime.now(timezone.utc),
    }
    result = db.interviews.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "title": doc["title"],
        "interview_type": doc["interview_type"],
        "status": doc["status"],
        "scheduled_at": doc["scheduled_at"],
        "created_by": doc["created_by"],
        "created_at": doc["created_at"],
    }

@router.get("", response_model=list[InterviewOut])
def list_interviews(
    current_user=Depends(require_roles("admin"))
):
    return [
        {
            "id": str(doc["_id"]),
            "title": doc["title"],
            "interview_type": doc["interview_type"],
            "status": doc["status"],
            "scheduled_at": doc.get("scheduled_at"),
            "created_by": doc["created_by"],
            "created_at": doc["created_at"],
        }
        for doc in db.interviews.find().sort("created_at", -1)
    ]

@router.get("/{interview_id}", response_model=InterviewOut)
def get_interview(
    interview_id: str,
    current_user= Depends(get_current_user)
):
    try:
        obj_id = ObjectId(interview_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail= "Invalid Inteview ID")

    interview = db.interviews.find_one({"_id": obj_id})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    require_interview_access(
        interview_id=interview_id,
        user_email=current_user["email"],
        user_role=current_user["role"]
    )
    return {
        "id": str(interview["_id"]),
        "title": interview["title"],
        "interview_type": interview["interview_type"],
        "status": interview["status"],
        "scheduled_at": interview.get("scheduled_at"),
        "created_by": interview["created_by"],
        "created_at": interview["created_at"],
    }

@router.patch("/{interview_id}/status")
def update_interview_status(
    interview_id: str,
    payload: InterviewStatusUpdate,
    current_user=Depends(get_current_user)
):
    try:
        obj_id = ObjectId(interview_id)
    except InvalidId:
        raise HTTPException(status_code = 400, details = "Invalid  interview ID")

    interview = db.interviews.find_one({"_id": obj_id})
    if not interview:
        raise HTTPException(status_code=404, detail= "Interview not found")


    require_interview_access(
        interview_id=interview_id,
        user_email = current_user["email"],
        user_role=current_user["role"]
    )
    current_status = interview["status"]
    new_status = payload.status


    if not is_valid_transition(current_status, new_status):
        raise HTTPException(
            status_code = 400,
            detail=f"Invalid transition from {current_status} to {new_status}"
        )

    #role based restriction
    if current_user["role"] == "candidate":
        raise HTTPException(status_code=403,  detail="Candidates cannot change status")


    if current_user["role"] == "interviewer":
        if current_status == "scheduled" and new_status != "ongoing":
            raise HTTPException(status_code=403, detail="Interviewers can only start interviews")
        if current_status == "onging" and new_status != "completed":
            raise  HTTPException(
                status_code=403,
                detail="Interviewer can only complete interviews"
            )

    # update status
    db.interviews.update_one(
        {"_id" : ObjectId(interview_id)},
        {"$set" : {"status": new_status}}
    )
    return {
        "message": f"Interview status changed from {current_status} to {new_status}"
    }

