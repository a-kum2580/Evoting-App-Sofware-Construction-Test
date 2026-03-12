"""AuditEntry domain model."""

import datetime


class AuditEntry:
    """Represents a single audit-log record."""

    def __init__(self, action, user, details, timestamp=None):
        self.timestamp = timestamp or str(datetime.datetime.now())
        self.action = action
        self.user = user
        self.details = details

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "user": self.user,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            action=data["action"],
            user=data["user"],
            details=data["details"],
            timestamp=data.get("timestamp"),
        )
