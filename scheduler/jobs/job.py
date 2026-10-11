from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jobs.job_status import Status


@dataclass
class Job:
    job_id: int
    train_id: int
    status: Status
    dataset_dir: Path
    config_path: Path
    log_path: Path
    created_at: datetime | None = None
    scheduled_at: datetime | None = None
    finished_at: datetime | None = None

    def __str__(self) -> str:
        return f"job={self.job_id} train={self.train_id} status={self.status} dataset={self.dataset_dir}"
