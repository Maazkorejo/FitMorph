import logging
from typing import List, Optional
from app.models.exercise import Exercise

logger = logging.getLogger("fitmorph.injury_shield")

# Biomechanical replacement dictionary for high-risk compound lifts
JOINT_SAFE_REPLACEMENTS = {
    # Lower Back / Spinal Compression Replacements
    "Barbell Back Squat": ["Dumbbell Goblet Squat", "Leg Press (High & Wide Stance)", "Isometric Wall Sit", "Dumbbell Bulgarian Split Squat"],
    "Barbell Deadlift": ["Dumbbell Romanian Deadlift", "Barbell Hip Thrust", "Single-Leg Glute Bridge", "Seated Leg Curl"],

    # Shoulder Impingement Replacements
    "Barbell Bench Press": ["Dumbbell Floor Press", "Incline Dumbbell Press", "Cable Chest Flye"],
    "Seated Overhead Dumbbell Press": ["Cable Lateral Raise", "Prone Y-T-W Posture Raises", "Standard Push-Up"],
    "Overhead Dumbbell Tricep Extension": ["Triceps Rope Pushdown"],

    # Knee Pain / Patellar Tendonitis Replacements
    "Air Squat (3-Second Tempo)": ["Isometric Wall Sit", "Single-Leg Glute Bridge"],
    "High-Knee Cardio Intervals": ["Doorframe Bodyweight Row", "Hollow Body Core Hold"],

    # Wrist Pain Replacements
    "Standard Push-Up": ["Forearm Plank", "Dumbbell Floor Press"],
    "Pike Push-Up": ["Prone Y-T-W Posture Raises"]
}

class InjuryPreventionShield:
    """Enforces zero-harm biomechanical boundaries on workout routines."""

    @staticmethod
    def is_exercise_contraindicated(exercise: Exercise, user_injuries: List[str]) -> bool:
        """Returns True if the exercise must be filtered out due to joint pain/injuries."""
        if not user_injuries:
            return False

        contra_raw = exercise.contraindicated_injuries.lower()
        contra_tags = [c.strip() for c in contra_raw.split(",") if c.strip()]

        for injury in user_injuries:
            inj_clean = injury.strip().lower()
            if inj_clean in contra_tags:
                return True
            # Specific biomechanical stress rules:
            if inj_clean == "lower_back" and exercise.spinal_compression == "high":
                return True
            if inj_clean == "knees" and exercise.knee_stress == "high":
                return True
            if inj_clean == "shoulders" and exercise.shoulder_stress == "high":
                return True
            if inj_clean == "wrists" and exercise.wrist_stress == "high":
                return True

        return False

    @classmethod
    def filter_safe_exercises(cls, exercises: List[Exercise], user_injuries: List[str]) -> List[Exercise]:
        """Filters a list of candidate exercises, removing all contraindicated items."""
        safe_list = []
        for ex in exercises:
            if not cls.is_exercise_contraindicated(ex, user_injuries):
                safe_list.append(ex)
            else:
                logger.info(f"InjuryShield blocked '{ex.name}' due to injuries: {user_injuries}")
        return safe_list

    @classmethod
    def find_safe_alternative(
        cls,
        original_name: str,
        user_injuries: List[str],
        available_pool: List[Exercise]
    ) -> Optional[Exercise]:
        """Finds a pre-mapped biomechanically safe alternative for an exercise."""
        replacements = JOINT_SAFE_REPLACEMENTS.get(original_name, [])
        pool_by_name = {e.name: e for e in available_pool}

        for rep_name in replacements:
            candidate = pool_by_name.get(rep_name)
            if candidate and not cls.is_exercise_contraindicated(candidate, user_injuries):
                return candidate

        # Fallback: find any safe exercise targeting the same primary muscle
        orig_ex = pool_by_name.get(original_name)
        if orig_ex:
            for cand in available_pool:
                if (cand.primary_muscle == orig_ex.primary_muscle and
                    cand.name != original_name and
                    not cls.is_exercise_contraindicated(cand, user_injuries)):
                    return cand

        return None
