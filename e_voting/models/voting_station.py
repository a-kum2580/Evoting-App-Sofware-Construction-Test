"""
VotingStation model — Represents a physical voting location.

Each voting station has a maximum voter capacity, operating hours,
and a supervisor. Voters are assigned to exactly one station during
registration, and can only vote in polls that include their station.
"""

import datetime


class VotingStation:
    """Domain entity for a physical voting station.

    Attributes:
        id: Unique auto-incremented identifier.
        name: Human-readable station name (e.g. "Kampala Central").
        location: Street address or landmark description.
        region: Administrative region or district.
        capacity: Maximum number of voters the station can accommodate.
        is_active: Soft-delete flag — inactive stations cannot accept
                   new voter registrations.
    """

    def __init__(self, station_id, name, location, region, capacity,
                 registered_voters=0, supervisor="", contact="",
                 opening_time="", closing_time="",
                 is_active=True, created_at=None, created_by=None):
        self.id = station_id
        self.name = name
        self.location = location
        self.region = region
        self.capacity = capacity
        self.registered_voters = registered_voters
        self.supervisor = supervisor
        self.contact = contact
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.is_active = is_active
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by

    def deactivate(self):
        """Soft-delete: marks the station as inactive. Existing voters
        remain assigned but no new registrations are accepted."""
        self.is_active = False

    def to_dict(self):
        """Serialise to a plain dictionary for JSON persistence."""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "region": self.region,
            "capacity": self.capacity,
            "registered_voters": self.registered_voters,
            "supervisor": self.supervisor,
            "contact": self.contact,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a VotingStation instance from a stored dictionary."""
        return cls(
            station_id=data["id"],
            name=data["name"],
            location=data["location"],
            region=data["region"],
            capacity=data["capacity"],
            registered_voters=data.get("registered_voters", 0),
            supervisor=data.get("supervisor", ""),
            contact=data.get("contact", ""),
            opening_time=data.get("opening_time", ""),
            closing_time=data.get("closing_time", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            created_by=data.get("created_by"),
        )