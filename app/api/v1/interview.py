from fastapi import Depends, APIRouter, status, HTTPException, Query
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from app.schemas.interview import (
    InterviewOut,
    InterviewCreate,
    InterviewStatusUpdate
)
from app.core.permissions import require_roles
from app.core.auth_dependencies import get_current_user
from app.core.authorization import require_interview_access
from app.core.interview_lifecycle import is_valid_transition
from app.core.errors import api_error
from app.core.cache import cache
from app.db.mongo import db

router = APIRouter(prefix="/v1/interviews", tags=["interviews"])

# CREATE INTERVIEW (WRITE → invalidate cache)
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

    # invalidate interview list cache
    cache.invalidate_prefix("interviews:")

    return {
        "id": str(result.inserted_id),
        "title": doc["title"],
        "interview_type": doc["interview_type"],
        "status": doc["status"],
        "scheduled_at": doc["scheduled_at"],
        "created_by": doc["created_by"],
        "created_at": doc["created_at"],
    }

# LIST INTERVIEWS (READ → cached)
@router.get("", response_model=list[InterviewOut])
def list_interviews(
    current_user=Depends(require_roles("admin")),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    status: str | None = None,
    interview_type: str | None = None,
):
    cache_key = f"interviews:{limit}:{offset}:{status}:{interview_type}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    query = {}
    if status:
        query["status"] = status
    if interview_type:
        query["interview_type"] = interview_type

    result = [
        {
            "id": str(doc["_id"]),
            "title": doc["title"],
            "interview_type": doc["interview_type"],
            "status": doc["status"],
            "scheduled_at": doc.get("scheduled_at"),
            "created_by": doc["created_by"],
            "created_at": doc["created_at"],
        }
        for doc in (
            db.interviews
            .find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
    ]

    cache.set(cache_key, result, ttl=60)
    return result
# GET SINGLE INTERVIEW (READ → cached)
@router.get("/{interview_id}", response_model=InterviewOut)
def get_interview(
    interview_id: str,
    current_user=Depends(get_current_user)
):
    cache_key = f"interview:{interview_id}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        obj_id = ObjectId(interview_id)
    except InvalidId:
        api_error(
            status_code=400,
            code="INTERVIEW_INVALID_ID",
            message="Invalid interview ID"
        )

    interview = db.interviews.find_one({"_id": obj_id})
    if not interview:
        api_error(
            status_code=404,
            code="INTERVIEW_NOT_FOUND",
            message="Interview not found"
        )

    require_interview_access(
        interview_id=interview_id,
        user_email=current_user["email"],
        user_role=current_user["role"]
    )

    result = {
        "id": str(interview["_id"]),
        "title": interview["title"],
        "interview_type": interview["interview_type"],
        "status": interview["status"],
        "scheduled_at": interview.get("scheduled_at"),
        "created_by": interview["created_by"],
        "created_at": interview["created_at"],
    }

    cache.set(cache_key, result, ttl=60)
    return result
# UPDATE INTERVIEW STATUS (WRITE → invalidate cache)
@router.patch("/{interview_id}/status")
def update_interview_status(
    interview_id: str,
    payload: InterviewStatusUpdate,
    current_user=Depends(get_current_user)
):
    try:
        obj_id = ObjectId(interview_id)
    except InvalidId:
        api_error(
            status_code=400,
            code="INTERVIEW_INVALID_ID",
            message="Invalid interview ID"
        )

    interview = db.interviews.find_one({"_id": obj_id})
    if not interview:
        api_error(
            status_code=404,
            code="INTERVIEW_NOT_FOUND",
            message="Interview not found"
        )

    require_interview_access(
        interview_id=interview_id,
        user_email=current_user["email"],
        user_role=current_user["role"]
    )

    current_status = interview["status"]
    new_status = payload.status

    if not is_valid_transition(current_status, new_status):
        api_error(
            status_code=400,
            code="INTERVIEW_INVALID_STATUS_TRANSITION",
            message=f"Invalid transition from {current_status} to {new_status}"
        )

    if current_user["role"] == "candidate":
        api_error(
            status_code=403,
            code="PERMISSION_DENIED",
            message="Candidates cannot change interview status"
        )

    if current_user["role"] == "interviewer":
        if current_status == "scheduled" and new_status != "ongoing":
            api_error(
                status_code=403,
                code="PERMISSION_DENIED",
                message="Interviewers can only start interviews"
            )
        if current_status == "ongoing" and new_status != "completed":
            api_error(
                status_code=403,
                code="PERMISSION_DENIED",
                message="Interviewers can only complete interviews"
            )

    db.interviews.update_one(
        {"_id": obj_id},
        {"$set": {"status": new_status}}
    )
    # invalidate caches
    cache.invalidate_prefix("interviews:")
    cache.invalidate_prefix(f"interview:{interview_id}")

    return {
        "message": f"Interview status changed from {current_status} to {new_status}"
    }
