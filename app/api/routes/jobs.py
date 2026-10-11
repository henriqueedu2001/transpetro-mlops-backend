from http import HTTPStatus
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from app.database.database_manager import Database, get_database
from app.database.repositories import Repository

router = APIRouter()
LOGGER = logging.getLogger("transpetro.api")


@router.get("/jobs/")
async def get_jobs(db: Database = Depends(get_database)):
    return Repository(db).get_jobs()


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: int, db: Database = Depends(get_database)):
    try:
        status = Repository(db).request_cancel(job_id)
    except RuntimeError as error:
        raise HTTPException(HTTPStatus.CONFLICT, str(error)) from error
    if status is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "job não encontrado")
    LOGGER.info("event=job_cancel_requested job_id=%s result=%s", job_id, status)
    return {"job_id": job_id, "status": status}


@router.post("/jobs/{job_id}/restart")
async def restart_job(job_id: int, db: Database = Depends(get_database)):
    try:
        status = Repository(db).restart_job(job_id)
    except RuntimeError as error:
        raise HTTPException(HTTPStatus.CONFLICT, str(error)) from error
    if status is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "job não encontrado")
    LOGGER.info("event=job_restarted job_id=%s", job_id)
    return {"job_id": job_id, "status": status}


@router.get("/jobs/{job_id}/logs", response_class=PlainTextResponse)
async def get_job_logs(job_id: int, db: Database = Depends(get_database)):
    job = Repository(db).get_job(job_id)
    if job is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "job não encontrado")
    log_path = job.get("log_path")
    if not log_path:
        return PlainTextResponse("Job legado: nenhum log foi registrado pela plataforma.\n")
    path = Path(log_path)
    if not path.is_file():
        return PlainTextResponse("O job ainda não produziu logs.\n")
    return PlainTextResponse(path.read_text(encoding="utf-8", errors="replace"))
