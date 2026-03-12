from fastapi import APIRouter, HTTPException, status

from app.models.meeting import MeetingCreate, MeetingResponse
from app.models.note import MeetingNotesResponse
from app.models.processing import ProcessMeetingRequest
from app.services import chunks_service, meetings_service, notes_service, processing_service


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


# return all generated notes versions for a meeting
@router.get("/{meeting_id}/notes", response_model=list[MeetingNotesResponse])
def get_meeting_notes(meeting_id: str):
    notes = notes_service.list_notes_by_meeting_id(meeting_id)

    # raise http error if no notes exist
    if not notes:
        raise HTTPException(status_code=404, detail="notes not found")

    return notes


# return stored transcript chunks for a meeting
@router.get("/{meeting_id}/chunks")
def get_meeting_chunks(meeting_id: str):
    return chunks_service.list_chunks_by_meeting_id(meeting_id)


# create a new meeting
@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(meeting_data: MeetingCreate):
    return meetings_service.create_meeting(meeting_data)


# process meeting transcript and generate notes using selected llm
@router.post("/{meeting_id}/process", response_model=MeetingNotesResponse)
def process_meeting(meeting_id: str, request: ProcessMeetingRequest):
    return processing_service.process_meeting(meeting_id=meeting_id,llm=request.llm)