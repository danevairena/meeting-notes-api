import re


GOOGLE_DOC_URL_PATTERN = re.compile(
    r"^https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)(?:/.*)?$"
)


def extract_google_doc_id(google_doc_url: str) -> str:
    # extract the google doc id from a standard docs url
    match = GOOGLE_DOC_URL_PATTERN.match(google_doc_url)

    if not match:
        raise ValueError("invalid google docs url")

    return match.group(1)