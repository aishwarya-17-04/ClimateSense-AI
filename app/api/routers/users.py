from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import User, SettingsConfig
from app.schemas.domain import UserResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/settings")
def get_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        settings_record = db.query(SettingsConfig).filter(SettingsConfig.user_id == current_user.id).first()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc

    if not settings_record:
        return {"preferences": {}}
    return settings_record.preferences


@router.get("/users/me/settings")
def get_current_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_settings(current_user=current_user, db=db)
