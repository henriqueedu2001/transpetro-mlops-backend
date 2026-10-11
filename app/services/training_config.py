"""Validation and normalization for YOLO training requests."""

from __future__ import annotations

import re
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


MODEL_CATALOG = [
    {"id": "yolov8", "label": "YOLOv8", "sizes": ["n", "s", "m", "l", "x"]},
    {"id": "yolo11", "label": "YOLO11", "sizes": ["n", "s", "m", "l", "x"]},
    {"id": "yolo12", "label": "YOLO12", "sizes": ["n", "s", "m", "l", "x"]},
    {"id": "yolo26", "label": "YOLO26", "sizes": ["n", "s", "m", "l", "x"]},
]

MODEL_SIZES = {item["id"]: set(item["sizes"]) for item in MODEL_CATALOG}
OPTIMIZERS = {
    "auto": "auto",
    "sgd": "SGD",
    "adam": "Adam",
    "adamw": "AdamW",
    "nadam": "NAdam",
    "radam": "RAdam",
    "rmsprop": "RMSProp",
}
PROTECTED_YAML_KEYS = {
    "data", "model", "project", "name", "exist_ok", "save_dir", "resume",
}
EXTRA_YAML_KEYS = {
    "amp", "cache", "rect", "multi_scale", "single_cls", "fraction", "pretrained",
    "hsv_h", "hsv_s", "hsv_v", "degrees", "translate", "scale", "shear",
    "perspective", "flipud", "fliplr", "mosaic", "mixup", "copy_paste",
}
BOOLEAN_EXTRA_KEYS = {"amp", "cache", "rect", "multi_scale", "single_cls", "pretrained"}
UNIT_INTERVAL_EXTRA_KEYS = {
    "fraction", "hsv_h", "hsv_s", "hsv_v", "translate", "perspective",
    "flipud", "fliplr", "mosaic", "mixup", "copy_paste",
}
NON_NEGATIVE_EXTRA_KEYS = {"degrees", "scale", "shear"}


class TrainingConfig(BaseModel):
    """Complete set of user-controlled parameters for one training."""

    model_config = ConfigDict(extra="forbid")

    model_version: str = "yolov8"
    model_size: str = "n"
    epochs: int = Field(default=10, ge=1, le=10000)
    batch: int = Field(default=16, ge=1, le=1024)
    workers: int = Field(default=8, ge=0, le=128)
    imgsz: int = Field(default=640, ge=32, le=4096)
    patience: int = Field(default=100, ge=0, le=10000)
    optimizer: str = "auto"
    lr0: float = Field(default=0.01, gt=0, le=1)
    lrf: float = Field(default=0.01, ge=0, le=1)
    momentum: float = Field(default=0.937, ge=0, le=1)
    weight_decay: float = Field(default=0.0005, ge=0, le=1)
    warmup_epochs: float = Field(default=3.0, ge=0, le=1000)
    cos_lr: bool = False
    close_mosaic: int = Field(default=10, ge=0, le=10000)
    seed: int = Field(default=0, ge=0, le=2_147_483_647)
    deterministic: bool = True
    device: str = "0"

    @field_validator("model_version")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if value not in MODEL_SIZES:
            raise ValueError(f"modelo não suportado: {value}")
        return value

    @field_validator("model_size")
    @classmethod
    def validate_size(cls, value: str, info) -> str:
        version = info.data.get("model_version", "yolov8")
        if value not in MODEL_SIZES.get(version, set()):
            raise ValueError(f"tamanho {value} não suportado para {version}")
        return value

    @field_validator("optimizer")
    @classmethod
    def validate_optimizer(cls, value: str) -> str:
        canonical = OPTIMIZERS.get(value.strip().lower())
        if canonical is None:
            raise ValueError(f"otimizador não suportado: {value}")
        return canonical

    @field_validator("device")
    @classmethod
    def validate_device(cls, value: str) -> str:
        value = value.strip().lower()
        if value in {"cpu", "mps"} or re.fullmatch(r"\d+(,\d+)*", value):
            return value
        raise ValueError("device deve ser cpu, mps, um índice de GPU ou uma lista como 0,1")

    @property
    def checkpoint(self) -> str:
        return f"{self.model_version}{self.model_size}.pt"

    def to_training_dict(self) -> dict[str, Any]:
        values = self.model_dump(exclude={"model_version", "model_size"})
        values["model"] = self.checkpoint
        return values


def parse_args_yaml(content: bytes | None) -> dict[str, Any]:
    """Parse a small args.yaml and reject unknown or platform-owned options."""
    if not content:
        return {}
    if len(content) > 64 * 1024:
        raise ValueError("args.yaml excede o limite de 64 KiB")
    try:
        parsed = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise ValueError(f"args.yaml inválido: {error}") from error
    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise ValueError("args.yaml deve conter um mapa de chaves e valores")

    protected = sorted(set(parsed) & PROTECTED_YAML_KEYS)
    if protected:
        raise ValueError(f"args.yaml não pode alterar: {', '.join(protected)}")
    form_keys = set(TrainingConfig.model_fields)
    unknown = sorted(set(parsed) - form_keys - EXTRA_YAML_KEYS)
    if unknown:
        raise ValueError(f"parâmetros desconhecidos no args.yaml: {', '.join(unknown)}")
    for key in BOOLEAN_EXTRA_KEYS & set(parsed):
        if not isinstance(parsed[key], bool):
            raise ValueError(f"{key} deve ser true ou false")
    for key in UNIT_INTERVAL_EXTRA_KEYS & set(parsed):
        value = parsed[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"{key} deve ser um número entre 0 e 1")
    for key in NON_NEGATIVE_EXTRA_KEYS & set(parsed):
        value = parsed[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"{key} deve ser um número não negativo")
    return parsed


def build_training_config(form_values: dict[str, Any], yaml_content: bytes | None) -> tuple[TrainingConfig, dict[str, Any]]:
    """Merge form and YAML values; YAML has precedence for allowed keys."""
    yaml_values = parse_args_yaml(yaml_content)
    model_values = {**form_values, **{k: v for k, v in yaml_values.items() if k in TrainingConfig.model_fields}}
    config = TrainingConfig.model_validate(model_values)
    extras = {k: v for k, v in yaml_values.items() if k in EXTRA_YAML_KEYS}
    return config, extras
