from dataclasses import dataclass


@dataclass
class TrainConfig:
    model_name: str = "mobilenet_v3"       # resnet50 | efficientnet_b3 | mobilenet_v3
    data_dir: str = "./data/dogs-vs-cats"  # expects data_dir/train/cat, data_dir/train/dog, data_dir/val/cat, data_dir/val/dog
    output_dir: str = "./ml_models"
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 1e-4
    image_size: int = 224
    num_workers: int = 2
    val_split: float = 0.15
    seed: int = 42
