from sqlalchemy import Column, Integer, String, Text, Boolean
from app.db.session import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)

    # Anatomy & Movement
    primary_muscle = Column(String(50), nullable=False, index=True)  # "Chest", "Lats", "Quads", "Glutes", etc.
    secondary_muscles = Column(String(100), nullable=False, default="")  # "Triceps, Front Delts"
    movement_pattern = Column(String(50), nullable=False, index=True)  # "Push", "Pull", "Squat", "Hinge", etc.

    # Equipment & Goal Suitability
    equipment_tier = Column(String(30), nullable=False, index=True)  # "full_gym" | "dumbbells_only" | "no_equipment"
    target_goals = Column(String(100), nullable=False, default="fat_loss,hypertrophy,strength")  # comma-separated

    # Biomechanical & Joint Impact Flags
    spinal_compression = Column(String(20), nullable=False, default="none")  # "high" | "medium" | "none"
    knee_stress = Column(String(20), nullable=False, default="none")         # "high" | "medium" | "none"
    shoulder_stress = Column(String(20), nullable=False, default="none")     # "high" | "medium" | "none"
    wrist_stress = Column(String(20), nullable=False, default="none")        # "high" | "medium" | "none"

    # Physiological & Injury Filters
    gender_focus = Column(String(30), nullable=False, default="unisex")  # "unisex" | "female_emphasis" | "male_emphasis"
    contraindicated_injuries = Column(String(150), nullable=False, default="")  # e.g. "lower_back,knees"
    is_bodyweight = Column(Boolean, default=False, nullable=False)

    # Coaching & Form Guide
    instructions = Column(Text, nullable=False, default="")

    def is_safe_for(self, user_injuries: list[str]) -> bool:
        """Determines if the exercise is safe given a list of user injury tags."""
        if not user_injuries:
            return True
        contra_set = {c.strip().lower() for c in self.contraindicated_injuries.split(",") if c.strip()}
        for inj in user_injuries:
            if inj.strip().lower() in contra_set:
                return False
        return True

    def matches_equipment(self, allowed_equipment: str) -> bool:
        """Checks if exercise can be performed with the user's available equipment."""
        if allowed_equipment == "full_gym":
            return True
        elif allowed_equipment == "dumbbells_only":
            return self.equipment_tier in ["dumbbells_only", "no_equipment"]
        elif allowed_equipment == "no_equipment":
            return self.equipment_tier == "no_equipment"
        return False

    def __repr__(self) -> str:
        return f"<Exercise name={self.name} muscle={self.primary_muscle} equip={self.equipment_tier}>"
