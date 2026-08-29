import pytest
from app.models.workout import WorkoutPlan

def get_auth_header(client, email="gen_test@example.com"):
    client.post("/api/auth/signup", json={"email": email, "password": "password123"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_generate_full_gym_workout_plan(client):
    headers = get_auth_header(client, "gym_guy@example.com")
    client.post("/api/profile", json={
        "gender": "male",
        "age": 26,
        "height_cm": 182.0,
        "weight_kg": 80.0,
        "fitness_goal": "hypertrophy",
        "equipment_access": "full_gym",
        "injuries": "none"
    }, headers=headers)

    gen_resp = client.post("/api/workouts/generate", json={}, headers=headers)
    assert gen_resp.status_code == 201
    plan = gen_resp.json()
    assert len(plan["days"]) == 4
    assert plan["equipment"] == "full_gym"
    assert plan["gender"] == "male"
    assert "Hypertrophy" in plan["title"]

    day1 = plan["days"][0]
    assert len(day1["exercises"]) >= 3
    # Check that rest seconds for male hypertrophy compound is around 90s
    assert day1["exercises"][0]["rest_seconds"] >= 60

def test_generate_female_bodyweight_with_knee_injury(client):
    headers = get_auth_header(client, "female_bw@example.com")
    client.post("/api/profile", json={
        "gender": "female",
        "age": 29,
        "height_cm": 165.0,
        "weight_kg": 58.0,
        "fitness_goal": "fat_loss",
        "equipment_access": "no_equipment",
        "injuries": "knees"
    }, headers=headers)

    gen_resp = client.post("/api/workouts/generate", json={}, headers=headers)
    assert gen_resp.status_code == 201
    plan = gen_resp.json()
    assert plan["equipment"] == "no_equipment"
    assert plan["gender"] == "female"

    all_ex_names = []
    for day in plan["days"]:
        for ex in day["exercises"]:
            all_ex_names.append(ex["name"])

    # High knee cardio and heavy squats contraindicated for knees must not be selected
    assert "High-Knee Cardio Intervals" not in all_ex_names
    assert "Barbell Back Squat" not in all_ex_names

def test_1click_exercise_swap(client):
    headers = get_auth_header(client, "swap_user@example.com")
    client.post("/api/profile", json={
        "gender": "male",
        "age": 30,
        "height_cm": 178.0,
        "weight_kg": 76.0,
        "fitness_goal": "hypertrophy",
        "equipment_access": "full_gym",
        "injuries": "shoulders"
    }, headers=headers)

    gen_resp = client.post("/api/workouts/generate", json={}, headers=headers)
    plan = gen_resp.json()
    day1 = plan["days"][0]
    first_ex = day1["exercises"][0]["name"]

    swap_resp = client.post("/api/workouts/swap", json={
        "day_id": day1["id"],
        "exercise_name": first_ex,
        "reason": "joint_discomfort"
    }, headers=headers)

    assert swap_resp.status_code == 200
    swap_data = swap_resp.json()
    assert swap_data["success"] is True
    assert swap_data["original_exercise"] == first_ex
    assert swap_data["replacement"]["name"] != first_ex
