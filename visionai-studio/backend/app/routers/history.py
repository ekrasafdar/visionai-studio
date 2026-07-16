from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(tags=["history"])


@router.get("/history", response_model=List[schemas.PredictionOut])
def history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.user_id == current_user.id)
        .order_by(models.Prediction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.delete("/history/{prediction_id}")
def delete_prediction(prediction_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    record = (
        db.query(models.Prediction)
        .filter(models.Prediction.id == prediction_id, models.Prediction.user_id == current_user.id)
        .first()
    )
    if not record:
        return {"message": "Not found"}
    db.delete(record)
    db.commit()
    return {"message": "Deleted"}
