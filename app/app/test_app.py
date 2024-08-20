from fastapi.testclient import TestClient
import pytest

from app import app, users, sign_jwt

client = TestClient(app)

def get_token(username: str, password: str) -> str:
    print(client.post("/app/register", json={"username": username, "password": password}))
    response = client.post("/app/login", json={"username": username, "password": password})
    print(response)
    return response.json()["token"]

def test_register_success():
    response = client.post("/app/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "username":"testuser"}
    assert users['testuser'] == "testpass"

def test_register_failed_exists():
    client.post("/app/register", json={"username": "testuser", "password": "testpass"})
    response = client.post("/app/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 405


def test_login_successful():
    users["testuser"] = "testpass"
    client.post("/app/register", json={"username": "testuser", "password": "testpass"})
    response = client.post("/app/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200

def test_login_invalid_password():
    users["testuser"] = "testpass"
    
    response = client.post("/app/login", json={"username": "testuser", "password": "wrongpass"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid username or password"}

def test_login_nonexistent_user():
    response = client.post("/app/login", json={"username": "nonexistentuser", "password": "anypass"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid username or password"}

def test_login_invalid_user_data():
    response = client.post("/app/login", json={"password": "testpass"})
    assert response.status_code == 422 

    response = client.post("/app/login", json={"username": "testuser"})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_tnt_insert():
    token = get_token("testuser", "testpass")
    headers = {"Authorization": f"Bearer {token}"}

    data = {"data": {"key1": "value1", "key2": "value2"}}
    response = client.post("/app/write", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

@pytest.mark.asyncio
async def test_tnt_insert_duplicate_keys():
    token = get_token("testuser", "testpass")
    headers = {"Authorization": f"Bearer {token}"}

    data = {"data": {"key1": "value1"}}
    client.post("/app/write", json=data, headers=headers)
    response = client.post("/app/write", json=data, headers=headers)
    assert response.status_code == 3

@pytest.mark.asyncio
async def test_tnt_read():
    token = get_token("testuser", "testpass")
    headers = {"Authorization": f"Bearer {token}"}

    keys = {"keys": ["key1", "key2", "nonexistent_key"]}
    response = client.post("/app/read", json=keys, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "key1": "value1",
            "key2": "value2",
            "nonexistent_key": None
        }
    }