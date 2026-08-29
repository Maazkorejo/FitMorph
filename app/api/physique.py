from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import os
import uuid
import shutil
from typing import List, Optional

from app.db.session import get_db
from app.core.config import settings
from app.models.user import User
from app.models.physique import PhysiqueScan
from app.schemas.physique import (
    PhysiqueScanResponse,
    PhysiqueProgressComparison,
    CorrectiveExercise
)
from app.services.ai_vision import PhysiqueVisionAnalyzer
from app.api.deps import get_current_user

router = APIRouter(prefix="/physique", tags=["Physique & AI Vision"])

def format_scan_response(scan: PhysiqueScan) -> PhysiqueScanResponse:
    bonus_list = [CorrectiveExercise(**b) for b in scan.bonus_exercise_list]
    return PhysiqueScanResponse(
        id=scan.id,
        user_id=scan.user_id,
        image_filename=scan.image_filename,
        month_number=scan.month_number,
        symmetry_score=scan.symmetry_score,
        posture_assessment=scan.posture_assessment,
        lagging_muscle_groups=scan.lagging_muscle_groups,
        strong_muscle_groups=scan.strong_muscle_groups,
        estimated_body_composition=scan.estimated_body_composition,
        ai_analysis_notes=scan.ai_analysis_notes,
        bonus_exercises=bonus_list,
        created_at=scan.created_at
    )

@router.post("/scan", response_model=PhysiqueScanResponse, status_code=status.HTTP_201_CREATED)
async def upload_physique_scan(
    file: UploadFile = File(...),
    month_number: Optional[int] = Form(1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads a physique check-in photo and runs AI vision symmetry analysis."""
    # Validate image extension
    allowed_exts = [".jpg", ".jpeg", ".png", ".webp"]
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image format. Allowed: {', '.join(allowed_exts)}"
        )

    # Save to uploads folder with unique filename
    unique_filename = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}{ext.lower()}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run AI Vision Analysis
    gender = current_user.profile.gender if current_user.profile else "male"
    analysis = PhysiqueVisionAnalyzer.analyze_image(file_path, gender=gender)

    # Create PhysiqueScan record
    scan = PhysiqueScan(
        user_id=current_user.id,
        image_filename=unique_filename,
        month_number=month_number or 1,
        symmetry_score=float(analysis.get("symmetry_score", 75.0)),
        posture_assessment=analysis.get("posture_assessment", ""),
        lagging_muscle_groups=analysis.get("lagging_muscle_groups", ""),
        strong_muscle_groups=analysis.get("strong_muscle_groups", ""),
        estimated_body_composition=analysis.get("estimated_body_composition", "Athletic"),
        ai_analysis_notes=analysis.get("ai_analysis_notes", "")
    )
    scan.set_bonus_exercises(analysis.get("bonus_exercises", []))

    db.add(scan)
    db.commit()
    db.refresh(scan)

    return format_scan_response(scan)

@router.get("/history", response_model=List[PhysiqueScanResponse])
def get_physique_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all past physique check-ins for the authenticated user."""
    scans = db.query(PhysiqueScan).filter(
        PhysiqueScan.user_id == current_user.id
    ).order_by(PhysiqueScan.created_at.desc()).all()

    return [format_scan_response(s) for s in scans]

@router.get("/progress", response_model=PhysiqueProgressComparison)
def compare_monthly_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compares latest two monthly scans to measure visual symmetry progress."""
    scans = db.query(PhysiqueScan).filter(
        PhysiqueScan.user_id == current_user.id
    ).order_by(PhysiqueScan.created_at.desc()).limit(2).all()

    if len(scans) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 physique scans are required to compare monthly progress."
        )

    current_scan = scans[0]
    previous_scan = scans[1]

    change_pct = round(
        ((current_scan.symmetry_score - previous_scan.symmetry_score) / previous_scan.symmetry_score) * 100.0,
        1
    )

    improvements = [
        f"Symmetry score progressed from {previous_scan.symmetry_score} to {current_scan.symmetry_score}.",
        f"Primary posture note: {current_scan.posture_assessment}"
    ]
    if change_pct > 0:
        improvements.append(f"Visual muscular balance improved by {change_pct}% over previous month.")

    return PhysiqueProgressComparison(
        current_scan_id=current_scan.id,
        previous_scan_id=previous_scan.id,
        month_current=current_scan.month_number,
        month_previous=previous_scan.month_number,
        symmetry_score_current=current_scan.symmetry_score,
        symmetry_score_previous=previous_scan.symmetry_score,
        symmetry_change_pct=change_pct,
        visual_improvements=improvements,
        lagging_areas_status=f"Priority focus: {current_scan.lagging_muscle_groups}",
        next_cycle_focus=f"Prioritize {current_scan.lagging_muscle_groups} while maintaining {current_scan.strong_muscle_groups}."
    )
