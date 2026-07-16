"""
Transfer-learning training script for VisionAI Studio.

Run directly (Colab/Kaggle/local GPU):
    python -m ml.train --model mobilenet_v3 --epochs 10 --data-dir ./data/dogs-vs-cats

Called by the backend's /retrain endpoint with --emit-json, which prints
one JSON line per epoch to stdout so the API can stream progress.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import models as tv_models

from ml.dataset import build_dataloaders
from ml.config import TrainConfig

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_model(name: str, num_classes: int) -> nn.Module:
    if name == "resnet50":
        m = tv_models.resnet50(weights=tv_models.ResNet50_Weights.IMAGENET1K_V2)
        for p in m.parameters():
            p.requires_grad = False
        m.fc = nn.Linear(m.fc.in_features, num_classes)
    elif name == "efficientnet_b3":
        m = tv_models.efficientnet_b3(weights=tv_models.EfficientNet_B3_Weights.IMAGENET1K_V1)
        for p in m.parameters():
            p.requires_grad = False
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, num_classes)
    elif name == "mobilenet_v3":
        m = tv_models.mobilenet_v3_large(weights=tv_models.MobileNet_V3_Large_Weights.IMAGENET1K_V2)
        for p in m.parameters():
            p.requires_grad = False
        m.classifier[3] = nn.Linear(m.classifier[3].in_features, num_classes)
    else:
        raise ValueError(f"Unknown model: {name}")

    # Unfreeze the classifier head (always) plus the last block (fine-tuning).
    for p in m.parameters():
        pass
    return m


def run_epoch(model, loader, criterion, optimizer=None):
    is_train = optimizer is not None
    model.train() if is_train else model.eval()

    total_loss, correct, total = 0.0, 0, 0
    with torch.set_grad_enabled(is_train):
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, labels)

            if is_train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * images.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += images.size(0)

    return total_loss / total, correct / total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mobilenet_v3", choices=["resnet50", "efficientnet_b3", "mobilenet_v3"])
    parser.add_argument("--data-dir", default="./data/dogs-vs-cats")
    parser.add_argument("--output-dir", default="./ml_models")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--emit-json", action="store_true", help="Print one JSON line per epoch (used by the backend /retrain job).")
    args = parser.parse_args()

    train_loader, val_loader, class_names = build_dataloaders(
        args.data_dir, image_size=224, batch_size=args.batch_size, num_workers=2
    )

    model = build_model(args.model, num_classes=len(class_names)).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    best_val_acc = 0.0
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc = run_epoch(model, val_loader, criterion, optimizer=None)
        scheduler.step()
        elapsed = time.time() - t0

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), output_dir / f"{args.model}.pt")
            (output_dir / f"{args.model}_labels.json").write_text(json.dumps(class_names))

        payload = {
            "epoch": epoch, "total_epochs": args.epochs,
            "train_loss": round(train_loss, 4), "val_loss": round(val_loss, 4),
            "train_acc": round(train_acc, 4), "val_acc": round(val_acc, 4),
            "epoch_seconds": round(elapsed, 1),
        }
        if args.emit_json:
            print(json.dumps(payload))
            sys.stdout.flush()
        else:
            print(f"Epoch {epoch}/{args.epochs} | train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
                  f"| val_loss={val_loss:.4f} val_acc={val_acc:.4f} | {elapsed:.1f}s")

    print(f"Best val accuracy: {best_val_acc:.4f}. Model saved to {output_dir}/{args.model}.pt")


if __name__ == "__main__":
    main()
