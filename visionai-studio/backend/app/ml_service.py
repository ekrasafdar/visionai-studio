"""
Loads trained classification models and runs inference + Grad-CAM.
Supports resnet50, efficientnet_b3, mobilenet_v3 — all fine-tuned via
ml/train.py and exported with ml/export_model.py into MODEL_DIR.

Falls back to ImageNet-pretrained torchvision weights (with the 1000-class
label set) if no fine-tuned checkpoint is found yet, so the API is usable
immediately after `docker compose up`, before you've run any training.
"""
import io
import json
import os
import time
from pathlib import Path
from typing import Tuple, List, Dict

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms, models as tv_models

from app.config import settings

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

PREPROCESS = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])

_MODEL_CACHE: Dict[str, torch.nn.Module] = {}
_LABELS_CACHE: Dict[str, List[str]] = {}
_TARGET_LAYER_CACHE: Dict[str, torch.nn.Module] = {}


def _build_architecture(name: str, num_classes: int) -> torch.nn.Module:
    if name == "resnet50":
        m = tv_models.resnet50(weights=tv_models.ResNet50_Weights.IMAGENET1K_V2)
        m.fc = torch.nn.Linear(m.fc.in_features, num_classes)
        return m
    if name == "efficientnet_b3":
        m = tv_models.efficientnet_b3(weights=tv_models.EfficientNet_B3_Weights.IMAGENET1K_V1)
        m.classifier[1] = torch.nn.Linear(m.classifier[1].in_features, num_classes)
        return m
    if name == "mobilenet_v3":
        m = tv_models.mobilenet_v3_large(weights=tv_models.MobileNet_V3_Large_Weights.IMAGENET1K_V2)
        m.classifier[3] = torch.nn.Linear(m.classifier[3].in_features, num_classes)
        return m
    raise ValueError(f"Unknown model: {name}")


def _target_layer(model: torch.nn.Module, name: str) -> torch.nn.Module:
    if name == "resnet50":
        return model.layer4[-1]
    if name == "efficientnet_b3":
        return model.features[-1]
    if name == "mobilenet_v3":
        return model.features[-1]
    raise ValueError(name)


def _checkpoint_path(name: str) -> Path:
    return Path(settings.MODEL_DIR) / f"{name}.pt"


def _labels_path(name: str) -> Path:
    return Path(settings.MODEL_DIR) / f"{name}_labels.json"


def load_model(name: str) -> Tuple[torch.nn.Module, List[str]]:
    """Loads (and caches) a fine-tuned checkpoint if present, else a plain
    ImageNet backbone so the endpoint still returns real predictions."""
    if name in _MODEL_CACHE:
        return _MODEL_CACHE[name], _LABELS_CACHE[name]

    ckpt_path = _checkpoint_path(name)
    labels_path = _labels_path(name)

    if ckpt_path.exists() and labels_path.exists():
        labels = json.loads(labels_path.read_text())
        model = _build_architecture(name, num_classes=len(labels))
        state = torch.load(ckpt_path, map_location=DEVICE)
        model.load_state_dict(state)
    else:
        # No fine-tuned weights yet — fall back to ImageNet-1000 backbone.
        imagenet_labels_file = Path(__file__).parent / "imagenet_classes.json"
        labels = json.loads(imagenet_labels_file.read_text()) if imagenet_labels_file.exists() else [str(i) for i in range(1000)]
        model = _build_architecture(name, num_classes=len(labels)) if labels_path.exists() else {
            "resnet50": tv_models.resnet50(weights=tv_models.ResNet50_Weights.IMAGENET1K_V2),
            "efficientnet_b3": tv_models.efficientnet_b3(weights=tv_models.EfficientNet_B3_Weights.IMAGENET1K_V1),
            "mobilenet_v3": tv_models.mobilenet_v3_large(weights=tv_models.MobileNet_V3_Large_Weights.IMAGENET1K_V2),
        }[name]

    model.eval().to(DEVICE)
    _MODEL_CACHE[name] = model
    _LABELS_CACHE[name] = labels
    _TARGET_LAYER_CACHE[name] = _target_layer(model, name)
    return model, labels


class GradCAM:
    """Standard Grad-CAM: hooks the last conv block, backprops the target
    class score, and weights activation maps by their averaged gradients."""

    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.activations = None
        self.gradients = None
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, inp, out):
        self.activations = out.detach()

    def _save_gradient(self, module, grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def generate(self, input_tensor: torch.Tensor, class_idx: int) -> np.ndarray:
        self.model.zero_grad()
        output = self.model(input_tensor)
        score = output[0, class_idx]
        score.backward()

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=(224, 224), mode="bilinear", align_corners=False)
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam


def predict(image_bytes: bytes, model_name: str, with_gradcam: bool = True):
    model, labels = load_model(model_name)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = PREPROCESS(image).unsqueeze(0).to(DEVICE)
    tensor.requires_grad_(True)

    t0 = time.time()
    with torch.no_grad():
        logits = model(tensor)
        probs = F.softmax(logits, dim=1)[0]
    elapsed_ms = (time.time() - t0) * 1000

    top5_prob, top5_idx = torch.topk(probs, k=min(5, probs.shape[0]))
    top5 = [{"label": labels[i], "confidence": float(p)} for p, i in zip(top5_prob, top5_idx)]

    cam_array = None
    if with_gradcam:
        cam_gen = GradCAM(model, _TARGET_LAYER_CACHE[model_name])
        cam_array = cam_gen.generate(tensor, int(top5_idx[0]))

    return {
        "predicted_label": top5[0]["label"],
        "confidence": top5[0]["confidence"],
        "top5": top5,
        "inference_time_ms": elapsed_ms,
        "gradcam": cam_array,  # 224x224 float array in [0,1], caller renders/saves it
    }
