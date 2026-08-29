import pytest

def get_auth_header(client, email="coach_user@example.com"):
    client.post("/api/auth/signup", json={"email": email, "password": "password123"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_coach_advice_requires_profile(client):
    headers = get_auth_header(client, "noprofile_coach@example.com")
    resp = client.get("/api/coach/advice", headers=headers)
    assert resp.status_code == 400
    assert "complete your profile" in resp.json()["detail"]

def test_coach_advice_with_injuries(client):
    headers = get_auth_header(client, "injured_coach@example.com")
    client.post("/api/profile", json={
        "gender": "male",
        "age": 28,
        "height_cm": 180.0,
        "weight_kg": 82.0,
        "fitness_goal": "hypertrophy",
        "equipment_access": "full_gym",
        "injuries": "lower_back"
    }, headers=headers)

    resp = client.get("/api/coach/advice", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "advice" in data
    assert "Spinal Safety" in data["advice"] or "lower back" in data["advice"].lower()
    assert data["goal"] == "hypertrophy"
    assert data["gender"] == "male"
