import pytest
import io
from PIL import Image

def get_auth_header(client, email="physique_user@example.com"):
    client.post("/api/auth/signup", json={"email": email, "password": "password123"})
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def create_dummy_image_bytes():
    file = io.BytesIO()
    image = Image.new("RGB", (200, 400), color=(120, 150, 180))
    image.save(file, format="JPEG")
    file.seek(0)
    return file

def test_physique_scan_upload_and_analysis(client):
    headers = get_auth_header(client, "scanner_athlete@example.com")
    client.post("/api/profile", json={
        "gender": "male",
        "age": 27,
        "height_cm": 178.0,
        "weight_kg": 77.0,
        "fitness_goal": "hypertrophy"
    }, headers=headers)

    img_bytes = create_dummy_image_bytes()
    resp = client.post(
        "/api/physique/scan",
        files={"file": ("checkin_month1.jpg", img_bytes, "image/jpeg")},
        data={"month_number": 1},
        headers=headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "symmetry_score" in data
    assert data["symmetry_score"] >= 50.0
    assert "posture_assessment" in data
    assert "lagging_muscle_groups" in data
    assert len(data["bonus_exercises"]) >= 1

def test_monthly_physique_progress_comparison(client):
    headers = get_auth_header(client, "progress_athlete@example.com")
    client.post("/api/profile", json={
        "gender": "male",
        "age": 28,
        "height_cm": 180.0,
        "weight_kg": 80.0,
        "fitness_goal": "hypertrophy"
    }, headers=headers)

    # Scan 1
    client.post(
        "/api/physique/scan",
        files={"file": ("m1.jpg", create_dummy_image_bytes(), "image/jpeg")},
        data={"month_number": 1},
        headers=headers
    )
    # Scan 2
    client.post(
        "/api/physique/scan",
        files={"file": ("m2.jpg", create_dummy_image_bytes(), "image/jpeg")},
        data={"month_number": 2},
        headers=headers
    )

    comp_resp = client.get("/api/physique/progress", headers=headers)
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert comp_data["month_current"] == 2
    assert comp_data["month_previous"] == 1
    assert "symmetry_change_pct" in comp_data
    assert len(comp_data["visual_improvements"]) >= 1

def test_pdf_report_generation_and_download(client):
    headers = get_auth_header(client, "pdf_athlete@example.com")
    client.post("/api/profile", json={
        "gender": "male",
        "age": 29,
        "height_cm": 183.0,
        "weight_kg": 82.0,
        "fitness_goal": "hypertrophy",
        "equipment_access": "full_gym",
        "injuries": "none"
    }, headers=headers)
    client.post("/api/workouts/generate", json={}, headers=headers)

    # Add a scan
    client.post(
        "/api/physique/scan",
        files={"file": ("test_pose.jpg", create_dummy_image_bytes(), "image/jpeg")},
        data={"month_number": 1},
        headers=headers
    )

    pdf_resp = client.get("/api/reports/download", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    # PDF magic signature: starts with %PDF-
    assert pdf_resp.content.startswith(b"%PDF-")
    assert len(pdf_resp.content) > 1000
