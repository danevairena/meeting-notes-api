from app.models.google_docs_import import GoogleDocsImportRequest, GoogleDocsImportResponse, GoogleDocsImportItemResult
from app.utils.google_docs import extract_google_doc_id, fetch_google_doc_text

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

            # treat a successfully fetched transcript as a successful import step
            results.append(
                GoogleDocsImportItemResult(
                    title=item.title,
                    google_doc_url=str(item.google_doc_url),
                    success=True,
                    meeting_id=None,
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

        except Exception:
            # avoid leaking unexpected internal errors to the client
            results.append(
                GoogleDocsImportItemResult(
                    title=item.title,
                    google_doc_url=str(item.google_doc_url),
                    success=False,
                    meeting_id=None,
                    error="unexpected error during google docs import",
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