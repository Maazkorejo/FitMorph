from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class LoggedSet(Base):
    __tablename__ = "logged_sets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    exercise_name = Column(String(100), nullable=False, index=True)
    muscle_group = Column(String(50), nullable=False, index=True)
    set_number = Column(Integer, nullable=False, default=1)
    weight_kg = Column(Float, nullable=False, default=0.0)
    reps = Column(Integer, nullable=False, default=1)
    rpe = Column(Float, nullable=True, default=8.0)  # Rate of Perceived Exertion (1.0 to 10.0)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="logged_sets")

    @property
    def volume_load(self) -> float:
        """Calculates volume load in kg: weight_kg * reps."""
        return round(self.weight_kg * self.reps, 2)

    @property
    def estimated_one_rep_max(self) -> float:
        """Calculates estimated 1RM using Epley formula: weight * (1 + reps/30)."""
        if self.reps <= 1:
            return self.weight_kg
        return round(self.weight_kg * (1.0 + (self.reps / 30.0)), 2)

    def __repr__(self) -> str:
        return f"<LoggedSet {self.exercise_name} set={self.set_number} {self.weight_kg}kg x {self.reps}>"


class CardioLog(Base):
    __tablename__ = "cardio_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    cardio_type = Column(String(50), nullable=False)  # "Zone 2 LISS" | "HIIT" | "Incline Walk" | "Cycling"
    duration_minutes = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=True, default=0.0)
    avg_heart_rate = Column(Integer, nullable=True)
    calories_burned = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="cardio_logs")

    def __repr__(self) -> str:
        return f"<CardioLog {self.cardio_type} duration={self.duration_minutes}min>"
