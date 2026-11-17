import unittest
from datetime import datetime

from check_newsroom_runs import evaluate, previous_slot


def at(value):
    return datetime.fromisoformat(value)


NOW = at("2026-11-17T23:15:00Z")
RUN = dict(event="schedule", head_branch="main", id=44191344614, run_attempt=1,
           status="completed", conclusion="success", created_at="2026-11-17T22:34:20Z",
           run_started_at="2026-11-17T22:34:20Z")


def assess(*runs):
    return evaluate(dict(workflow_runs=list(runs), total_count=len(runs)), NOW)


class NewsroomCheckTests(unittest.TestCase):
    def test_known_late_run(self):
        level, message = assess(RUN)
        self.assertEqual(level, "warning")
        self.assertIn("485 minutes", message)

    def test_missing_slot_does_not_credit_push(self):
        self.assertEqual(assess(dict(RUN, event="push"))[0], "error")

    def test_duplicate_runs(self):
        self.assertEqual(assess(RUN, dict(RUN, id=2))[0], "error")

    def test_queued_failed_and_recovered(self):
        self.assertEqual(assess(dict(RUN, status="queued"))[0], "warning")
        self.assertEqual(assess(dict(RUN, conclusion="failure"))[0], "error")
        self.assertIn("recovered on retry", assess(dict(RUN, run_attempt=2))[1])

    def test_on_time_and_previous_weekday(self):
        self.assertEqual(assess(dict(RUN, run_started_at="2026-11-17T14:39:00Z",
                                     created_at="2026-11-17T14:39:00Z"))[0], "notice")
        self.assertEqual(previous_slot(at("2026-11-23T15:28:00Z")),
                         at("2026-11-20T14:29:00Z"))

    def test_incomplete_results_stop(self):
        with self.assertRaises(ValueError):
            evaluate(dict(workflow_runs=[RUN], total_count=2), NOW)
