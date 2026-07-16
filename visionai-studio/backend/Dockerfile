FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 gcc \
    && rm -rf /var/lib/apt/lists/*
ENV PIP_DEFAULT_TIMEOUT=1000 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .

# Install torch/torchvision from PyTorch's CPU-only index FIRST.
# The default PyPI wheel bundles full CUDA libs and is ~779MB, which is
# what was timing out on pip's default 15s read timeout / slow connections.
# The CPU-only wheel is ~200MB. This does not change functionality: the
# app already checks torch.cuda.is_available() at runtime and only uses
# a GPU if one is present (see app/ml_service.py) — this backend targets
# CPU inference on Railway/Render per docs/DEPLOYMENT.md anyway.
RUN pip install --no-cache-dir --default-timeout=1000 --retries 10 \
    torch==2.3.1 torchvision==0.18.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Now install everything else. pip sees torch/torchvision already satisfy
# the pinned versions in requirements.txt and skips re-downloading them.
RUN pip install --no-cache-dir --default-timeout=1000 --retries 10 -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]