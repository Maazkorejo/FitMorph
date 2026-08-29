from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class SetLogCreate(BaseModel):
    exercise_name: str = Field(..., min_length=2, max_length=100)
    muscle_group: str = Field(..., min_length=2, max_length=50)
    set_number: int = Field(default=1, ge=1, le=20)
    weight_kg: float = Field(default=0.0, ge=0.0, le=500.0)
    reps: int = Field(..., ge=1, le=100)
    rpe: Optional[float] = Field(default=8.0, ge=1.0, le=10.0)
    notes: Optional[str] = None

class SetLogResponse(SetLogCreate):
    id: int
    user_id: int
    volume_load: float
    estimated_one_rep_max: float
    logged_at: datetime

    class Config:
        from_attributes = True

class CardioLogCreate(BaseModel):
    cardio_type: str = Field(..., min_length=2, max_length=50)
    duration_minutes: float = Field(..., ge=1.0, le=360.0)
    distance_km: Optional[float] = Field(default=0.0, ge=0.0)
    avg_heart_rate: Optional[int] = Field(default=None, ge=40, le=220)
    calories_burned: Optional[float] = Field(default=None, ge=0.0)
    notes: Optional[str] = None

class CardioLogResponse(CardioLogCreate):
    id: int
    user_id: int
    logged_at: datetime

    class Config:
        from_attributes = True

class VolumeSummaryResponse(BaseModel):
    total_volume_kg: float
    total_sets: int
    total_reps: int
    volume_by_muscle: Dict[str, float] = {}
    weekly_change_pct: float = 0.0
    plateau_warning: bool = False
