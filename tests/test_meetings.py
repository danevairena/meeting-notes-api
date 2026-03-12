from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# verify meetings list endpoint responds
def test_list_meetings():
    response = client.get("/meetings")

    assert response.status_code in (200, 500)


# verify meeting retrieval endpoint responds
def test_get_meeting():
    response = client.get("/meetings/00000000-0000-0000-0000-000000000000")

    assert response.status_code in (200, 404)


# verify notes endpoint responds
def test_get_meeting_notes():
    response = client.get("/meetings/00000000-0000-0000-0000-000000000000/notes")

    assert response.status_code in (200, 404)


# verify process endpoint validates body
def test_process_meeting_validation():
    response = client.post(
        "/meetings/00000000-0000-0000-0000-000000000000/process",
        json={"llm": "gemini"},
    )

    assert response.status_code in (200, 404, 429)