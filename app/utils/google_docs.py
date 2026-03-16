import re, httpx


GOOGLE_DOC_URL_PATTERN = re.compile(
    r"^https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)(?:/.*)?$"
)


def extract_google_doc_id(google_doc_url: str) -> str:
    # extract the google doc id from a standard docs url
    match = GOOGLE_DOC_URL_PATTERN.match(google_doc_url)

    if not match:
        raise ValueError("invalid google docs url")

    return match.group(1)

async def fetch_google_doc_text(google_doc_id: str) -> str:
    # fetch the google doc as plain text using the export endpoint
    export_url = f"https://docs.google.com/document/d/{google_doc_id}/export?format=txt"

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        response = await client.get(export_url)

    if response.status_code == 404:
        # report missing documents clearly
        raise ValueError("google doc not found")

    if response.status_code in (401, 403):
        # report inaccessible documents clearly
        raise ValueError("google doc is not accessible")

    if response.status_code != 200:
        # report unexpected upstream failures
        raise ValueError(f"failed to fetch google doc content with status {response.status_code}")

    text_content = response.text.strip()

    if not text_content:
        # reject empty transcripts
        raise ValueError("google doc content is empty")

    if "<html" in text_content.lower():
        # detect permission or redirect pages returned as html
        raise ValueError("google doc is not publicly accessible")

    return text_content