import pytest

def test_signup_success(client):
    response = client.post(
        "/api/auth/signup",
        json={"email": "athlete@example.com", "password": "securepassword123", "full_name": "Test Athlete"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "athlete@example.com"
    assert data["full_name"] == "Test Athlete"
    assert "id" in data

def test_signup_duplicate_email_fails(client):
    client.post(
        "/api/auth/signup",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/auth/signup",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success_and_jwt_token(client):
    client.post(
        "/api/auth/signup",
        json={"email": "login_test@example.com", "password": "mypassword123"}
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "login_test@example.com", "password": "mypassword123"}
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

def test_login_invalid_password_fails(client):
    client.post(
        "/api/auth/signup",
        json={"email": "wrong_pw@example.com", "password": "correctpassword"}
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "wrong_pw@example.com", "password": "wrongpassword"}
    )
    assert login_resp.status_code == 401
    assert "Invalid email or password" in login_resp.json()["detail"]

def test_get_current_user_authenticated(client):
    client.post(
        "/api/auth/signup",
        json={"email": "me_test@example.com", "password": "password123", "full_name": "Me Tester"}
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "me_test@example.com", "password": "password123"}
    )
    token = login_resp.json()["access_token"]

    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "me_test@example.com"
    assert me_resp.json()["has_profile"] is False

def test_unauthenticated_request_fails(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
