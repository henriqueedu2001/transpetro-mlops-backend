from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from app.database.database_manager import *
from app.database.repositories import *
from app.modules.file_handler import *
from app.modules.unzip import *
from app.modules.zip import *
import os

router = APIRouter()

@router.get("/downloads/model")
async def download_file(train_id: str, db: Database = Depends(get_database)):
    repo = Repository(db)

    try:
        dataset_dir = Path(repo.get_dataset_dir(train_id))
        best_model_path = dataset_dir.parent / 'weights' / 'best.pt'
    except Exception as error:
            raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(error))
    
    return FileResponse(path=best_model_path, filename=best_model_path.name)


@router.get("/downloads/zip")
async def download_file(train_id: str, db: Database = Depends(get_database)):
    repo = Repository(db)

    try:
        dataset_dir = Path(repo.get_dataset_dir(train_id))
        train_dir = dataset_dir.parent
    except Exception as error:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(error))

    source = train_dir
    destination = train_dir / f'{train_dir.name}.zip'    

    if os.path.isfile(destination):
        print('ZIP already exists')
    else:
        zip(source=source, destination=destination)
    
    return FileResponse(path=destination, filename=destination.name)