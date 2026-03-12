"""Poll lifecycle management service."""

import datetime

from models.poll import Poll


class PollService:
    """CRUD, open/close lifecycle, and candidate assignment for polls."""

    def __init__(self, store):
        self.store = store

    def get_all(self):
        return self.store.polls

    def get_by_id(self, poll_id):
        return self.store.polls.get(poll_id)

    def get_open_polls(self):
        return {pid: p for pid, p in self.store.polls.items()
                if p.status == "open"}

    def get_closed_polls(self):
        return {pid: p for pid, p in self.store.polls.items()
                if p.status == "closed"}

    def create(self, title, description, election_type, start_date,
               end_date, poll_positions, station_ids, created_by):
        pid = self.store.poll_id_counter
        poll = Poll(
            poll_id=pid,
            title=title,
            description=description,
            election_type=election_type,
            start_date=start_date,
            end_date=end_date,
            positions=poll_positions,
            station_ids=station_ids,
            status="draft",
            created_by=created_by,
        )
        self.store.polls[pid] = poll
        self.store.poll_id_counter += 1
        return poll

    def update(self, poll_id, **fields):
        poll = self.store.polls.get(poll_id)
        if poll is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(poll, key):
                setattr(poll, key, value)
        return poll

    def delete(self, poll_id):
        """Permanently remove a poll and its associated votes."""
        if poll_id not in self.store.polls:
            return False
        del self.store.polls[poll_id]
        self.store.votes = [v for v in self.store.votes
                            if v.poll_id != poll_id]
        return True

    def open_poll(self, poll_id):
        poll = self.store.polls.get(poll_id)
        if poll:
            poll.status = "open"
        return poll

    def close_poll(self, poll_id):
        poll = self.store.polls.get(poll_id)
        if poll:
            poll.status = "closed"
        return poll

    def has_candidates_assigned(self, poll):
        """Return True if at least one position has candidates."""
        return any(pos.get("candidate_ids") for pos in poll.positions)

    @staticmethod
    def validate_dates(start_date, end_date):
        """
        Validate date strings.
        Returns (start_dt, end_dt, error).
        """
        try:
            sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if ed <= sd:
                return None, None, "End date must be after start date."
            return sd, ed, None
        except ValueError:
            return None, None, "Invalid date format."

    @staticmethod
    def validate_single_date(date_str):
        """Validate a single date string. Returns True on success."""
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
