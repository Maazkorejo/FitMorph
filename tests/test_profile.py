import pytest

def get_auth_header(client, email="profile_tester@example.com"):
    client.post("/api/auth/signup", json={"email": email, "password": "password123"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_and_get_profile(client):
    headers = get_auth_header(client, "profile1@example.com")

    # Initially 404
    resp = client.get("/api/profile", headers=headers)
    assert resp.status_code == 404

    # Create profile
    payload = {
        "gender": "male",
        "age": 28,
        "height_cm": 180.0,
        "weight_kg": 75.0,
        "fitness_goal": "hypertrophy",
        "experience_level": "intermediate",
        "equipment_access": "full_gym",
        "injuries": "lower_back, knees"
    }
    create_resp = client.post("/api/profile", json=payload, headers=headers)
    assert create_resp.status_code == 201
    data = create_resp.json()
    assert data["bmi"] == 23.1
    assert data["bmi_category"] == "normal"
    assert "lower_back" in data["injury_list"]
    assert "knees" in data["injury_list"]

    # Retrieve profile
    get_resp = client.get("/api/profile", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["bmi"] == 23.1

def test_profile_obese_bmi_calculation(client):
    headers = get_auth_header(client, "profile_obese@example.com")
    payload = {
        "gender": "female",
        "age": 35,
        "height_cm": 160.0,
        "weight_kg": 85.0,
        "fitness_goal": "fat_loss",
        "equipment_access": "no_equipment",
        "injuries": "none"
    }
    resp = client.post("/api/profile", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["bmi"] == 33.2
    assert data["bmi_category"] == "obese"

def test_profile_validation_rejects_invalid_inputs(client):
    headers = get_auth_header(client, "profile_val@example.com")

    # Invalid gender
    bad_gender = {
        "gender": "alien",
        "age": 25,
        "height_cm": 175.0,
        "weight_kg": 70.0,
        "fitness_goal": "hypertrophy"
    }
    resp = client.post("/api/profile", json=bad_gender, headers=headers)
    assert resp.status_code == 422

    # Invalid goal
    bad_goal = {
        "gender": "male",
        "age": 25,
        "height_cm": 175.0,
        "weight_kg": 70.0,
        "fitness_goal": "become_superman"
    }
    resp2 = client.post("/api/profile", json=bad_goal, headers=headers)
    assert resp2.status_code == 422
