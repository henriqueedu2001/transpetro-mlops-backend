from pathlib import Path
from datetime import datetime
from jobs.job_status import *

class Job:
    def __init__(
        self,
        id: int,
        train_id: int,
        status: Status = Status.CREATED,
        created_at: datetime = None,
        scheduled_at: datetime = None,
        finished_at: datetime = None,
        dataset_dir: Path = None
    ):
        self.id = id
        self.train_id = train_id
        self.status = status
        self.created_at = created_at
        self.scheduled_at = scheduled_at
        self.finished_at = finished_at
        self.dataset_dir = dataset_dir
        pass


    def __str__(self):
        job_str = ''
        job_str += f'job_id: {self.id} | status: {self.status} | created_at: {self.created_at} | dataset_dir: {self.dataset_dir}'
        return job_str