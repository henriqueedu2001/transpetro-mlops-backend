import logging
import time
from pathlib import Path

from database.database_manager import Database
from database.repositories import Repository
from jobs.job import Job
from jobs.job_status import Status
from runner.runner import ReturnCode, Runner


def configure_logging() -> logging.Logger:
    log_dir = Path(__file__).resolve().parents[1] / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s level=%(levelname)s component=scheduler %(message)s",
        handlers=[logging.FileHandler(log_dir / "system.log"), logging.StreamHandler()],
    )
    return logging.getLogger("scheduler")


LOGGER = configure_logging()


class Scheduler:
    def __init__(self, runner: Runner, poll_delay: float = 1.0):
        self.runner = runner
        self.poll_delay = poll_delay
        self.db = Database()
        self.repository = Repository(self.db)
        self.running = False

    def run(self) -> None:
        self.running = True
        LOGGER.info("event=scheduler_started")
        while self.running:
            jobs = [self._cast_job(row) for row in self.repository.get_queued_jobs()]
            for job in jobs:
                if self.repository.claim(job.job_id):
                    self.execute_job(job)
            time.sleep(self.poll_delay)

    def execute_job(self, job: Job) -> None:
        LOGGER.info("event=job_started job_id=%s train_id=%s", job.job_id, job.train_id)
        try:
            code, error = self.runner.run(
                job, should_cancel=lambda: self.repository.cancellation_requested(job.job_id)
            )
            if code == ReturnCode.SUCCESS:
                self.repository.finish(job.job_id)
                LOGGER.info("event=job_succeeded job_id=%s", job.job_id)
            elif code == ReturnCode.CANCELLED:
                self.repository.cancel(job.job_id)
                LOGGER.info("event=job_cancelled job_id=%s", job.job_id)
            else:
                self.repository.fail(job.job_id, error or "falha desconhecida")
                LOGGER.error("event=job_failed job_id=%s error=%s", job.job_id, error)
        except Exception as error:
            self.repository.fail(job.job_id, str(error))
            LOGGER.exception("event=job_failed job_id=%s", job.job_id)

    @staticmethod
    def _cast_job(row: dict) -> Job:
        return Job(
            job_id=row["job_id"], train_id=row["train_id"], status=Status(row["status"]),
            created_at=row["created_at"], scheduled_at=row["scheduled_at"],
            finished_at=row["finished_at"], dataset_dir=Path(row["dataset_dir"]),
            config_path=Path(row["config_path"]), log_path=Path(row["log_path"]),
        )


def main() -> None:
    scheduler = Scheduler(Runner())
    try:
        scheduler.run()
    except KeyboardInterrupt:
        LOGGER.info("event=scheduler_stopped")
    finally:
        scheduler.db.close()


if __name__ == "__main__":
    main()
