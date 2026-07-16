from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.config import settings

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    q = db.query(models.Prediction).filter(models.Prediction.user_id == current_user.id)
    total = q.count()
    avg_conf = db.query(func.avg(models.Prediction.confidence)).filter(
        models.Prediction.user_id == current_user.id
    ).scalar() or 0.0
    avg_time = db.query(func.avg(models.Prediction.inference_time_ms)).filter(
        models.Prediction.user_id == current_user.id
    ).scalar() or 0.0

    since = datetime.utcnow() - timedelta(days=14)
    daily = (
        db.query(func.date(models.Prediction.created_at).label("day"), func.count().label("count"))
        .filter(models.Prediction.user_id == current_user.id, models.Prediction.created_at >= since)
        .group_by("day")
        .order_by("day")
        .all()
    )

    active_model = db.query(models.ModelLog).filter(models.ModelLog.is_active == True).first()

    return schemas.DashboardStats(
        total_predictions=total,
        avg_confidence=float(avg_conf),
        avg_inference_time_ms=float(avg_time),
        predictions_by_day=[{"day": str(d.day), "count": d.count} for d in daily],
        active_model=active_model.model_name if active_model else settings.DEFAULT_MODEL,
    )
