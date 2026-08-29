from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import json
from app.db.session import Base

class PhysiqueScan(Base):
    __tablename__ = "physique_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    image_filename = Column(String(255), nullable=False)
    month_number = Column(Integer, nullable=False, default=1)

    # AI Vision Assessments
    symmetry_score = Column(Float, nullable=False, default=75.0)  # 0.0 to 100.0
    posture_assessment = Column(String(200), nullable=False, default="Neutral spine alignment detected")
    lagging_muscle_groups = Column(String(200), nullable=False, default="Upper Back, Rear Deltoids")
    strong_muscle_groups = Column(String(200), nullable=False, default="Chest, Quadriceps")
    estimated_body_composition = Column(String(50), nullable=False, default="Athletic")

    # Detailed Coaching Guidance
    ai_analysis_notes = Column(Text, nullable=False, default="")
    bonus_exercises_json = Column(Text, nullable=False, default="[]")  # List of corrective exercises injected

    # Timestamp
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="physique_scans")

    @property
    def bonus_exercise_list(self) -> list[dict]:
        try:
            return json.loads(self.bonus_exercises_json)
        except Exception:
            return []

    def set_bonus_exercises(self, exercises: list[dict]) -> None:
        self.bonus_exercises_json = json.dumps(exercises)

    def __repr__(self) -> str:
        return f"<PhysiqueScan id={self.id} user_id={self.user_id} month={self.month_number} score={self.symmetry_score}>"
