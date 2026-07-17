from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import User, CarbonRecord, Challenge
from app.schemas.domain import CarbonInput, CarbonAnalysisResponse
from app.api.deps import get_current_user
from app.agents.workflow import carbon_app

router = APIRouter()

@router.post("/calculate", response_model=CarbonAnalysisResponse)
async def calculate_carbon(
    data_in: CarbonInput, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inputs = {"input_data": data_in.model_dump()}
    try:
        result = carbon_app.invoke(inputs)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Carbon analysis workflow failed. Please try again.",
        ) from exc

    record = CarbonRecord(
        user_id=current_user.id,
        transport_emissions=data_in.transport_miles * 0.404,
        energy_emissions=data_in.electricity_kwh * 0.385,
        food_emissions=data_in.meat_meals_per_week * 3.3,
        total_score=result["total_emissions"],
    )
    challenge = Challenge(
        user_id=current_user.id,
        title="Daily AI Challenge",
        description=result["challenge"],
    )

    try:
        db.add(record)
        db.add(challenge)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc

    return {
        "total_emissions_kg": round(result["total_emissions"], 2),
        "recommendations": result["recommendations"],
        "daily_challenge": result["challenge"],
        "report_summary": result["report"],
    }


@router.get("/challenge/today")
@router.get("/carbon/challenge/today")
def get_today_challenge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        challenge = (
            db.query(Challenge)
            .filter(
                Challenge.user_id == current_user.id,
                Challenge.is_completed.is_(False),
            )
            .order_by(Challenge.date_assigned.desc())
            .first()
        )
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc

    return challenge or {"message": "No active challenges today."}


@router.post("/challenge/complete/{challenge_id}")
@router.post("/carbon/challenge/complete/{challenge_id}")
def complete_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        challenge = (
            db.query(Challenge)
            .filter(
                Challenge.id == challenge_id,
                Challenge.user_id == current_user.id,
            )
            .first()
        )
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found.")

        challenge.is_completed = True
        db.commit()
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc

    return {"message": "Challenge completed! Badge progress updated."}
