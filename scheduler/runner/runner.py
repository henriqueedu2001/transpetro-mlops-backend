from jobs.job import Job
import subprocess
import time

class ReturnCode:
    SUCCESS = 0
    FAIL = 1

class Runner:
    def __init__(self, check_process_delay: float = 0.5):
        self.check_process_delay = check_process_delay
        pass


    def run(self, job: Job) -> int:
        cmd = [
            f'python3', 'trainer/main.py',
            f'{job.dataset_dir}',
            '--epochs', f'{job.epochs}',
            '--batch', f'{job.batch}',
            '--workers', f'{job.workers}'
        ]
        print(f'Running command: {cmd}')
        process = subprocess.Popen(cmd)

        while True:
            return_code = process.poll()
            if return_code is not None: return return_code
            else: time.sleep(self.check_process_delay)