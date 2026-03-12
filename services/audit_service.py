"""Audit logging service."""

from models.audit_entry import AuditEntry


class AuditService:
    """Appends and retrieves entries in the audit log."""

    def __init__(self, store):
        self.store = store

    def log(self, action, user, details):
        """Record an action in the audit log."""
        entry = AuditEntry(action=action, user=user, details=details)
        self.store.audit_log.append(entry)

    def get_all(self):
        """Return every audit entry."""
        return self.store.audit_log

    def get_last_n(self, n):
        """Return the last *n* entries."""
        return self.store.audit_log[-n:]

    def filter_by_action(self, action_type):
        """Return entries matching a specific action type."""
        return [e for e in self.store.audit_log if e.action == action_type]

    def filter_by_user(self, user_fragment):
        """Return entries whose user field contains *user_fragment*."""
        fragment = user_fragment.lower()
        return [e for e in self.store.audit_log if fragment in e.user.lower()]

    def get_action_types(self):
        """Return a sorted unique list of action types present in the log."""
        return sorted(set(e.action for e in self.store.audit_log))
