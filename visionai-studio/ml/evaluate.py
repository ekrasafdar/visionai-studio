"""
Evaluates a trained checkpoint on the val set: accuracy, precision, recall,
F1, confusion matrix, and inference speed. Writes a JSON report the backend
can ingest into the model_logs table (see database/schema.sql).

Usage:
    python -m ml.evaluate --model mobilenet_v3 --data-dir ./data/dogs-vs-cats
"""
import argparse
import json
import time
from pathlib import Path

import torch
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, accuracy_score

from ml.dataset import build_dataloaders
from ml.train import build_model

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mobilenet_v3", choices=["resnet50", "efficientnet_b3", "mobilenet_v3"])
    parser.add_argument("--data-dir", default="./data/dogs-vs-cats")
    parser.add_argument("--model-dir", default="./ml_models")
    args = parser.parse_args()

    model_dir = Path(args.model_dir)
    class_names = json.loads((model_dir / f"{args.model}_labels.json").read_text())

    model = build_model(args.model, num_classes=len(class_names))
    model.load_state_dict(torch.load(model_dir / f"{args.model}.pt", map_location=DEVICE))
    model.eval().to(DEVICE)

    _, val_loader, _ = build_dataloaders(args.data_dir, image_size=224, batch_size=32, num_workers=2)

    all_preds, all_labels, times = [], [], []
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(DEVICE)
            t0 = time.time()
            outputs = model(images)
            times.append((time.time() - t0) * 1000 / images.size(0))
            preds = outputs.argmax(1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    acc = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average="macro")
    cm = confusion_matrix(all_labels, all_preds).tolist()
    num_params = sum(p.numel() for p in model.parameters())

    report = {
        "model_name": args.model,
        "accuracy": round(acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "class_names": class_names,
        "parameters": num_params,
        "avg_inference_ms": round(sum(times) / len(times), 2),
    }
    out_path = model_dir / f"{args.model}_eval.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
