from fastapi.testclient import TestClient

from src.application import get_app


app = get_app()

client = TestClient(app)


def test_read_root():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert "ok" in str(response.content)