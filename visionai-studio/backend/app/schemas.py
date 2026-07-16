from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_admin: bool
    is_email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Predictions ----------
class ClassProb(BaseModel):
    label: str
    confidence: float


class PredictionOut(BaseModel):
    id: str
    image_path: str
    model_name: str
    predicted_label: str
    confidence: float
    top5: List[ClassProb]
    inference_time_ms: float
    gradcam_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Models / training ----------
class ModelInfo(BaseModel):
    model_name: str
    version: str
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    parameters: Optional[int]
    inference_speed_ms: Optional[float]
    is_active: bool

    class Config:
        from_attributes = True


class RetrainRequest(BaseModel):
    model_name: str  # resnet50 | efficientnet_b3 | mobilenet_v3
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 1e-4


class TrainingStatus(BaseModel):
    id: str
    model_name: str
    status: str
    current_epoch: int
    total_epochs: int
    train_loss: Optional[List[float]]
    val_loss: Optional[List[float]]
    train_acc: Optional[List[float]]
    val_acc: Optional[List[float]]

    class Config:
        from_attributes = True


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    total_predictions: int
    avg_confidence: float
    avg_inference_time_ms: float
    predictions_by_day: List[dict]
    active_model: str


# ---------- Profile ----------
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
