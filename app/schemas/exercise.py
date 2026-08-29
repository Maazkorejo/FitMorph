from pydantic import ConfigDict, BaseModel, Field
from typing import Optional, List

class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    primary_muscle: str = Field(..., description="Chest, Lats, Quads, Glutes, Shoulders, etc.")
    secondary_muscles: str = Field(default="")
    movement_pattern: str = Field(..., description="Push, Pull, Squat, Hinge, etc.")
    equipment_tier: str = Field(..., description="full_gym | dumbbells_only | no_equipment")
    target_goals: str = Field(default="fat_loss,hypertrophy,strength")

    spinal_compression: str = Field(default="none", description="high | medium | none")
    knee_stress: str = Field(default="none", description="high | medium | none")
    shoulder_stress: str = Field(default="none", description="high | medium | none")
    wrist_stress: str = Field(default="none", description="high | medium | none")

    gender_focus: str = Field(default="unisex", description="unisex | female_emphasis | male_emphasis")
    contraindicated_injuries: str = Field(default="", description="Comma-separated e.g. 'lower_back,knees'")
    is_bodyweight: bool = Field(default=False)
    instructions: str = Field(default="")

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseResponse(ExerciseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ExerciseFilterQuery(BaseModel):
    muscle: Optional[str] = None
    equipment: Optional[str] = None
    goal: Optional[str] = None
    injury: Optional[str] = None
