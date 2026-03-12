import shutil
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.models.meeting import MeetingCreate, MeetingResponse
from app.services.file_extraction_service import extract_transcript
from app.services import meetings_service, projects_service
from app.utils.parsing import parse_meeting_from_path


# create a meeting from an uploaded transcript file
def create_meeting_from_upload(
    file: UploadFile,
    source: str,
    project_name: str | None = None,
) -> MeetingResponse:
    if not file.filename:
        raise ValueError("uploaded file must have a filename")

    suffix = Path(file.filename).suffix.lower()

    # allow only supported transcript file types
    if suffix not in {".docx", ".pdf"}:
        raise ValueError("only .docx and .pdf files are supported")

    temp_file_path: Path | None = None

    try:
        # persist uploaded file temporarily so existing parsing utilities can reuse path-based logic
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = Path(temp_file.name)

        # rename the temporary file to preserve original filename for metadata parsing
        named_temp_path = temp_file_path.with_name(file.filename)
        temp_file_path.replace(named_temp_path)
        temp_file_path = named_temp_path

        # extract meeting metadata from filename and file metadata
        parsed_meeting = parse_meeting_from_path(temp_file_path)

        # extract transcript text from uploaded document
        raw_transcript = extract_transcript(temp_file_path)

        if not raw_transcript.strip():
            raise ValueError("uploaded file does not contain readable transcript text")

        project_id = None

        # resolve project id from project name when provided
        if project_name and project_name.strip():
            project = projects_service.get_or_create_project(project_name.strip())
            project_id = project.id

        meeting_data = MeetingCreate(
            title=parsed_meeting.title,
            meeting_date=parsed_meeting.meeting_date,
            source=source,
            source_file=file.filename,
            raw_transcript=raw_transcript,
            project_id=project_id,
        )

        # reuse existing create meeting flow to persist the uploaded transcript
        return meetings_service.create_meeting(meeting_data)

    finally:
        # close uploaded file handle and remove temporary file
        file.file.close()

        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()