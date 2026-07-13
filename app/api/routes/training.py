from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Depends, Query
from app.modules.file_handler import *

router = APIRouter()

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