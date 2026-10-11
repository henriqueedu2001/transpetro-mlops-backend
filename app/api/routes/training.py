import json
import logging
import shutil
from http import HTTPStatus

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app.database.database_manager import Database, get_database
from app.database.repositories import Repository
from app.modules.file_handler import save_dataset, save_file
from app.modules.unzip import unzip
from app.services.training_config import MODEL_CATALOG, build_training_config

router = APIRouter()
LOGGER = logging.getLogger("transpetro.api")


@router.get("/models")
async def get_models():
    return {"models": MODEL_CATALOG}


@router.post("/trainings/", status_code=HTTPStatus.CREATED)
async def create_training(
    train_name: str = Form(..., min_length=1, max_length=255),
    project_name: str = Form(..., min_length=1, max_length=255),
    project_owner: str = Form(..., min_length=1, max_length=255),
    model_version: str = Form("yolov8"),
    model_size: str = Form("n"),
    epochs: int = Form(10),
    batch: int = Form(16),
    workers: int = Form(8),
    imgsz: int = Form(640),
    patience: int = Form(100),
    optimizer: str = Form("auto"),
    lr0: float = Form(0.01),
    lrf: float = Form(0.01),
    momentum: float = Form(0.937),
    weight_decay: float = Form(0.0005),
    warmup_epochs: float = Form(3.0),
    cos_lr: bool = Form(False),
    close_mosaic: int = Form(10),
    seed: int = Form(0),
    deterministic: bool = Form(True),
    device: str = Form("0"),
    file: UploadFile = File(...),
    args_yaml: UploadFile | None = File(None),
    db: Database = Depends(get_database),
):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, "o dataset deve ser um arquivo .zip")
    if args_yaml and args_yaml.filename and not args_yaml.filename.lower().endswith(('.yaml', '.yml')):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, "os argumentos devem estar em um arquivo .yaml ou .yml")

    yaml_content = await args_yaml.read() if args_yaml else None
    if args_yaml:
        await args_yaml.close()
    form_values = {
        "model_version": model_version, "model_size": model_size,
        "epochs": epochs, "batch": batch, "workers": workers, "imgsz": imgsz,
        "patience": patience, "optimizer": optimizer, "lr0": lr0, "lrf": lrf,
        "momentum": momentum, "weight_decay": weight_decay,
        "warmup_epochs": warmup_epochs, "cos_lr": cos_lr,
        "close_mosaic": close_mosaic, "seed": seed,
        "deterministic": deterministic, "device": device,
    }
    try:
        config, yaml_extras = build_training_config(form_values, yaml_content)
    except (ValueError, ValidationError) as error:
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, str(error)) from error

    effective_config = {
        "model_version": config.model_version,
        "model_size": config.model_size,
        "arguments": {**config.to_training_dict(), **yaml_extras},
    }
    repo = Repository(db)
    train_dir = None
    try:
        train_id, paths = repo.create_training(
            train_name=train_name.strip(),
            project_name=project_name.strip(),
            project_owner=project_owner.strip(),
            config=effective_config,
        )
        train_dir = paths["train_dir"]
        dataset_zip = await save_dataset(file, train_id, project_name)
        paths["dataset_dir"].mkdir(parents=True, exist_ok=True)
        unzip(dataset_zip, paths["dataset_dir"])
        paths["training_config"].write_text(
            json.dumps(effective_config, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        if yaml_content:
            (train_dir / "args.yaml").write_bytes(yaml_content)
        db.commit()
        LOGGER.info(
            "event=training_created train_id=%s model=%s owner=%s",
            train_id, config.checkpoint, project_owner.strip(),
        )
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        if train_dir and train_dir.exists():
            shutil.rmtree(train_dir)
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, f"não foi possível criar o treinamento: {error}") from error

    return {
        "train_id": train_id,
        "status": "queued",
        "model": config.checkpoint,
        "configuration": effective_config,
    }


@router.post("/datasets/upload")
async def upload_dataset(user_dataset: UploadFile = File(...)):
    try:
        path = await save_file(file=user_dataset)
        return {"path": str(path)}
    except Exception as error:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, str(error)) from error
