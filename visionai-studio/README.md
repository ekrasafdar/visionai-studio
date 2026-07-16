# VisionAI Studio

A full-stack AI image classification platform: Next.js/TypeScript frontend,
FastAPI backend, PostgreSQL, JWT auth, and a PyTorch transfer-learning
pipeline across ResNet50, EfficientNet-B3, and MobileNetV3.

## Project layout

```
frontend/    Next.js 15 + TypeScript + Tailwind — UI, calls the backend API
backend/     FastAPI + SQLAlchemy + JWT auth — REST API, serves predictions
ml/          PyTorch training/eval pipeline (run on Colab/Kaggle/GPU)
database/    Reference PostgreSQL schema (also auto-created by SQLAlchemy)
docker/      docker-compose.yml wiring db + redis + backend + frontend
docs/        Deployment guide, API reference
```

## Local development (Docker)

```bash
cp backend/.env.example backend/.env      # edit JWT_SECRET_KEY at minimum
cp frontend/.env.local.example frontend/.env.local
docker compose -f docker/docker-compose.yml up --build
```
- Frontend: http://localhost:3000
- Backend docs (Swagger): http://localhost:8000/docs
- Postgres: localhost:5432 (user/pass: visionai/visionai)

One-time setup (inside the backend container or locally before first run):
```bash
python -m app.download_imagenet_labels
```
This fetches the standard 1000 ImageNet class names so `/predict` returns
readable labels even before you've fine-tuned a custom checkpoint.

The backend works immediately with ImageNet-pretrained backbones (no
training required) — it just won't be specialized to your classes until
you run the `ml/` pipeline and drop the resulting checkpoint into
`backend/ml_models/`. See `ml/README.md`.

## Training your own model

```bash
cd ml
pip install -r requirements.txt
python -m ml.prepare_data --out ./data/dogs-vs-cats
python -m ml.train --model mobilenet_v3 --epochs 10 --data-dir ./data/dogs-vs-cats
python -m ml.evaluate --model mobilenet_v3 --data-dir ./data/dogs-vs-cats
```
Copy `ml_models/mobilenet_v3.pt` and `mobilenet_v3_labels.json` into
`backend/ml_models/` (or mount the same volume, as docker-compose.yml does).

## Deployment

See `docs/DEPLOYMENT.md` for the Vercel (frontend) + Railway/Render
(backend + Postgres) path.

## API

See `docs/API.md` for the full endpoint reference, or the live Swagger UI
at `/docs` once the backend is running.
