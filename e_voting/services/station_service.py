"""
StationService — Business logic for voting station management.

Handles station creation, retrieval, updates, soft-deletion, and
counting registered voters per station. Stations are fundamental to
the system because voters are assigned to a station at registration
and can only vote in polls that include their station.
"""

from e_voting.models.voting_station import VotingStation


class StationService:
    """Business logic for voting station management."""

    def __init__(self, store):
        self._store = store

    def create(self, name, location, region, capacity, supervisor, contact,
               opening_time, closing_time, created_by):
        """Create a new voting station, persist it, and log the action.
        Returns the created VotingStation object."""
        station_id = self._store.next_id("station")
        station = VotingStation(
            station_id=station_id,
            name=name,
            location=location,
            region=region,
            capacity=capacity,
            supervisor=supervisor,
            contact=contact,
            opening_time=opening_time,
            closing_time=closing_time,
            created_by=created_by,
        )
        self._store.voting_stations[station_id] = station
        self._store.log_action(
            "CREATE_STATION", created_by,
            f"Created station: {name} (ID: {station_id})"
        )
        self._store.save()
        return station

    def get_all(self):
        """Return the full dictionary of all stations."""
        return self._store.voting_stations

    def get(self, station_id):
        """Look up a single station by ID. Returns None if not found."""
        return self._store.voting_stations.get(station_id)

    def get_active(self):
        """Return only stations that are currently active.
        Used when presenting station choices to voters during registration."""
        return {
            sid: s for sid, s in self._store.voting_stations.items()
            if s.is_active
        }

    def get_registered_voter_count(self, station_id):
        """Count how many voters are registered at the given station.
        Computed dynamically from the voter collection rather than
        storing a denormalised counter (avoids stale data)."""
        return sum(
            1 for v in self._store.voters.values()
            if v.station_id == station_id
        )

    def update(self, station_id, updates, updated_by):
        """Apply a dictionary of field updates to a station.
        Returns the updated station, or None if not found."""
        station = self._store.voting_stations.get(station_id)
        if not station:
            return None
        for key, value in updates.items():
            if value is not None and hasattr(station, key):
                setattr(station, key, value)
        self._store.log_action(
            "UPDATE_STATION", updated_by,
            f"Updated station: {station.name} (ID: {station_id})"
        )
        self._store.save()
        return station

    def deactivate(self, station_id, deactivated_by):
        """Soft-delete a station. Existing voters remain assigned
        but no new registrations are accepted."""
        station = self._store.voting_stations.get(station_id)
        if not station:
            return False
        station.deactivate()
        self._store.log_action(
            "DELETE_STATION", deactivated_by,
            f"Deactivated station: {station.name}"
        )
        self._store.save()
        return True
