# Deployment Guide — Vercel + Railway/Render

## 1. Backend + PostgreSQL → Railway or Render

**Railway** (fastest path):
1. `railway login` → `railway init` inside `backend/`.
2. Add a PostgreSQL plugin from the Railway dashboard — it gives you a
   `DATABASE_URL` automatically.
3. Set environment variables (Railway → Variables tab), copying from
   `backend/.env.example`: `JWT_SECRET_KEY` (generate a real random
   value — `openssl rand -hex 32`), `CORS_ORIGINS` (your Vercel URL,
   added after step 2 below), `DEFAULT_MODEL`.
4. Railway auto-detects the `Dockerfile` in `backend/` and builds from it.
5. Note the generated public URL, e.g. `https://visionai-backend.up.railway.app`.

**Render** is equivalent: New → Web Service → point at `backend/`,
Render reads the Dockerfile automatically; New → PostgreSQL for the
database, copy its connection string into `DATABASE_URL`.

Either way, GPU inference isn't available on these platforms' standard
tiers — CPU inference works fine for MobileNetV3/single-image requests;
for heavier ResNet50/EfficientNet-B3 traffic at scale, look at a GPU
instance (e.g. Lambda, RunPod) behind the same FastAPI app.

## 2. Frontend → Vercel

1. `vercel login` → `vercel` inside `frontend/`, or connect the repo via
   the Vercel dashboard and set the root directory to `frontend/`.
2. Set the environment variable `NEXT_PUBLIC_API_URL` to your Railway/Render
   backend URL from step 1.
3. Deploy. Vercel builds the Next.js app automatically — no Dockerfile needed there.

## 3. Wire CORS

Go back to the backend's `CORS_ORIGINS` env var and add your live Vercel
URL (e.g. `https://visionai-studio.vercel.app`), redeploy the backend.

## 4. Uploaded images & model checkpoints

Railway/Render containers have ephemeral disks by default — uploaded
images and `ml_models/*.pt` checkpoints will be wiped on redeploy unless
you attach a persistent volume (both platforms support this) or switch
`app/utils.py` to write to S3/R2/Cloudinary instead of local disk. For a
portfolio deployment, a persistent volume is the simplest fix.

## 5. Redis (optional)

Only needed if you extend the backend with caching or a job queue.
Railway/Render both offer a one-click Redis plugin; point `REDIS_URL` at it.
