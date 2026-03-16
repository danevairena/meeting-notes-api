from datetime import date

from app.models.google_docs_import import GoogleDocsImportRequest, GoogleDocsImportResponse, GoogleDocsImportItemResult
from app.utils.google_docs import extract_google_doc_id, fetch_google_doc_text
from app.models.meeting import MeetingCreate
from app.services import meetings_service


async def import_meetings_from_google_docs(
    payload: GoogleDocsImportRequest,
) -> GoogleDocsImportResponse:
    results: list[GoogleDocsImportItemResult] = []

    for item in payload.meetings:
        try:
            # extract the google doc id from the provided url
            google_doc_id = extract_google_doc_id(str(item.google_doc_url))

            # fetch the document transcript
            transcript = await fetch_google_doc_text(google_doc_id)

            # create the meeting payload for the imported google doc
            meeting_data = MeetingCreate(
                title=item.title,
                meeting_date=date.today(),
                source="google_docs",
                source_file=None,
                source_url=str(item.google_doc_url),
                external_id=google_doc_id,
                raw_transcript=transcript,
                project_id=None,
            )

            # persist the imported meeting through the existing meetings service
            created_meeting = meetings_service.create_meeting(meeting_data)

            results.append(
                GoogleDocsImportItemResult(
                    title=item.title,
                    google_doc_url=str(item.google_doc_url),
                    success=True,
                    meeting_id=str(created_meeting.id),
                    error=None,
                )
            )

        except ValueError as exc:
            # keep processing other items when one item fails validation or fetch
            results.append(
                GoogleDocsImportItemResult(
                    title=item.title,
                    google_doc_url=str(item.google_doc_url),
                    success=False,
                    meeting_id=None,
                    error=str(exc),
                )
            )

        except Exception as exc:
            # avoid losing unexpected persistence errors during debugging
            results.append(
                GoogleDocsImportItemResult(
                    title=item.title,
                    google_doc_url=str(item.google_doc_url),
                    success=False,
                    meeting_id=None,
                    error=str(exc),
                )
            )

    imported = sum(1 for result in results if result.success)
    failed = len(results) - imported

    return GoogleDocsImportResponse(
        total=len(results),
        imported=imported,
        failed=failed,
        results=results,
    )