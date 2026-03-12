from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query, File, Form, UploadFile

from app.models.meeting import MeetingCreate, MeetingResponse, MeetingListResponse
from app.models.note import MeetingNotesResponse
from app.models.processing import ProcessMeetingRequest
from app.services import chunks_service, meetings_service, notes_service, process_cache_service, processing_service, upload_meeting_service
from app.errors import NotesNotFoundError, BadRequestError


# create router instance for meeting related endpoints
router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)


# return a list of all meetings with optional project filter
@router.get("/", response_model=list[MeetingListResponse])
def list_meetings(project_id: UUID | None = Query(None)):
    project_id_value = str(project_id) if project_id is not None else None

    return meetings_service.list_meetings(project_id=project_id_value)


# return a single meeting by id
@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: str):
    return meetings_service.get_meeting_by_id(meeting_id)


# return all generated notes versions for a meeting
@router.get("/{meeting_id}/notes", response_model=list[MeetingNotesResponse])
def get_meeting_notes(meeting_id: str):
    notes = notes_service.list_notes_by_meeting_id(meeting_id)

    # raise domain error if no notes exist
    if not notes:
        raise NotesNotFoundError(meeting_id)

    return notes


# return stored transcript chunks for a meeting
@router.get("/{meeting_id}/chunks")
def get_meeting_chunks(meeting_id: str):
    return chunks_service.list_chunks_by_meeting_id(meeting_id)


# create a new meeting
@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(meeting_data: MeetingCreate):
    return meetings_service.create_meeting(meeting_data)


# create a new meeting from uploaded transcript file
@router.post("/upload", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def upload_meeting(
    file: UploadFile = File(...),
    source: str = Form(...),
    project_name: str | None = Form(None),
):
    try:
        return upload_meeting_service.create_meeting_from_upload(
            file=file,
            source=source,
            project_name=project_name,
        )
    # convert validation errors into consistent API error
    except ValueError as exc:
        raise BadRequestError(str(exc)) from exc


# process meeting transcript and generate notes using selected llm
@router.post("/{meeting_id}/process", response_model=MeetingNotesResponse)
def process_meeting(meeting_id: str, request: ProcessMeetingRequest):
    cached_notes = process_cache_service.get_cached_notes(meeting_id=meeting_id, llm=request.llm)

    # return cached result when the same meeting was processed recently
    if cached_notes is not None:
        return cached_notes

    # reject repeated processing calls within the cooldown window
    if process_cache_service.is_rate_limited(meeting_id=meeting_id, llm=request.llm):
        raise HTTPException(
            status_code=429,
            detail="processing rate limit exceeded for this meeting and llm",
        )

    process_cache_service.mark_process_call(meeting_id=meeting_id, llm=request.llm)

    notes = processing_service.process_meeting(meeting_id=meeting_id, llm=request.llm)

    # cache the latest successful processing result
    process_cache_service.set_cached_notes(meeting_id=meeting_id, llm=request.llm, notes=notes)

    return notes