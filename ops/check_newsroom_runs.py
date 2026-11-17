"""Check the most recent due newsroom slot using public Actions metadata."""
import json
import sys
from datetime import UTC, datetime, time, timedelta

SLOT = time(14, 29, tzinfo=UTC)
GRACE = timedelta(hours=1)


def timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC timestamp required")
    return datetime.fromisoformat(value)


def previous_slot(now):
    day = (now - GRACE).date()
    slot = datetime.combine(day, SLOT)
    if slot + GRACE > now:
        slot -= timedelta(days=1)
    while slot.weekday() >= 5:
        slot -= timedelta(days=1)
    return slot


def evaluate(payload, now):
    slot = previous_slot(now)
    next_slot = slot + timedelta(days=1)
    while next_slot.weekday() >= 5:
        next_slot += timedelta(days=1)
    runs = payload.get("workflow_runs")
    if not isinstance(runs, list) or payload.get("total_count") != len(runs):
        raise ValueError("Incomplete workflow-run response")
    candidates = [
        run for run in runs
        if run.get("event") == "schedule" and run.get("head_branch") == "main"
        and slot <= timestamp(run.get("created_at")) < next_slot
    ]
    label = slot.strftime("%Y-%m-%d %H:%M UTC")
    if len(candidates) != 1:
        return "error", f"{label}: expected one scheduled newsroom run, found {len(candidates)}."
    run = candidates[0]
    run_id = run.get("id")
    attempt = run.get("run_attempt")
    if type(run_id) is not int or run_id < 1 or type(attempt) is not int or attempt < 1:
        raise ValueError("Invalid run identifier or attempt")
    ref = f"{label}: newsroom run {run_id}, attempt {attempt}"
    if run.get("status") != "completed":
        return "warning", ref + " has not completed."
    if run.get("conclusion") != "success":
        return "error", ref + " did not succeed."
    started = timestamp(run.get("run_started_at"))
    if started < slot or started > now:
        raise ValueError("Invalid run start time")
    delay = started - slot
    minutes = int(delay.total_seconds() // 60)
    if attempt > 1:
        return "warning", ref + f" recovered on retry (start {minutes} minutes after slot)."
    if delay > GRACE:
        return "warning", ref + f" started {minutes} minutes after the slot."
    return "notice", ref + f" succeeded (start {minutes} minutes after slot)."


def main():
    try:
        level, message = evaluate(json.load(sys.stdin), datetime.now(UTC))
    except (ValueError, TypeError, AttributeError):
        level, message = "error", "Could not verify newsroom run metadata."
    print(f"::{level}::{message}")
    return int(level == "error")


if __name__ == "__main__":
    raise SystemExit(main())
