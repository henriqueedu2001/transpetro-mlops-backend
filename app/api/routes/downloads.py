from http import HTTPStatus
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.database.database_manager import Database, get_database
from app.database.repositories import Repository
from app.modules.zip import zip as create_zip

router = APIRouter()


def train_dir_for(train_id: int, db: Database) -> Path:
    try:
        return Path(Repository(db).get_dataset_dir(train_id)).parent
    except FileNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, str(error)) from error


@router.get("/downloads/model")
async def download_model(train_id: int, db: Database = Depends(get_database)):
    model = train_dir_for(train_id, db) / "weights" / "best.pt"
    if not model.is_file():
        raise HTTPException(HTTPStatus.NOT_FOUND, "modelo ainda não está disponível")
    return FileResponse(model, filename=f"train_{train_id}_best.pt")


@router.get("/downloads/zip")
async def download_zip(train_id: int, db: Database = Depends(get_database)):
    train_dir = train_dir_for(train_id, db)
    destination = train_dir.with_suffix(".zip")
    if not destination.is_file():
        create_zip(train_dir, destination)
    return FileResponse(destination, filename=f"train_{train_id}_output.zip")
