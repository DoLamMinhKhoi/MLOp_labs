from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_version():
    response = client.get("/get_version")
    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}

def test_check_prime_valid_prime():
    response = client.post("/check_prime", json={"number": 7})
    assert response.status_code == 200
    assert response.json() == {"number": 7, "is_prime": True}

    response = client.post("/check_prime", json={"number": 17})
    assert response.status_code == 200
    assert response.json() == {"number": 17, "is_prime": True}

    response = client.post("/check_prime", json={"number": 31})
    assert response.status_code == 200
    assert response.json() == {"number": 31, "is_prime": True}

    response = client.post("/check_prime", json={"number": 2})
    assert response.status_code == 200
    assert response.json() == {"number": 2, "is_prime": True}

def test_check_prime_valid_non_prime():
    response = client.post("/check_prime", json={"number": 4})
    assert response.status_code == 200
    assert response.json() == {"number": 4, "is_prime": False}

    response = client.post("/check_prime", json={"number": 6})
    assert response.status_code == 200
    assert response.json() == {"number": 6, "is_prime": False}

    response = client.post("/check_prime", json={"number": 8})
    assert response.status_code == 200
    assert response.json() == {"number": 8, "is_prime": False}

    response = client.post("/check_prime", json={"number": 10})
    assert response.status_code == 200
    assert response.json() == {"number": 10, "is_prime": False}

def test_check_prime_invalid_number():
    response = client.post("/check_prime", json={"number": 1})
    assert response.status_code == 400
    assert response.json() == {"detail": "Number must be >= 2"}

    response = client.post("/check_prime", json={"number": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "Number must be >= 2"}