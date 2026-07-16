from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, ml_service
from app.database import get_db
from app.deps import get_current_user
from app.utils import save_upload, save_gradcam_overlay
from app.config import settings

router = APIRouter(tags=["predict"])

VALID_MODELS = {"resnet50", "efficientnet_b3", "mobilenet_v3"}


@router.post("/predict", response_model=schemas.PredictionOut)
async def predict(
    file: UploadFile = File(...),
    model_name: str = Form(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    model_name = model_name or settings.DEFAULT_MODEL
    if model_name not in VALID_MODELS:
        raise HTTPException(status_code=400, detail=f"model_name must be one of {VALID_MODELS}")

    path, contents = await save_upload(file)

    result = ml_service.predict(contents, model_name, with_gradcam=True)

    gradcam_path = None
    if result["gradcam"] is not None:
        gradcam_path = save_gradcam_overlay(result["gradcam"], contents)

    record = models.Prediction(
        user_id=current_user.id,
        image_path=path,
        model_name=model_name,
        predicted_label=result["predicted_label"],
        confidence=result["confidence"],
        top5=result["top5"],
        inference_time_ms=result["inference_time_ms"],
        gradcam_path=gradcam_path,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
