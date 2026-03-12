"""Poll / Election domain model."""

import datetime


class Poll:
    """Represents an election or poll with one or more contested positions."""

    def __init__(self, poll_id, title, description, election_type,
                 start_date, end_date, positions=None, station_ids=None,
                 status="draft", total_votes_cast=0, created_at=None,
                 created_by=None):
        self.id = poll_id
        self.title = title
        self.description = description
        self.election_type = election_type
        self.start_date = start_date
        self.end_date = end_date
        self.positions = positions if positions is not None else []
        self.station_ids = station_ids if station_ids is not None else []
        self.status = status
        self.total_votes_cast = total_votes_cast
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by

    def is_open(self):
        return self.status == "open"

    def is_draft(self):
        return self.status == "draft"

    def is_closed(self):
        return self.status == "closed"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "election_type": self.election_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "positions": self.positions,
            "station_ids": self.station_ids,
            "status": self.status,
            "total_votes_cast": self.total_votes_cast,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            poll_id=data["id"],
            title=data["title"],
            description=data["description"],
            election_type=data["election_type"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            positions=data.get("positions", []),
            station_ids=data.get("station_ids", []),
            status=data.get("status", "draft"),
            total_votes_cast=data.get("total_votes_cast", 0),
            created_at=data.get("created_at"),
            created_by=data.get("created_by"),
        )
