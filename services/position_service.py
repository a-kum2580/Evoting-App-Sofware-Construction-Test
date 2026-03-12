"""Position management service."""

import datetime

from models.position import Position
from config import MIN_CANDIDATE_AGE


class PositionService:
    """CRUD operations for electable positions."""

    def __init__(self, store):
        self.store = store

    def get_all(self):
        return self.store.positions

    def get_active(self):
        return {pid: p for pid, p in self.store.positions.items() if p.is_active}

    def get_by_id(self, position_id):
        return self.store.positions.get(position_id)

    def create(self, title, description, level, max_winners,
               min_candidate_age=MIN_CANDIDATE_AGE, created_by=None):
        pid = self.store.position_id_counter
        position = Position(
            position_id=pid,
            title=title,
            description=description,
            level=level,
            max_winners=max_winners,
            min_candidate_age=min_candidate_age,
            created_by=created_by,
        )
        self.store.positions[pid] = position
        self.store.position_id_counter += 1
        return position

    def update(self, position_id, **fields):
        position = self.store.positions.get(position_id)
        if position is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(position, key):
                setattr(position, key, value)
        return position

    def deactivate(self, position_id):
        position = self.store.positions.get(position_id)
        if position:
            position.is_active = False
        return position

    def is_in_active_poll(self, position_id):
        """Return poll title if position is used in an open poll, else None."""
        for poll in self.store.polls.values():
            for pp in poll.positions:
                if pp["position_id"] == position_id and poll.status == "open":
                    return poll.title
        return None
