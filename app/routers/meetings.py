from fastapi import APIRouter, HTTPException, status
from app.services import meetings_service
from app.models.meeting import MeetingCreate, MeetingResponse
from app.models.note import MeetingNotesResponse
from app.services import notes_service, processing_service


# create router instance for meeting related endpoints
router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)

# return a list of all meetings
@router.get("/", response_model=list[MeetingResponse])
def list_meetings():
    return meetings_service.list_meetings()

# return a single meeting by id
@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: str):
     return meetings_service.get_meeting_by_id(meeting_id)

# create a new meeting
@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(meeting_data: MeetingCreate):
    return meetings_service.create_meeting(meeting_data)

# return notes for a meeting
@router.get("/{meeting_id}/notes", response_model=MeetingNotesResponse)
def get_meeting_notes(meeting_id: str):
    notes = notes_service.get_notes_by_meeting_id(meeting_id)

    # raise http error if notes do not exist
    if notes is None:
        raise HTTPException(status_code=404, detail="notes not found")

    return notes

# process meeting transcript and generate notes
@router.post("/{meeting_id}/process", response_model=MeetingNotesResponse)
def process_meeting(meeting_id: str):
    return processing_service.process_meeting(meeting_id)