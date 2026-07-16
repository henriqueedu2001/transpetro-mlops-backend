from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Depends, Query
from app.modules.file_handler import *

router = APIRouter()

@router.get('/jobs/')
async def get_jobs():
    job_1 = {
        'id': 1,
        'train_id': 77,
        'status': 'created',
        'created_at': datetime(year=2026, month=7, day=14, hour=12),
        'scheduled_at': datetime(year=2026, month=7, day=14, hour=13),
        'finished_at': datetime(year=2026, month=7, day=14, hour=14)
    }
    job_2 = {
        'id': 2,
        'train_id': 88,
        'status': 'processing',
        'created_at': datetime(year=2026, month=7, day=14, hour=12),
        'scheduled_at': datetime(year=2026, month=7, day=14, hour=13),
        'finished_at': datetime(year=2026, month=7, day=14, hour=14)
    }
    job_3 = {
        'id': 3,
        'train_id': 99,
        'status': 'finished',
        'created_at': datetime(year=2026, month=7, day=14, hour=12),
        'scheduled_at': datetime(year=2026, month=7, day=14, hour=13),
        'finished_at': datetime(year=2026, month=7, day=14, hour=14)
    }
    job_4 = {
        'id': 4,
        'train_id': 99,
        'status': 'cancelled',
        'created_at': datetime(year=2026, month=7, day=14, hour=12),
        'scheduled_at': datetime(year=2026, month=7, day=14, hour=13),
        'finished_at': datetime(year=2026, month=7, day=14, hour=14)
    }
    return [job_1, job_2, job_3, job_4]