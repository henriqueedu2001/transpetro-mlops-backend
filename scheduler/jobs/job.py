from datetime import datetime
from scheduler.jobs.job_status import *

class Job:
    def __init__(
        self,
        id: int,
        train_id: int,
        status: Status = Status.CREATED,
        created_at: datetime = None,
        scheduled_at: datetime = None,
        finished_at: datetime = None,
    ):
        self.id = id
        self.train_id = train_id
        self.status = status
        self.created_at = created_at
        self.scheduled_at = scheduled_at
        self.finished_at = finished_at
        pass