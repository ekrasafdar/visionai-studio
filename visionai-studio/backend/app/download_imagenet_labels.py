"""
One-time setup helper: fetches the standard 1000-class ImageNet label list
and saves it as app/imagenet_classes.json, so /predict returns real class
names (e.g. "golden retriever") instead of fine-tuned-only labels when no
custom checkpoint is loaded yet for a given model.

Run once after installing requirements:
    python -m app.download_imagenet_labels
"""
import json
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
OUT = Path(__file__).parent / "imagenet_classes.json"


def main():
    with urllib.request.urlopen(URL) as resp:
        lines = resp.read().decode("utf-8").splitlines()
    labels = [line.strip() for line in lines if line.strip()]
    OUT.write_text(json.dumps(labels))
    print(f"Saved {len(labels)} labels to {OUT}")


if __name__ == "__main__":
    main()
