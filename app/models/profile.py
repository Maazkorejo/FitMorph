from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Core Biometrics
    gender = Column(String(20), nullable=False, default="male")  # "male" | "female"
    age = Column(Integer, nullable=False, default=25)
    height_cm = Column(Float, nullable=False, default=175.0)
    weight_kg = Column(Float, nullable=False, default=70.0)

    # Goals & Context
    fitness_goal = Column(String(30), nullable=False, default="hypertrophy")  # "fat_loss" | "hypertrophy" | "strength"
    experience_level = Column(String(20), nullable=False, default="intermediate")  # "beginner" | "intermediate" | "advanced"
    equipment_access = Column(String(30), nullable=False, default="full_gym")  # "full_gym" | "dumbbells_only" | "no_equipment"

    # Injury & Limitation Flags (comma-separated, e.g. "lower_back,knees,shoulders,wrists" or "none")
    injuries = Column(Text, nullable=False, default="none")

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")

    @property
    def bmi(self) -> float:
        """Calculates Body Mass Index: weight(kg) / (height(m))^2."""
        if self.height_cm and self.height_cm > 0:
            height_m = self.height_cm / 100.0
            return round(self.weight_kg / (height_m * height_m), 1)
        return 0.0

    @property
    def injury_list(self) -> list[str]:
        """Returns list of active injury flags normalized to lowercase."""
        if not self.injuries or self.injuries.strip().lower() in ["none", ""]:
            return []
        return [i.strip().lower() for i in self.injuries.split(",") if i.strip()]

    def __repr__(self) -> str:
        return f"<Profile user_id={self.user_id} goal={self.fitness_goal} gender={self.gender}>"
