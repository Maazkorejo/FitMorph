from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ProfileBase(BaseModel):
    gender: str = Field(..., description="male | female")
    age: int = Field(..., ge=12, le=100, description="Age between 12 and 100")
    height_cm: float = Field(..., ge=100.0, le=250.0, description="Height in centimeters (100 to 250)")
    weight_kg: float = Field(..., ge=30.0, le=300.0, description="Weight in kilograms (30 to 300)")

    fitness_goal: str = Field(..., description="fat_loss | hypertrophy | strength")
    experience_level: str = Field(default="intermediate", description="beginner | intermediate | advanced")
    equipment_access: str = Field(default="full_gym", description="full_gym | dumbbells_only | no_equipment")
    injuries: str = Field(default="none", description="Comma-separated injuries e.g. 'lower_back,knees' or 'none'")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'")
        return clean

    @field_validator("fitness_goal")
    @classmethod
    def validate_goal(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in ["fat_loss", "hypertrophy", "strength"]:
            raise ValueError("Goal must be 'fat_loss', 'hypertrophy', or 'strength'")
        return clean

    @field_validator("equipment_access")
    @classmethod
    def validate_equipment(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in ["full_gym", "dumbbells_only", "no_equipment"]:
            raise ValueError("Equipment must be 'full_gym', 'dumbbells_only', or 'no_equipment'")
        return clean

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=12, le=100)
    height_cm: Optional[float] = Field(None, ge=100.0, le=250.0)
    weight_kg: Optional[float] = Field(None, ge=30.0, le=300.0)
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None
    equipment_access: Optional[str] = None
    injuries: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    bmi: float
    bmi_category: str = "normal"
    injury_list: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
