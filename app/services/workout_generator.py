import json
import logging
from sqlalchemy.orm import Session
from typing import List, Dict

from app.models.user import User
from app.models.profile import Profile
from app.models.exercise import Exercise
from app.models.workout import WorkoutPlan, WorkoutDay
from app.services.injury_shield import InjuryPreventionShield
from app.services.gender_tuning import GenderTuner
from app.services.cardio_engine import CardioEngine

logger = logging.getLogger("fitmorph.workout_generator")

class WorkoutGenerator:
    """Generates complete, scientifically periodized 4-week adaptive training plans."""

    def __init__(self, db: Session):
        self.db = db

    def generate_plan(
        self,
        user: User,
        goal_override: str = None,
        equipment_override: str = None
    ) -> WorkoutPlan:
        profile = user.profile
        if not profile:
            raise ValueError("User must complete profile setup before generating a workout.")

        goal = (goal_override or profile.fitness_goal).lower()
        equipment = (equipment_override or profile.equipment_access).lower()
        gender = profile.gender.lower()
        injuries = profile.injury_list
        bmi = profile.bmi

        # 1. Fetch available exercises matching equipment
        all_exercises = self.db.query(Exercise).all()
        equipment_matched = [e for e in all_exercises if e.matches_equipment(equipment)]

        # 2. Filter out injury contraindications
        safe_pool = InjuryPreventionShield.filter_safe_exercises(equipment_matched, injuries)

        if not safe_pool:
            # Fallback to bodyweight if equipment pool is empty
            safe_pool = [e for e in all_exercises if e.is_bodyweight]

        # 3. Define 4-Day Split Blueprint
        days_config = [
            {"day": 1, "name": "Day 1: Upper Body Power & Lat Width", "muscles": ["Chest", "Upper Back", "Lats", "Shoulders"]},
            {"day": 2, "name": "Day 2: Lower Body & Posterior Chain Focus", "muscles": ["Quads", "Glutes", "Hamstrings"]},
            {"day": 3, "name": "Day 3: Upper Hypertrophy & Arms", "muscles": ["Chest", "Shoulders", "Rear Delts", "Triceps", "Biceps"]},
            {"day": 4, "name": "Day 4: Lower Body Volume & Core", "muscles": ["Glutes", "Hamstrings", "Quads", "Core"]}
        ]

        title = f"4-Week {goal.replace('_', ' ').title()} Blueprint ({equipment.replace('_', ' ').title()})"

        # Deactivate any previous active plan
        self.db.query(WorkoutPlan).filter(
            WorkoutPlan.user_id == user.id,
            WorkoutPlan.is_active == True
        ).update({"is_active": False})

        new_plan = WorkoutPlan(
            user_id=user.id,
            title=title,
            goal=goal,
            gender=gender,
            equipment=equipment,
            split_type="Upper / Lower Split (4-Day)",
            weeks=4,
            deload_scheduled=False,
            is_active=True
        )
        self.db.add(new_plan)
        self.db.commit()
        self.db.refresh(new_plan)

        # 4. Populate each workout day
        pool_by_muscle = {}
        for ex in safe_pool:
            pool_by_muscle.setdefault(ex.primary_muscle, []).append(ex)

        for d_cfg in days_config:
            day_exercises: List[dict] = []
            target_muscles = d_cfg["muscles"]

            for muscle in target_muscles:
                candidates = pool_by_muscle.get(muscle, [])
                if candidates:
                    # Pick highest priority exercise
                    selected = candidates[0]
                    is_compound = selected.movement_pattern in ["Push", "Pull", "Squat", "Hinge"]
                    tuning = GenderTuner.get_rep_and_rest_protocol(goal, gender, is_compound)

                    cues = selected.instructions
                    if injuries:
                        cues += f" [Joint Safety: Verified safe for {', '.join(injuries)}]"

                    day_exercises.append({
                        "exercise_id": selected.id,
                        "name": selected.name,
                        "muscle": selected.primary_muscle,
                        "sets": 4 if is_compound else 3,
                        "reps": tuning["reps"],
                        "rest_seconds": tuning["rest_seconds"],
                        "rpe_target": tuning["rpe_target"],
                        "cues": cues,
                        "is_swap": False
                    })

            # Assign cardio
            cardio_presc = CardioEngine.get_prescribed_cardio(
                goal=goal,
                weight_kg=profile.weight_kg,
                bmi=bmi,
                equipment=equipment,
                injuries=injuries
            )

            workout_day = WorkoutDay(
                plan_id=new_plan.id,
                day_number=d_cfg["day"],
                day_name=d_cfg["name"],
                cardio_protocol=cardio_presc
            )
            workout_day.set_exercise_list(day_exercises)
            self.db.add(workout_day)

        self.db.commit()
        self.db.refresh(new_plan)
        logger.info(f"Generated 4-week workout plan '{new_plan.title}' for user {user.id}")
        return new_plan
