from time import *
from datetime import datetime
from runner.runner import *
from jobs.job import *
from jobs.job_status import *
from database.database_manager import *
from database.repositories import *
from services.api import *

class Scheduler:
    def __init__(self, runner: Runner):
        self.running = False
        self.runner = runner
        self.db = Database()
        self.repository = Repository(self.db)
        pass

    
    def run(self):
        self.running = True

        while self.running:
            log_message('Retrieving active jobs...')
            jobs = self.retrieve_active_jobs()
            log_message(f'{len(jobs)} jobs found.')
            for index, job in enumerate(jobs): print(f'job #{index + 1}\n{job}')

            for job in jobs:
                log_message(f'Executing the job:\n{job}')
                self.execute_job(job)

            log_message('All jobs finished!')

        return

    def retrieve_active_jobs(self):
        sleep(1)
        jobs = self.repository.get_active_jobs()
        self.db.commit()
        jobs = [self._cast_job(job) for job in jobs] 
        
        return jobs
    

    def start_job(self, job: Job):
        REST_API.start_job(job_id=job.job_id)
        return
    

    def execute_job(self, job: Job):
        self.start_job(job)

        return_code = self.runner.run(job)
        if return_code == ReturnCode.SUCCESS:
            log_message(f'Job finalized with success.')
            self.finish_job(job)
        else:
            log_message(f'Job failed.')
        return
    

    def finish_job(self, job: Job):
        REST_API.finish_job(job_id=job.job_id)
        return
    

    def _cast_job(self, job: Dict) -> Job:
        return Job(
            job_id=job.get('id'),
            train_id=job.get('train_id'),
            status=job.get('status'),
            created_at=job.get('created_at'),
            scheduled_at=job.get('scheduled_at'),
            finished_at=job.get('finished_at'),
            dataset_dir=job.get('file_path'),
            epochs=job.get('epochs'),
            batch=job.get('batch'),
            workers=job.get('workers')
        )


def log_message(message: str):
    """Logs the message, by printing it with the current timestamp.

    Args:
        message (str): the log message
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def main():
    runner = Runner()
    scheduler = Scheduler(runner)
    scheduler.run()
    return

if __name__ == '__main__':
    main()