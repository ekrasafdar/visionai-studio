# VisionAI Studio

A full-stack AI image classification platform — Next.js/TypeScript frontend, FastAPI backend, PostgreSQL, JWT authentication, and a PyTorch transfer-learning pipeline across ResNet50, EfficientNet-B3, and MobileNetV3, with real Grad-CAM explainability.

## Features

- 🔐 JWT auth — register, login, refresh tokens, forgot/reset password, email verification
- 🧠 Three switchable architectures via transfer learning: ResNet50, EfficientNet-B3, MobileNetV3
- 📊 Top-5 confidence scores + real Grad-CAM heatmaps (proper forward/backward hooks, not a fake overlay)
- 📈 Per-user dashboard: prediction history, accuracy/precision/recall/F1, confusion matrices
- 🛠️ Admin panel: manage users, delete predictions, view training logs, platform analytics
- 🔁 Retrain models from the API — background job with live epoch progress
- 🐳 One-command local spin-up via Docker Compose

## Tech stack

| Layer | Stack |
|---|---|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Framer Motion, Recharts |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, JWT (python-jose), Passlib/bcrypt |
| ML | PyTorch, torchvision (ResNet50 / EfficientNet-B3 / MobileNetV3), scikit-learn |
| Infra | Docker, Docker Compose, Redis (optional) |

## Project layout

```
frontend/    Next.js UI — landing, upload/predict, dashboard, auth
backend/     FastAPI REST API, JWT auth, inference + Grad-CAM
ml/          PyTorch training/eval pipeline (Colab/Kaggle-ready)
database/    Reference PostgreSQL schema
docker/      docker-compose.yml wiring db + redis + backend + frontend
docs/        Deployment guide, API reference
```

## Quickstart (Docker)

```bash
git clone <your-repo-url>
cd visionai-studio

cp backend/.env.example backend/.env        # set a real JWT_SECRET_KEY
cp frontend/.env.local.example frontend/.env.local

docker compose -f docker/docker-compose.yml up --build
```

- Frontend: http://localhost:3000
- Backend Swagger docs: http://localhost:8000/docs
- Postgres: localhost:5432 (visionai / visionai)

One-time step, inside the backend container (or locally), to get readable class names before you've trained a custom model:
```bash
python -m app.download_imagenet_labels
```

> **Note on the first Docker build:** the backend image installs PyTorch. If you hit a `pip` read-timeout on `torch` during `docker compose build`, that's a slow-connection issue with the ~800MB CUDA wheel — the Dockerfile in this repo already installs the CPU-only wheel (~200MB) from PyTorch's own index to avoid it. If you still see timeouts, check your network/VPN and retry; `docker compose build --progress plain` will show exactly where it's stuck.

## Training your own model

```bash
cd ml
pip install -r requirements.txt
python -m ml.prepare_data --out ./data/dogs-vs-cats
python -m ml.train --model mobilenet_v3 --epochs 10 --data-dir ./data/dogs-vs-cats
python -m ml.evaluate --model mobilenet_v3 --data-dir ./data/dogs-vs-cats
```
Copy the resulting `mobilenet_v3.pt` + `mobilenet_v3_labels.json` into `backend/ml_models/` (docker-compose already mounts this as a volume). Full instructions, including running for free on Kaggle/Colab, are in `ml/README.md`.

## Deployment

`docs/DEPLOYMENT.md` — Vercel (frontend) + Railway/Render (backend + Postgres), step by step.

## API reference

`docs/API.md`, or the live Swagger UI at `/docs` once the backend is running.

## License

MIT — see LICENSE.
