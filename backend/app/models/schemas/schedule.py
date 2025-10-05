import datetime
import json

class Schedule:
    def __init__(self, workflow_id, next_run, interval_seconds=None, until=None, max_occurrences=None, occurrences=0, context=None):
        self.workflow_id = workflow_id
        self.next_run = next_run
        self.interval_seconds = interval_seconds
        self.until = until
        self.max_occurrences = max_occurrences
        self.occurrences = occurrences
        self.context = context or {}

    def to_dict(self):
        return {
            "workflow_id": self.workflow_id,
            "next_run": self.next_run.isoformat(),
            "interval_seconds": self.interval_seconds,
            "until": self.until,
            "max_occurrences": self.max_occurrences,
            "occurrences": self.occurrences,
            "context": self.context
        }

    @staticmethod
    def from_dict(data):
        return Schedule(
            workflow_id=data["workflow_id"],
            next_run=datetime.datetime.fromisoformat(data["next_run"]),
            interval_seconds=data.get("interval_seconds"),
            until=data.get("until"),
            max_occurrences=data.get("max_occurrences"),
            occurrences=data.get("occurrences", 0),
            context=data.get("context")
        )
