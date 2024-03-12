from points_air import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_hello():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == "Bonjour!"
