from uuid import UUID, uuid4
from fastapi import APIRouter, status, Query, File, Form, UploadFile, BackgroundTasks, HTTPException

from app.models.meeting import MeetingCreate, MeetingResponse, MeetingListResponse
from app.models.note import MeetingNotesResponse
from app.models.processing import ProcessMeetingRequest
from app.services import chunks_service, meetings_service, notes_service, process_cache_service, processing_service, upload_meeting_service
from app.errors import NotesNotFoundError, RateLimitExceededError
from app.models.google_docs_import import GoogleDocsImportRequest, GoogleDocsImportJobResponse, GoogleDocsImportJobStatusResponse
from app.services.import_jobs import IMPORT_JOBS
from app.services.google_docs_import_service import run_google_docs_import_job


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
    source: str = Form("upload"),
    project_name: str = Form("unknown")
):
    return upload_meeting_service.create_meeting_from_upload(
        file=file,
        source=source,
        project_name=project_name,
    )


# process meeting transcript and generate notes using selected llm
@router.post("/{meeting_id}/process", response_model=MeetingNotesResponse)
def process_meeting(meeting_id: str, request: ProcessMeetingRequest):
    cached_notes = process_cache_service.get_cached_notes(meeting_id=meeting_id, llm=request.llm)

    # return cached result when the same meeting was processed recently
    if cached_notes is not None:
        return cached_notes

    # reject repeated processing calls within the cooldown window
    if process_cache_service.is_rate_limited(meeting_id=meeting_id, llm=request.llm):
        raise RateLimitExceededError(meeting_id, request.llm)

    process_cache_service.mark_process_call(meeting_id=meeting_id, llm=request.llm)

    notes = processing_service.process_meeting(meeting_id=meeting_id, llm=request.llm)

    # cache the latest successful processing result
    process_cache_service.set_cached_notes(meeting_id=meeting_id, llm=request.llm, notes=notes)

    return notes

# start google docs import in the background
@router.post(
    "/import/google-docs",
    response_model=GoogleDocsImportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def import_google_docs(
    request: GoogleDocsImportRequest,
    background_tasks: BackgroundTasks,
):
    # generate a unique id for tracking the background import job
    job_id = str(uuid4())

    # initialize the job state before starting background processing
    IMPORT_JOBS[job_id] = GoogleDocsImportJobStatusResponse(
        job_id=job_id,
        status="pending",
        total=len(request.meetings),
        imported=0,
        failed=0,
        results=[],
        error=None,
    )

    background_tasks.add_task(
        run_google_docs_import_job,
        job_id,
        request,
    )

    return GoogleDocsImportJobResponse(
        job_id=job_id,
        status="pending",
    )

# return the current status and per-item results for a google docs import job
@router.get(
    "/import/google-docs/{job_id}",
    response_model=GoogleDocsImportJobStatusResponse,
)
async def get_google_docs_import_job(job_id: str):
    job = IMPORT_JOBS.get(job_id)

    # return 404 when the provided job id does not exist
    if job is None:
        raise HTTPException(status_code=404, detail="Import job not found")

    return job