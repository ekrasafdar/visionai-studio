import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config import settings

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
GRADCAM_DIR = Path("uploads/gradcam")
GRADCAM_DIR.mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile) -> tuple[str, bytes]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG or WEBP images are allowed")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.UPLOAD_MAX_MB:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.UPLOAD_MAX_MB}MB limit")

    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[file.content_type]
    filename = f"{uuid.uuid4()}.{ext}"
    path = UPLOAD_DIR / filename
    path.write_bytes(contents)
    return str(path), contents


def save_gradcam_overlay(cam_array, original_bytes: bytes) -> str:
    """Overlays the Grad-CAM heatmap on the original image and saves it as a PNG."""
    import io
    import numpy as np
    from PIL import Image

    heatmap = (cam_array * 255).astype("uint8")
    heatmap_img = Image.fromarray(heatmap).convert("L").resize((224, 224))

    import matplotlib.cm as cm
    colored = (cm.jet(np.array(heatmap_img) / 255.0)[:, :, :3] * 255).astype("uint8")
    colored_img = Image.fromarray(colored).convert("RGBA")
    colored_img.putalpha(140)

    base = Image.open(io.BytesIO(original_bytes)).convert("RGBA").resize((224, 224))
    overlay = Image.alpha_composite(base, colored_img)

    filename = f"{uuid.uuid4()}.png"
    path = GRADCAM_DIR / filename
    overlay.convert("RGB").save(path)
    return str(path)
