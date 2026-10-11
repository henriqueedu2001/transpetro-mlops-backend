import sys
import unittest
from pathlib import Path


SCHEDULER_DIR = Path(__file__).resolve().parents[1] / "scheduler"
sys.path.insert(0, str(SCHEDULER_DIR))

from database.repositories import Repository  # noqa: E402


class FakeDatabase:
    def __init__(self, row=None):
        self.executed = []
        self.commits = 0
        self.row = row

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetch_all(self):
        return []

    def fetch_one(self):
        return self.row

    def commit(self):
        self.commits += 1


class SchedulerRepositoryTest(unittest.TestCase):
    def test_poll_ends_read_transaction(self):
        database = FakeDatabase()
        jobs = Repository(database).get_queued_jobs()
        self.assertEqual(jobs, [])
        self.assertEqual(database.commits, 1)

    def test_cancellation_check_ends_read_transaction(self):
        database = FakeDatabase({"cancel_requested": 1})

        requested = Repository(database).cancellation_requested(12)

        self.assertTrue(requested)
        self.assertEqual(database.commits, 1)


if __name__ == "__main__":
    unittest.main()
