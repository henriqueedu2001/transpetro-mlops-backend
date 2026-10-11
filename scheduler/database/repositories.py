from database.database_manager import Database
from jobs.job_status import Status


class Repository:
    def __init__(self, db: Database):
        self.db = db

    def get_queued_jobs(self) -> list[dict]:
        self.db.execute(
            """
            SELECT jobs.id AS job_id, jobs.train_id, jobs.status, jobs.created_at,
                   jobs.scheduled_at, jobs.finished_at, jobs.log_path,
                   dataset.file_path AS dataset_dir,
                   config.file_path AS config_path
            FROM jobs
            INNER JOIN files dataset
                ON jobs.train_id=dataset.train_id AND dataset.file_type='dataset_dir'
            INNER JOIN files config
                ON jobs.train_id=config.train_id AND config.file_type='training_config'
            WHERE jobs.status=%s
            ORDER BY jobs.created_at
            """,
            (Status.QUEUED.value,),
        )
        jobs = self.db.fetch_all()
        # MySQL uses REPEATABLE READ by default. End the read transaction on
        # every poll so jobs created after the scheduler starts become visible.
        self.db.commit()
        return jobs

    def claim(self, job_id: int) -> bool:
        self.db.execute(
            """UPDATE jobs SET status=%s, scheduled_at=NOW(), finished_at=NULL,
               cancel_requested=FALSE, error_message=NULL
               WHERE id=%s AND status=%s""",
            (Status.RUNNING.value, job_id, Status.QUEUED.value),
        )
        claimed = self.db.cursor.rowcount == 1
        self.db.commit()
        return claimed

    def cancellation_requested(self, job_id: int) -> bool:
        self.db.execute("SELECT cancel_requested FROM jobs WHERE id=%s", (job_id,))
        row = self.db.fetch_one()
        # End the read transaction after every check. Under MySQL's default
        # REPEATABLE READ isolation, keeping it open would make every later
        # check reuse the snapshot from before the API requested cancellation.
        self.db.commit()
        return bool(row and row["cancel_requested"])

    def finish(self, job_id: int) -> None:
        self._finish(job_id, Status.SUCCEEDED)

    def fail(self, job_id: int, message: str) -> None:
        self._finish(job_id, Status.FAILED, message[:2000])

    def cancel(self, job_id: int) -> None:
        self._finish(job_id, Status.CANCELLED)

    def _finish(self, job_id: int, status: Status, error: str | None = None) -> None:
        self.db.execute(
            """UPDATE jobs SET status=%s, finished_at=NOW(),
               cancel_requested=FALSE, error_message=%s WHERE id=%s""",
            (status.value, error, job_id),
        )
        self.db.commit()
