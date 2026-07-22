from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from app.database.database_manager import *
from app.database.repositories import *
from app.modules.file_handler import *
from app.modules.unzip import *

router = APIRouter()

@router.get("/downloads/model")
async def download_file(train_id: str, db: Database = Depends(get_database)):
    repo = Repository(db)

    dataset_dir = Path(repo.get_dataset_dir(train_id))
    best_model_path = dataset_dir.parent / 'weights' / 'best.pt'
    
    return FileResponse(path=best_model_path, filename=best_model_path.name)