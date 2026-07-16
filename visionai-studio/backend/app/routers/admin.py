from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@router.patch("/users/{user_id}/disable")
def disable_user(user_id: str, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
    return {"message": "User disabled"}


@router.delete("/predictions/{prediction_id}")
def delete_any_prediction(prediction_id: str, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    record = db.query(models.Prediction).filter(models.Prediction.id == prediction_id).first()
    if record:
        db.delete(record)
        db.commit()
    return {"message": "Deleted"}


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    total_users = db.query(models.User).count()
    total_predictions = db.query(models.Prediction).count()
    total_training_runs = db.query(models.TrainingLog).count()
    return {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "total_training_runs": total_training_runs,
    }


@router.get("/logs", response_model=List[schemas.TrainingStatus])
def training_logs(db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    return db.query(models.TrainingLog).order_by(models.TrainingLog.started_at.desc()).all()
