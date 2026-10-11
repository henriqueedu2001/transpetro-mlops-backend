import os
import signal
import subprocess
import sys
import time
from enum import IntEnum
from pathlib import Path
from typing import Callable

from jobs.job import Job


class ReturnCode(IntEnum):
    SUCCESS = 0
    FAIL = 1
    CANCELLED = 130


class Runner:
    def __init__(self, check_process_delay: float = 0.5):
        self.check_process_delay = check_process_delay
        self.repository_root = Path(__file__).resolve().parents[2]

    def run(self, job: Job, should_cancel: Callable[[], bool]) -> tuple[ReturnCode, str | None]:
        command = [
            sys.executable,
            str(self.repository_root / "trainer" / "main.py"),
            str(job.dataset_dir),
            "--config",
            str(job.config_path),
        ]
        job.log_path.parent.mkdir(parents=True, exist_ok=True)
        with job.log_path.open("a", encoding="utf-8") as log:
            log.write(f"\n=== execução do job {job.job_id} ===\n")
            log.write(f"comando: {' '.join(command)}\n")
            log.flush()
            process = subprocess.Popen(
                command,
                cwd=self.repository_root,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
            while process.poll() is None:
                if should_cancel():
                    self._terminate(process)
                    log.write("job cancelado por solicitação do usuário\n")
                    return ReturnCode.CANCELLED, None
                time.sleep(self.check_process_delay)

            if process.returncode == 0:
                return ReturnCode.SUCCESS, None
            return ReturnCode.FAIL, f"treinador finalizou com código {process.returncode}"

    @staticmethod
    def _terminate(process: subprocess.Popen) -> None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
