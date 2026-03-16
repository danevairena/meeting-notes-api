import asyncio
import io
import logging
import re

import httpx
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from app.settings import settings


logger = logging.getLogger(__name__)


GOOGLE_DOC_URL_PATTERN = re.compile(
    r"^https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)(?:/.*)?$"
)

GOOGLE_DOC_EXPORT_URL = "https://docs.google.com/document/d/{doc_id}/export?format=txt"

# retry only for temporary upstream failures
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

# keep retries small to avoid long request times
MAX_RETRIES = 3

# base delay for exponential backoff
BASE_BACKOFF_SECONDS = 0.5

# read private docs through google drive api
GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def extract_google_doc_id(google_doc_url: str) -> str:
    # extract the google doc id from a standard docs url
    match = GOOGLE_DOC_URL_PATTERN.match(google_doc_url)

    if not match:
        raise ValueError("invalid google docs url")

    return match.group(1)

async def fetch_public_google_doc_text(google_doc_id: str) -> str:
    # fetch the google doc as plain text using the public export endpoint
    export_url = GOOGLE_DOC_EXPORT_URL.format(doc_id=google_doc_id)

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        # retry a few times for temporary upstream errors
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = await client.get(export_url)

                if response.status_code == 404:
                    raise ValueError("google doc not found")

                if response.status_code in (401, 403):
                    # signal that public access is not available
                    raise PermissionError("google doc is not publicly accessible")

                if response.status_code in RETRYABLE_STATUS_CODES:
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(BASE_BACKOFF_SECONDS * (2 ** attempt))
                        continue

                    raise ValueError(
                        f"failed to fetch google doc content with status {response.status_code}"
                    )

                if response.status_code != 200:
                    raise ValueError(
                        f"failed to fetch google doc content with status {response.status_code}"
                    )

                text_content = response.text.strip()

                if not text_content:
                    raise ValueError("google doc content is empty")

                if "<html" in text_content.lower():
                    raise PermissionError("google doc is not publicly accessible")

                return text_content

            except (httpx.TimeoutException, httpx.NetworkError):
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(BASE_BACKOFF_SECONDS * (2 ** attempt))
                    continue

                raise ValueError("network error while fetching google doc")

    raise ValueError("failed to fetch google doc content")

def fetch_private_google_doc_text(google_doc_id: str) -> str:
    # require service account configuration for private docs
    if not settings.google_service_account_file:
        raise ValueError("google service account is not configured")

    try:
        # build service account credentials for drive api access
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_service_account_file,
            scopes=GOOGLE_DRIVE_SCOPES,
        )

        # use drive api export to read the google doc as plain text
        service = build("drive", "v3", credentials=credentials, cache_discovery=False)
        request = service.files().export_media(
            fileId=google_doc_id,
            mimeType="text/plain",
        )

        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        text_content = buffer.getvalue().decode("utf-8").strip()

        if not text_content:
            raise ValueError("google doc content is empty")

        logger.info("private google doc fetch succeeded for doc_id=%s", google_doc_id)
        return text_content

    except HttpError as exc:
        status_code = getattr(exc.resp, "status", None)

        if status_code == 404:
            logger.warning(
                "private google doc fetch failed doc_id=%s reason=not_found_or_not_shared",
                google_doc_id,
            )
            raise ValueError("private google doc not found or not shared with service account")

        if status_code == 403:
            logger.warning(
                "private google doc fetch failed doc_id=%s reason=forbidden",
                google_doc_id,
            )
            raise ValueError("private google doc is not accessible by the service account")

        logger.exception(
            "unexpected google drive api error while fetching doc_id=%s",
            google_doc_id,
        )
        raise ValueError("failed to fetch private google doc")

    except Exception:
        logger.exception(
            "unexpected private google doc fetch failure doc_id=%s",
            google_doc_id,
        )
        raise ValueError("failed to fetch private google doc")

async def fetch_google_doc_text(google_doc_id: str) -> str:
    # try public access first and fall back to private access if needed
    try:
        return await fetch_public_google_doc_text(google_doc_id)
    except PermissionError:
        logger.info(
            "public google doc access failed, falling back to private fetch doc_id=%s",
            google_doc_id,
        )
        return fetch_private_google_doc_text(google_doc_id)