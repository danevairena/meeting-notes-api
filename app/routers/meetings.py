from fastapi import APIRouter, HTTPException
from app.services import meetings_service

# create router instance for meeting related endpoints
router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)

# return a list of all meetings
@router.get("/")
def list_meetings():
    return meetings_service.list_meetings()

# return a single meeting by id
@router.get("/{meeting_id}")
def get_meeting(meeting_id: str):
    meeting = meetings_service.get_meeting_by_id(meeting_id)

    # raise http error if meeting does not exist
    if meeting is None:
        raise HTTPException(status_code=404, detail="meeting not found")

    return meeting