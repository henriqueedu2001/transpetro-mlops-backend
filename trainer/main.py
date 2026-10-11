import argparse
import json
from pathlib import Path

import yaml
from ultralytics import YOLO


def find_data_yaml(dataset_dir: Path) -> Path | None:
    candidates = sorted(dataset_dir.rglob("data.yaml")) + sorted(dataset_dir.rglob("data.yml"))
    return candidates[0] if candidates else None


def find_split(dataset_dir: Path, split: str) -> Path | None:
    candidates = [path for path in dataset_dir.rglob("images") if path.parent.name == split]
    return candidates[0] if candidates else None


def create_fallback_data_yaml(dataset_dir: Path, output_dir: Path) -> Path:
    train = find_split(dataset_dir, "train")
    val = find_split(dataset_dir, "val") or find_split(dataset_dir, "valid")
    if not train or not val:
        raise ValueError("dataset sem data.yaml e sem diretórios train/images e val/images")
    test = find_split(dataset_dir, "test")
    data = {
        "train": str(train),
        "val": str(val),
        "nc": 5,
        "names": ["Car", "Person", "Motorcycle", "Truck", "Animal"],
    }
    if test:
        data["test"] = str(test)
    path = output_dir / "data.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Transpetro MLOps YOLO trainer")
    parser.add_argument("dataset_dir", help="Diretório extraído do dataset")
    parser.add_argument("--config", required=True, help="Configuração efetiva em JSON")
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).resolve()
    config_path = Path(args.config).resolve()
    if not dataset_dir.is_dir():
        raise FileNotFoundError(f"diretório do dataset não encontrado: {dataset_dir}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    training_args = dict(config["arguments"])
    model_checkpoint = training_args.pop("model")
    # Release 1 originally persisted "Auto" while Ultralytics expects the
    # special automatic optimizer value in lowercase. Keep old jobs runnable.
    if str(training_args.get("optimizer", "")).lower() == "auto":
        training_args["optimizer"] = "auto"

    output_dir = dataset_dir.parent
    data_yaml = find_data_yaml(dataset_dir) or create_fallback_data_yaml(dataset_dir, output_dir)
    controlled_args = {
        "data": str(data_yaml),
        "project": str(output_dir.parent),
        "name": output_dir.name,
        "exist_ok": True,
        "verbose": True,
    }

    print("event=training_configuration")
    print(f"model={model_checkpoint}")
    print(f"dataset={data_yaml}")
    print(f"output={output_dir}")
    print(json.dumps(training_args, ensure_ascii=False, sort_keys=True))
    model = YOLO(model_checkpoint)
    model.train(**training_args, **controlled_args)
    print("event=training_finished")


if __name__ == "__main__":
    main()
