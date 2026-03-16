from app.models.google_docs_import import GoogleDocsImportRequest, GoogleDocsImportResponse, GoogleDocsImportItemResult


def import_meetings_from_google_docs(payload: GoogleDocsImportRequest) -> GoogleDocsImportResponse:
    results: list[GoogleDocsImportItemResult] = []

    for item in payload.meetings:
        # keep per-item processing isolated for partial success support
        results.append(
            GoogleDocsImportItemResult(
                title=item.title,
                google_doc_url=str(item.google_doc_url),
                success=False,
                error="not implemented yet",
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