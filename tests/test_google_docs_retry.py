import pytest
import httpx

from app.utils.google_docs import fetch_google_doc_text


class MockResponse:
    def __init__(self, status_code, text="mock text"):
        self.status_code = status_code
        self.text = text


@pytest.mark.asyncio
async def test_fetch_google_doc_retries_on_503(monkeypatch):
    # simulate two temporary failures followed by success
    responses = [
        MockResponse(503),
        MockResponse(503),
        MockResponse(200, "meeting notes content"),
    ]

    async def mock_get(*args, **kwargs):
        return responses.pop(0)

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return await mock_get()

    # patch httpx.AsyncClient with our mock client
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: MockClient())

    text = await fetch_google_doc_text("fake_doc_id")

    assert text == "meeting notes content"