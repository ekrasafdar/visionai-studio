import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Float, Integer, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    image_path = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    predicted_label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    top5 = Column(JSON, nullable=False)  # [{label, confidence}, ...]
    inference_time_ms = Column(Float, nullable=False)
    gradcam_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")


class ModelLog(Base):
    __tablename__ = "model_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    model_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    parameters = Column(Integer, nullable=True)
    inference_speed_ms = Column(Float, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingLog(Base):
    __tablename__ = "training_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    model_name = Column(String, nullable=False)
    status = Column(String, default="queued")  # queued|running|completed|failed
    current_epoch = Column(Integer, default=0)
    total_epochs = Column(Integer, default=0)
    train_loss = Column(JSON, nullable=True)   # list of per-epoch values
    val_loss = Column(JSON, nullable=True)
    train_acc = Column(JSON, nullable=True)
    val_acc = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    log_text = Column(Text, nullable=True)
