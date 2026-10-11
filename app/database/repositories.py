import json
from pathlib import Path
from typing import Any

from app.database.database_manager import Database
from app.modules.file_handler import get_dataset_dir, get_dataset_zip_path, get_train_dir
from app.schemas.jobs import JobStatus, RESTARTABLE_STATUSES


class Repository:
    def __init__(self, db: Database):
        self.db = db

    def create_training(
        self,
        train_name: str,
        project_name: str,
        project_owner: str,
        config: dict[str, Any],
    ) -> tuple[int, dict[str, Path]]:
        self.db.execute(
            "INSERT INTO train(train_name, project_name, project_owner) VALUES(%s, %s, %s)",
            (train_name, project_name, project_owner),
        )
        train_id = self.db.cursor.lastrowid

        self.db.execute(
            """
            INSERT INTO params(id, epochs, batch, workers, model_version, model_size, config_json)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                train_id,
                config["arguments"]["epochs"],
                config["arguments"]["batch"],
                config["arguments"]["workers"],
                config["model_version"],
                config["model_size"],
                json.dumps(config, ensure_ascii=False),
            ),
        )

        train_dir = get_train_dir(train_id, project_name)
        paths = {
            "train_dir": train_dir,
            "dataset_dir": get_dataset_dir(train_id, project_name),
            "dataset_zip": get_dataset_zip_path(train_id, project_name),
            "training_config": train_dir / "training_config.json",
            "job_log": train_dir / "job.log",
        }
        self.db.execute(
            "INSERT INTO jobs(train_id, status, log_path) VALUES(%s, %s, %s)",
            (train_id, JobStatus.QUEUED.value, str(paths["job_log"])),
        )
        self.db.execute_many(
            "INSERT INTO files(train_id, file_type, file_path) VALUES(%s, %s, %s)",
            [(train_id, kind, str(path)) for kind, path in paths.items() if kind != "job_log"],
        )
        return train_id, paths

    def get_jobs(self) -> list[dict]:
        self.db.execute(
            """
            SELECT jobs.id, jobs.train_id, jobs.status, jobs.created_at,
                   jobs.scheduled_at, jobs.finished_at, jobs.cancel_requested,
                   jobs.error_message, jobs.retry_count,
                   train.train_name, train.project_name, train.project_owner,
                   params.model_version, params.model_size, params.epochs,
                   params.batch, params.workers,
                   EXISTS(
                       SELECT 1 FROM files configuration
                       WHERE configuration.train_id=jobs.train_id
                         AND configuration.file_type='training_config'
                   ) AS config_ready
            FROM jobs
            INNER JOIN train ON jobs.train_id = train.id
            INNER JOIN params ON jobs.train_id = params.id
            ORDER BY jobs.created_at DESC
            """
        )
        return self.db.fetch_all()

    def get_job(self, job_id: int) -> dict | None:
        self.db.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        return self.db.fetch_one()

    def request_cancel(self, job_id: int) -> str | None:
        job = self.get_job(job_id)
        if not job:
            return None
        status = job["status"]
        if status == JobStatus.QUEUED.value:
            self.db.execute(
                """UPDATE jobs SET status=%s, cancel_requested=FALSE,
                   finished_at=NOW(), error_message=NULL WHERE id=%s""",
                (JobStatus.CANCELLED.value, job_id),
            )
        elif status == JobStatus.RUNNING.value:
            self.db.execute("UPDATE jobs SET cancel_requested=TRUE WHERE id=%s", (job_id,))
        else:
            raise RuntimeError(f"job em estado {status} não pode ser cancelado")
        self.db.commit()
        return JobStatus.CANCELLED.value if status == JobStatus.QUEUED.value else "cancellation_requested"

    def restart_job(self, job_id: int) -> str | None:
        job = self.get_job(job_id)
        if not job:
            return None
        self.db.execute(
            """SELECT 1 FROM files WHERE train_id=%s AND file_type='training_config'""",
            (job["train_id"],),
        )
        if not self.db.fetch_one():
            raise RuntimeError("job legado sem configuração efetiva; crie um novo treinamento")
        if JobStatus(job["status"]) not in RESTARTABLE_STATUSES:
            raise RuntimeError(f"job em estado {job['status']} não pode ser reiniciado")
        self.db.execute(
            """
            UPDATE jobs
            SET status=%s, scheduled_at=NULL, finished_at=NULL,
                cancel_requested=FALSE, error_message=NULL, retry_count=retry_count + 1
            WHERE id=%s
            """,
            (JobStatus.QUEUED.value, job_id),
        )
        self.db.commit()
        return JobStatus.QUEUED.value

    def get_dataset_dir(self, train_id: int) -> str:
        self.db.execute(
            "SELECT file_path FROM files WHERE file_type='dataset_dir' AND train_id=%s",
            (train_id,),
        )
        row = self.db.fetch_one()
        if not row:
            raise FileNotFoundError(f"dataset do treinamento {train_id} não encontrado")
        return row["file_path"]

    def get_job_log_path(self, job_id: int) -> str | None:
        self.db.execute("SELECT log_path FROM jobs WHERE id=%s", (job_id,))
        row = self.db.fetch_one()
        return row["log_path"] if row else None
