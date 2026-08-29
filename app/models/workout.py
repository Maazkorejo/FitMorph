from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import json
from app.db.session import Base

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(150), nullable=False)
    goal = Column(String(30), nullable=False)  # "fat_loss" | "hypertrophy" | "strength"
    gender = Column(String(20), nullable=False)  # "male" | "female"
    equipment = Column(String(30), nullable=False)  # "full_gym" | "dumbbells_only" | "no_equipment"
    split_type = Column(String(50), nullable=False, default="Upper/Lower")
    weeks = Column(Integer, nullable=False, default=4)

    deload_scheduled = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="workout_plans")
    days = relationship("WorkoutDay", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<WorkoutPlan id={self.id} user_id={self.user_id} title='{self.title}'>"


class WorkoutDay(Base):
    __tablename__ = "workout_days"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False, index=True)

    day_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    day_name = Column(String(100), nullable=False)  # e.g. "Day 1: Upper Power"
    cardio_protocol = Column(String(150), nullable=False, default="None")  # e.g. "Zone 2 Incline Walk: 30 min @ 130 bpm"

    # JSON structured string: list of dicts: [{exercise_id, name, sets, reps, rest_seconds, rpe, cues}]
    exercises_data = Column(Text, nullable=False, default="[]")

    # Relationship
    plan = relationship("WorkoutPlan", back_populates="days")

    @property
    def exercise_list(self) -> list[dict]:
        """Parses exercises_data JSON string to Python list."""
        try:
            return json.loads(self.exercises_data)
        except Exception:
            return []

    def set_exercise_list(self, items: list[dict]) -> None:
        """Serializes exercise list to JSON string."""
        self.exercises_data = json.dumps(items)

    def __repr__(self) -> str:
        return f"<WorkoutDay day_number={self.day_number} name='{self.day_name}'>"
