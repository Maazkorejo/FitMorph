from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["User Profile"])

def calculate_bmi_category(bmi: float) -> str:
    """Categorizes BMI value into standard medical classification."""
    if bmi < 18.5:
        return "underweight"
    elif 18.5 <= bmi < 25.0:
        return "normal"
    elif 25.0 <= bmi < 30.0:
        return "overweight"
    else:
        return "obese"

def format_profile_response(profile: Profile) -> ProfileResponse:
    bmi_val = profile.bmi
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        gender=profile.gender,
        age=profile.age,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        fitness_goal=profile.fitness_goal,
        experience_level=profile.experience_level,
        equipment_access=profile.equipment_access,
        injuries=profile.injuries,
        bmi=bmi_val,
        bmi_category=calculate_bmi_category(bmi_val),
        injury_list=profile.injury_list,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.get("", response_model=ProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves physical profile, calculated BMI, and injury flags for current user."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Physical profile not created yet. Please complete onboarding."
        )
    return format_profile_response(profile)

@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates or replaces the physical profile and biometric parameters."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    if profile:
        # Update existing profile
        profile.gender = profile_in.gender
        profile.age = profile_in.age
        profile.height_cm = profile_in.height_cm
        profile.weight_kg = profile_in.weight_kg
        profile.fitness_goal = profile_in.fitness_goal
        profile.experience_level = profile_in.experience_level
        profile.equipment_access = profile_in.equipment_access
        profile.injuries = profile_in.injuries
    else:
        # Create new profile
        profile = Profile(
            user_id=current_user.id,
            gender=profile_in.gender,
            age=profile_in.age,
            height_cm=profile_in.height_cm,
            weight_kg=profile_in.weight_kg,
            fitness_goal=profile_in.fitness_goal,
            experience_level=profile_in.experience_level,
            equipment_access=profile_in.equipment_access,
            injuries=profile_in.injuries
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return format_profile_response(profile)
