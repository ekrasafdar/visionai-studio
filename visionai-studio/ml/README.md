# VisionAI Studio — ML Pipeline

Transfer-learning training pipeline for the three supported architectures:
`resnet50`, `efficientnet_b3`, `mobilenet_v3`. Dataset-agnostic — ships
configured for Dogs vs Cats, swap in any ImageFolder-structured dataset.

## Quickstart on Kaggle or Colab (recommended — free GPU)

1. Open a new Kaggle Notebook or Colab notebook, enable a GPU runtime.
2. Upload this `ml/` folder (or `git clone` your repo).
3. Install deps:
   ```bash
   pip install -r ml/requirements.txt
   ```
4. On Kaggle: add the "Dogs vs. Cats" competition dataset to the notebook
   directly (Kaggle mounts it at `/kaggle/input/dogs-vs-cats` — no download
   needed, skip step 5).
   On Colab: get a Kaggle API token (kaggle.com → Account → Create New
   Token), upload `kaggle.json`, then:
   ```bash
   mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
   python -m ml.prepare_data --out ./data/dogs-vs-cats
   ```
5. Train:
   ```bash
   python -m ml.train --model mobilenet_v3 --epochs 10 --data-dir ./data/dogs-vs-cats
   ```
   Swap `--model resnet50` or `--model efficientnet_b3` to compare architectures.
6. Evaluate:
   ```bash
   python -m ml.evaluate --model mobilenet_v3 --data-dir ./data/dogs-vs-cats
   ```
   Produces `ml_models/mobilenet_v3_eval.json` with accuracy, precision,
   recall, F1, and a confusion matrix — insert these into the `model_logs`
   table (see `database/schema.sql`) so the dashboard/model-comparison
   pages in the frontend can display them.
7. Copy the resulting `ml_models/*.pt` and `*_labels.json` files into the
   backend's `MODEL_DIR` (set in `.env`) — `app/ml_service.py` picks them
   up automatically on next request.

## Using your own dataset

Any dataset laid out as:
```
data_dir/train/<class_a>/*.jpg
data_dir/train/<class_b>/*.jpg
data_dir/val/<class_a>/*.jpg
data_dir/val/<class_b>/*.jpg
```
works without touching `dataset.py` or `train.py` — `torchvision.datasets.ImageFolder`
infers classes from the folder names.

## Files

- `prepare_data.py` — downloads Dogs vs Cats via the Kaggle API and splits it into train/val folders
- `dataset.py` — `ImageFolder` loaders with real augmentation (crop, flip, color jitter, rotation)
- `train.py` — transfer-learning loop (frozen backbone + fine-tuned head), saves the best checkpoint by val accuracy
- `evaluate.py` — accuracy / precision / recall / F1 / confusion matrix / inference speed report
- `config.py` — default hyperparameters

Grad-CAM lives in `backend/app/ml_service.py` since it needs the model
loaded in the serving process — see that file for the implementation.
