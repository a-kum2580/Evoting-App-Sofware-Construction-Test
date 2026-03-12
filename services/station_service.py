"""Voting station management service."""

import datetime

from models.voting_station import VotingStation


class StationService:
    """CRUD operations for voting stations."""

    def __init__(self, store):
        self.store = store

    def get_all(self):
        return self.store.voting_stations

    def get_active(self):
        return {sid: s for sid, s in self.store.voting_stations.items()
                if s.is_active}

    def get_by_id(self, station_id):
        return self.store.voting_stations.get(station_id)

    def count_registered_voters(self, station_id):
        return sum(
            1 for v in self.store.voters.values()
            if v.station_id == station_id
        )

    def create(self, name, location, region, capacity, supervisor,
               contact, opening_time, closing_time, created_by):
        sid = self.store.station_id_counter
        station = VotingStation(
            station_id=sid,
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
        self.store.voting_stations[sid] = station
        self.store.station_id_counter += 1
        return station

    def update(self, station_id, **fields):
        station = self.store.voting_stations.get(station_id)
        if station is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(station, key):
                setattr(station, key, value)
        return station

    def deactivate(self, station_id):
        station = self.store.voting_stations.get(station_id)
        if station:
            station.is_active = False
        return station
