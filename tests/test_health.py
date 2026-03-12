from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# verify that health endpoint returns service status
def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"