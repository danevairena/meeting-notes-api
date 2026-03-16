from app.models.google_docs_import import GoogleDocsImportRequest, GoogleDocsImportResponse, GoogleDocsImportItemResult
from app.utils.google_docs import extract_google_doc_id

def import_meetings_from_google_docs(payload: GoogleDocsImportRequest) -> GoogleDocsImportResponse:
    results: list[GoogleDocsImportItemResult] = []

    for item in payload.meetings:
        try:
            # validate the url by extracting the google doc id
            google_doc_id = extract_google_doc_id(str(item.google_doc_url))

            results.append(
                GoogleDocsImportItemResult(
                    title=item.title,
                    google_doc_url=str(item.google_doc_url),
                    success=False,
                    error=f"google doc import not implemented yet for doc id {google_doc_id}",
                )
            )
        except ValueError as exc:
            # keep processing other items when one url is invalid
            results.append(
                GoogleDocsImportItemResult(
                    title=item.title,
                    google_doc_url=str(item.google_doc_url),
                    success=False,
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