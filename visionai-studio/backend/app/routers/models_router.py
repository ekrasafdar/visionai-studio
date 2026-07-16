import threading
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db, SessionLocal
from app.deps import get_current_user

router = APIRouter(tags=["models"])


@router.get("/models", response_model=List[schemas.ModelInfo])
def list_models(db: Session = Depends(get_db)):
    return db.query(models.ModelLog).order_by(models.ModelLog.created_at.desc()).all()


def _run_training_job(training_log_id: str, model_name: str, epochs: int, batch_size: int, lr: float):
    """Runs ml/train.py as a subprocess and streams epoch metrics back into
    the training_logs row. Kept as a background thread so /retrain returns
    immediately with a job id the frontend can poll."""
    import subprocess
    import json

    db = SessionLocal()
    log = db.query(models.TrainingLog).filter(models.TrainingLog.id == training_log_id).first()
    log.status = "running"
    db.commit()

    try:
        proc = subprocess.Popen(
            [
                "python", "-m", "ml.train",
                "--model", model_name,
                "--epochs", str(epochs),
                "--batch-size", str(batch_size),
                "--lr", str(lr),
                "--emit-json",  # ml/train.py prints one JSON line per epoch to stdout
            ],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd="..",
        )
        train_loss, val_loss, train_acc, val_acc = [], [], [], []
        for line in proc.stdout:
            try:
                payload = json.loads(line.strip())
            except (json.JSONDecodeError, ValueError):
                continue
            train_loss.append(payload["train_loss"])
            val_loss.append(payload["val_loss"])
            train_acc.append(payload["train_acc"])
            val_acc.append(payload["val_acc"])
            log.current_epoch = payload["epoch"]
            log.train_loss, log.val_loss = train_loss, val_loss
            log.train_acc, log.val_acc = train_acc, val_acc
            db.commit()
        proc.wait()
        log.status = "completed" if proc.returncode == 0 else "failed"
    except Exception as e:
        log.status = "failed"
        log.log_text = str(e)
    finally:
        log.finished_at = datetime.utcnow()
        db.commit()
        db.close()


@router.post("/retrain", response_model=schemas.TrainingStatus, status_code=202)
def retrain(
    payload: schemas.RetrainRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    log = models.TrainingLog(
        model_name=payload.model_name,
        total_epochs=payload.epochs,
        status="queued",
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    thread = threading.Thread(
        target=_run_training_job,
        args=(log.id, payload.model_name, payload.epochs, payload.batch_size, payload.learning_rate),
        daemon=True,
    )
    thread.start()
    return log


@router.get("/retrain/{training_log_id}", response_model=schemas.TrainingStatus)
def training_status(training_log_id: str, db: Session = Depends(get_db)):
    return db.query(models.TrainingLog).filter(models.TrainingLog.id == training_log_id).first()
