"""
Downloads and lays out the Dogs vs Cats dataset for ImageFolder-style
training (data_dir/train/{cat,dog}, data_dir/val/{cat,dog}).

Usage (Kaggle/Colab, after `pip install kaggle` and placing kaggle.json
in ~/.kaggle/):
    python -m ml.prepare_data --out ./data/dogs-vs-cats

To use a different dataset, point --out at any directory that already
follows the same train/<class>/*.jpg, val/<class>/*.jpg layout — the
rest of the pipeline (dataset.py, train.py) is dataset-agnostic.
"""
import argparse
import random
import shutil
import zipfile
from pathlib import Path


def download_kaggle_dataset(dest: Path):
    import kaggle  # requires ~/.kaggle/kaggle.json credentials

    kaggle.api.authenticate()
    print("Downloading dogs-vs-cats from Kaggle competition...")
    kaggle.api.competition_download_files("dogs-vs-cats", path=str(dest))
    zip_path = dest / "dogs-vs-cats.zip"
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest)
    # The competition zip nests train.zip/test1.zip inside — extract those too.
    for inner in ["train.zip", "test1.zip"]:
        inner_path = dest / inner
        if inner_path.exists():
            with zipfile.ZipFile(inner_path, "r") as z:
                z.extractall(dest)


def split_into_folders(raw_train_dir: Path, out_dir: Path, val_ratio: float = 0.15, seed: int = 42):
    random.seed(seed)
    files = list(raw_train_dir.glob("*.jpg"))
    cats = [f for f in files if f.name.startswith("cat")]
    dogs = [f for f in files if f.name.startswith("dog")]

    for label, group in [("cat", cats), ("dog", dogs)]:
        random.shuffle(group)
        n_val = int(len(group) * val_ratio)
        val_files, train_files = group[:n_val], group[n_val:]

        for split, files_ in [("train", train_files), ("val", val_files)]:
            target_dir = out_dir / split / label
            target_dir.mkdir(parents=True, exist_ok=True)
            for f in files_:
                shutil.copy(f, target_dir / f.name)

    print(f"Prepared {len(cats)} cat / {len(dogs)} dog images into {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="./data/dogs-vs-cats")
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--skip-download", action="store_true", help="Set if you already have the raw Kaggle 'train' folder locally.")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_download:
        download_kaggle_dataset(out_dir)

    raw_train = out_dir / "train"
    split_into_folders(raw_train, out_dir, val_ratio=args.val_ratio)
