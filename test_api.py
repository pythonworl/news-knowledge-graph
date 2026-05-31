from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_people():
    response = client.get("/people")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

if __name__ == "__main__":
    print("Running simple API tests...")
    test_get_people()
    print("Tests passed!")
