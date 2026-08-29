import sys
import os

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath("."))

from app.db.session import engine, SessionLocal, Base
from app.models.user import User
from app.models.profile import Profile
from app.models.exercise import Exercise
from app.models.workout import WorkoutPlan, WorkoutDay
from app.models.log import LoggedSet, CardioLog
from app.models.physique import PhysiqueScan
from app.core.security import get_password_hash

from app.data.exercises_gym import FULL_GYM_EXERCISES
from app.data.exercises_dumbbells import DUMBBELL_EXERCISES
from app.data.exercises_bodyweight import BODYWEIGHT_EXERCISES

def seed_database():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Exercises
        all_exercises = FULL_GYM_EXERCISES + DUMBBELL_EXERCISES + BODYWEIGHT_EXERCISES
        print(f"Checking {len(all_exercises)} exercises for seeding...")
        added_exercises = 0

        for item in all_exercises:
            existing = db.query(Exercise).filter(Exercise.name == item["name"]).first()
            if not existing:
                ex = Exercise(
                    name=item["name"],
                    primary_muscle=item["primary_muscle"],
                    secondary_muscles=item.get("secondary_muscles", ""),
                    movement_pattern=item["movement_pattern"],
                    equipment_tier=item["equipment_tier"],
                    target_goals=item["target_goals"],
                    spinal_compression=item.get("spinal_compression", "none"),
                    knee_stress=item.get("knee_stress", "none"),
                    shoulder_stress=item.get("shoulder_stress", "none"),
                    wrist_stress=item.get("wrist_stress", "none"),
                    gender_focus=item.get("gender_focus", "unisex"),
                    contraindicated_injuries=item.get("contraindicated_injuries", ""),
                    is_bodyweight=item.get("is_bodyweight", False),
                    instructions=item.get("instructions", "")
                )
                db.add(ex)
                added_exercises += 1

        db.commit()
        print(f"Successfully seeded {added_exercises} new exercises into database.")

        # 2. Seed Demo Test User
        demo_email = "demo@fitmorph.com"
        demo_user = db.query(User).filter(User.email == demo_email).first()
        if not demo_user:
            demo_user = User(
                email=demo_email,
                hashed_password=get_password_hash("demo1234"),
                full_name="Alex Demo Athlete",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            demo_profile = Profile(
                user_id=demo_user.id,
                gender="male",
                age=27,
                height_cm=180.0,
                weight_kg=78.5,
                fitness_goal="hypertrophy",
                experience_level="intermediate",
                equipment_access="full_gym",
                injuries="none"
            )
            db.add(demo_profile)
            db.commit()
            print(f"Created demo user: {demo_email} (password: demo1234)")
        else:
            print(f"Demo user already exists: {demo_email}")

        print("Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
