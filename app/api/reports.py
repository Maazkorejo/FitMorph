from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.db.session import get_db
from app.models.user import User
from app.models.workout import WorkoutPlan
from app.models.physique import PhysiqueScan
from app.services.pdf_generator import PDFGenerator
from app.api.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["PDF Reports"])

@router.get("/download")
def download_pdf_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates and serves the official, printable 4-Week Coaching Dossier PDF."""
    active_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).first()

    if not active_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active workout plan found. Please generate a plan before requesting a PDF dossier."
        )

    latest_scan = db.query(PhysiqueScan).filter(
        PhysiqueScan.user_id == current_user.id
    ).order_by(PhysiqueScan.created_at.desc()).first()

    try:
        pdf_path = PDFGenerator.generate_coaching_dossier(
            user=current_user,
            plan=active_plan,
            latest_scan=latest_scan
        )
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PDF generation failed")

        filename = os.path.basename(pdf_path)
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )

@router.get("/preview")
def preview_report_metadata(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns metadata about the currently available PDF report."""
    active_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).first()

    latest_scan = db.query(PhysiqueScan).filter(
        PhysiqueScan.user_id == current_user.id
    ).order_by(PhysiqueScan.created_at.desc()).first()

    return {
        "user_id": current_user.id,
        "has_active_plan": active_plan is not None,
        "plan_title": active_plan.title if active_plan else None,
        "has_physique_scan": latest_scan is not None,
        "symmetry_score": latest_scan.symmetry_score if latest_scan else None,
        "download_url": "/api/reports/download"
    }
