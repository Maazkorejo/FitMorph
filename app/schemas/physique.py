from pydantic import ConfigDict, BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class CorrectiveExercise(BaseModel):
    name: str
    target_muscle: str
    sets: int = 3
    reps: str = "12-15"
    reason: str

class PhysiqueScanResponse(BaseModel):
    id: int
    user_id: int
    image_filename: str
    month_number: int
    symmetry_score: float
    posture_assessment: str
    lagging_muscle_groups: str
    strong_muscle_groups: str
    estimated_body_composition: str
    ai_analysis_notes: str
    bonus_exercises: List[CorrectiveExercise] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PhysiqueProgressComparison(BaseModel):
    current_scan_id: int
    previous_scan_id: int
    month_current: int
    month_previous: int
    symmetry_score_current: float
    symmetry_score_previous: float
    symmetry_change_pct: float
    visual_improvements: List[str] = []
    lagging_areas_status: str
    next_cycle_focus: str
