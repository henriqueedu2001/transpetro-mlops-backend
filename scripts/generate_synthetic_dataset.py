"""Generate a small, deterministic YOLO dataset for timing smoke tests."""

from __future__ import annotations

import argparse
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw


IMAGE_SIZE = 640
JPEG_QUALITY = 90
SPLITS = {"train": 39, "val": 6, "test": 3}
CLASS_NAMES = ["Car", "Person", "Motorcycle", "Truck", "Animal"]


def make_example(rng: np.random.Generator, index: int) -> tuple[Image.Image, str]:
    pixels = rng.integers(0, 256, (IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
    image = Image.fromarray(pixels, mode="RGB")

    width = int(rng.integers(100, 260))
    height = int(rng.integers(100, 260))
    left = int(rng.integers(0, IMAGE_SIZE - width))
    top = int(rng.integers(0, IMAGE_SIZE - height))
    right = left + width
    bottom = top + height
    color = tuple(int(value) for value in rng.integers(32, 256, 3))
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=color)

    center_x = (left + right) / 2 / IMAGE_SIZE
    center_y = (top + bottom) / 2 / IMAGE_SIZE
    normalized_width = width / IMAGE_SIZE
    normalized_height = height / IMAGE_SIZE
    label = (
        f"{index % len(CLASS_NAMES)} {center_x:.6f} {center_y:.6f} "
        f"{normalized_width:.6f} {normalized_height:.6f}\n"
    )
    return image, label


def generate(output: Path, seed: int) -> Path:
    rng = np.random.default_rng(seed)
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="synthetic-yolo-") as temporary:
        dataset_root = Path(temporary) / "synthetic-noise-15mb"
        global_index = 0
        for split, count in SPLITS.items():
            image_dir = dataset_root / split / "images"
            label_dir = dataset_root / split / "labels"
            image_dir.mkdir(parents=True)
            label_dir.mkdir(parents=True)
            for local_index in range(count):
                image, label = make_example(rng, global_index)
                stem = f"noise_{split}_{local_index:03d}"
                image.save(
                    image_dir / f"{stem}.jpg",
                    format="JPEG",
                    quality=JPEG_QUALITY,
                    optimize=True,
                )
                (label_dir / f"{stem}.txt").write_text(label, encoding="utf-8")
                global_index += 1

        data = {
            "train": "train/images",
            "val": "val/images",
            "test": "test/images",
            "names": {index: name for index, name in enumerate(CLASS_NAMES)},
        }
        (dataset_root / "data.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        (dataset_root / "README.txt").write_text(
            "Dataset sintético determinístico para medir o tempo do pipeline.\n"
            "As imagens contêm ruído e um retângulo artificial; não servem para avaliar acurácia.\n",
            encoding="utf-8",
        )

        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
            for path in sorted(dataset_root.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(dataset_root.parent))

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("datasets/synthetic-noise-15mb.zip"),
    )
    parser.add_argument("--seed", type=int, default=20261007)
    args = parser.parse_args()
    output = generate(args.output, args.seed)
    print(f"created={output}")
    print(f"size_bytes={output.stat().st_size}")
    print(f"images={sum(SPLITS.values())}")


if __name__ == "__main__":
    main()
