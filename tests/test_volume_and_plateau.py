import pytest
from datetime import datetime, timedelta, timezone
from app.models.log import LoggedSet
from app.models.user import User

def get_auth_header(client, email="vol_user@example.com"):
    client.post("/api/auth/signup", json={"email": email, "password": "password123"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_log_set_calculates_volume_and_1rm(client):
    headers = get_auth_header(client, "lift_user@example.com")
    payload = {
        "exercise_name": "Barbell Bench Press",
        "muscle_group": "Chest",
        "set_number": 1,
        "weight_kg": 100.0,
        "reps": 5,
        "rpe": 8.5
    }
    resp = client.post("/api/logs/set", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["volume_load"] == 500.0
    # Epley formula: 100 * (1 + 5/30) = 116.67
    assert data["estimated_one_rep_max"] == 116.67

def test_cardio_logging(client):
    headers = get_auth_header(client, "cardio_user@example.com")
    payload = {
        "cardio_type": "Zone 2 LISS",
        "duration_minutes": 35.0,
        "distance_km": 4.2,
        "avg_heart_rate": 132,
        "calories_burned": 280.0
    }
    resp = client.post("/api/logs/cardio", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["cardio_type"] == "Zone 2 LISS"
    assert data["duration_minutes"] == 35.0

def test_volume_summary_and_plateau_status(client):
    headers = get_auth_header(client, "summary_user@example.com")
    client.post("/api/profile", json={
        "gender": "male",
        "age": 25,
        "height_cm": 175.0,
        "weight_kg": 75.0,
        "fitness_goal": "hypertrophy"
    }, headers=headers)
    client.post("/api/workouts/generate", json={}, headers=headers)

    # Log 3 sets
    for i in range(1, 4):
        client.post("/api/logs/set", json={
            "exercise_name": "Incline Dumbbell Press",
            "muscle_group": "Chest",
            "set_number": i,
            "weight_kg": 30.0,
            "reps": 10
        }, headers=headers)

    sum_resp = client.get("/api/logs/summary", headers=headers)
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert sum_data["total_volume_kg"] == 900.0
    assert sum_data["total_sets"] == 3
    assert sum_data["volume_by_muscle"]["Chest"] == 900.0

    plat_resp = client.get("/api/plateau/status", headers=headers)
    assert plat_resp.status_code == 200
    assert "current_week_volume_kg" in plat_resp.json()
