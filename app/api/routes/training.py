from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Depends, Query
from pydantic import BaseModel, Field
from app.database.database_manager import *
from app.database.repositories import *
from app.modules.file_handler import *
from app.modules.unzip import *

router = APIRouter()

@router.post('/trainings/')
async def create_training(
    train_name: str = Form(...),
    project_name: str = Form(...),
    project_owner: str = Form(...),
    epochs: int = Form(...),
    batch: int = Form(...),
    workers: int = Form(...),
    file: UploadFile = File(None),
    db: Database = Depends(get_database)
):
    # registering in the database
    repo = Repository(db)
    train_id, dataset_path = repo.create_training(
        file=file,
        train_name=train_name,
        project_name=project_name,
        project_owner=project_owner,
        epochs=epochs,
        batch=batch,
        workers=workers
    )

    # saving the dataset .zip
    await save_dataset(file=file, train_id=train_id, project_name=project_name)

    # unzips it
    dataset_dir = dataset_path.parent
    print(f'zip_path: {dataset_path}\ndestination: {dataset_dir}')
    unzip(zip_path=dataset_path, destination=dataset_dir)
    
    return {'train_id': train_id, 'dataset_path': dataset_path}

@router.post('/datasets/upload')
async def upload_dataset(user_dataset: UploadFile = File(None)):
    if user_dataset:
        try:
            abs_path = await save_file(file=user_dataset)
            return abs_path
        except Exception as error:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='empty file')