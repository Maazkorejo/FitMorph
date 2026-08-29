import pytest
from app.models.exercise import Exercise
from app.services.injury_shield import InjuryPreventionShield

def test_lower_back_injury_blocks_spinal_compression(db_session):
    all_ex = db_session.query(Exercise).all()
    injuries = ["lower_back"]

    safe_exercises = InjuryPreventionShield.filter_safe_exercises(all_ex, injuries)
    safe_names = [e.name for e in safe_exercises]

    # Barbell Back Squat and Barbell Deadlift have high spinal compression and contraindicated tags
    assert "Barbell Back Squat" not in safe_names
    assert "Barbell Deadlift" not in safe_names

    # Non-compressive back and chest movements remain safe
    assert "Chest-Supported Machine Row" in safe_names
    assert "Incline Dumbbell Press" in safe_names

def test_shoulder_injury_blocks_heavy_pressing(db_session):
    all_ex = db_session.query(Exercise).all()
    injuries = ["shoulders"]

    safe_exercises = InjuryPreventionShield.filter_safe_exercises(all_ex, injuries)
    safe_names = [e.name for e in safe_exercises]

    assert "Barbell Bench Press" not in safe_names
    assert "Seated Overhead Dumbbell Press" not in safe_names
    assert "Dumbbell Floor Press" in safe_names

def test_knee_injury_blocks_high_impact_movements(db_session):
    all_ex = db_session.query(Exercise).all()
    injuries = ["knees"]

    safe_exercises = InjuryPreventionShield.filter_safe_exercises(all_ex, injuries)
    safe_names = [e.name for e in safe_exercises]

    assert "Barbell Back Squat" not in safe_names
    assert "High-Knee Cardio Intervals" not in safe_names
    assert "Isometric Wall Sit" in safe_names

def test_joint_safe_substitution_finds_floor_press_for_bench_press(db_session):
    all_ex = db_session.query(Exercise).all()
    injuries = ["shoulders"]

    alt = InjuryPreventionShield.find_safe_alternative("Barbell Bench Press", injuries, all_ex)
    assert alt is not None
    assert alt.name in ["Dumbbell Floor Press", "Incline Dumbbell Press", "Cable Chest Flye"]

def test_joint_safe_substitution_for_squat_when_back_injured(db_session):
    all_ex = db_session.query(Exercise).all()
    injuries = ["lower_back"]

    alt = InjuryPreventionShield.find_safe_alternative("Barbell Back Squat", injuries, all_ex)
    assert alt is not None
    assert alt.name in ["Dumbbell Goblet Squat", "Leg Press (High & Wide Stance)", "Isometric Wall Sit", "Dumbbell Bulgarian Split Squat"]
