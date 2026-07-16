-- VisionAI Studio — PostgreSQL schema
-- Applied automatically by SQLAlchemy (backend/app/database.py) on startup,
-- kept here as a reference / for manual inspection or non-Python tooling.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    avatar_url VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR,
    password_reset_token VARCHAR,
    password_reset_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_path VARCHAR NOT NULL,
    model_name VARCHAR NOT NULL,
    predicted_label VARCHAR NOT NULL,
    confidence FLOAT NOT NULL,
    top5 JSONB NOT NULL,
    inference_time_ms FLOAT NOT NULL,
    gradcam_path VARCHAR,
    created_at TIMESTAMP DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at);

CREATE TABLE IF NOT EXISTS model_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    parameters INTEGER,
    inference_speed_ms FLOAT,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS training_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'queued',
    current_epoch INTEGER DEFAULT 0,
    total_epochs INTEGER DEFAULT 0,
    train_loss JSONB,
    val_loss JSONB,
    train_acc JSONB,
    val_acc JSONB,
    started_at TIMESTAMP DEFAULT now(),
    finished_at TIMESTAMP,
    log_text TEXT
);
