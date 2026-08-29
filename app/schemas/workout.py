from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WorkoutExerciseItem(BaseModel):
    exercise_id: Optional[int] = None
    name: str
    muscle: str
    sets: int = 3
    reps: str = "8-12"
    rest_seconds: int = 90
    rpe_target: float = 8.0
    cues: str = ""
    notes: Optional[str] = None
    is_swap: bool = False

class WorkoutDayResponse(BaseModel):
    id: int
    day_number: int
    day_name: str
    cardio_protocol: str
    exercises: List[WorkoutExerciseItem] = []

class WorkoutPlanResponse(BaseModel):
    id: int
    user_id: int
    title: str
    goal: str
    gender: str
    equipment: str
    split_type: str
    weeks: int
    deload_scheduled: bool
    is_active: bool
    created_at: datetime
    days: List[WorkoutDayResponse] = []

    class Config:
        from_attributes = True

class WorkoutGenerateRequest(BaseModel):
    goal: Optional[str] = None  # overrides profile if provided
    equipment: Optional[str] = None  # overrides profile if provided
    days_per_week: Optional[int] = Field(None, ge=2, le=6)

class ExerciseSwapRequest(BaseModel):
    day_id: int
    exercise_name: str
    reason: Optional[str] = "joint_discomfort"  # "joint_discomfort" | "equipment_busy" | "preference"

class ExerciseSwapResponse(BaseModel):
    success: bool
    original_exercise: str
    replacement: WorkoutExerciseItem
    reason: str
