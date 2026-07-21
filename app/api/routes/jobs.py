from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Depends, Query
from app.database.database_manager import *
from app.modules.file_handler import *
from app.database.repositories import *

router = APIRouter()

@router.get('/jobs/')
async def get_jobs(db: Database = Depends(get_database)):
    repo = Repository(db)
    jobs = repo.get_jobs()
    return jobs


@router.post('/jobs/start')
async def finish_job(job_id: int, db: Database = Depends(get_database)):
    repo = Repository(db)
    repo.start_job(job_id)


@router.post('/jobs/finish')
async def finish_job(job_id: int, db: Database = Depends(get_database)):
    repo = Repository(db)
    repo.finish_job(job_id)