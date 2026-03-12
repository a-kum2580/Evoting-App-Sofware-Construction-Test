"""
JSON persistence layer.

Serialises / deserialises the DataStore to and from a JSON file.
"""

import json
import os

from config import DATA_FILE_PATH
from models.admin import Admin
from models.candidate import Candidate
from models.voter import Voter
from models.voting_station import VotingStation
from models.position import Position
from models.poll import Poll
from models.vote import Vote
from models.audit_entry import AuditEntry


def save_data(store):
    """Persist every registry in *store* to the JSON file."""
    data = {
        "candidates": {
            str(k): v.to_dict() for k, v in store.candidates.items()
        },
        "candidate_id_counter": store.candidate_id_counter,
        "voting_stations": {
            str(k): v.to_dict() for k, v in store.voting_stations.items()
        },
        "station_id_counter": store.station_id_counter,
        "polls": {
            str(k): v.to_dict() for k, v in store.polls.items()
        },
        "poll_id_counter": store.poll_id_counter,
        "positions": {
            str(k): v.to_dict() for k, v in store.positions.items()
        },
        "position_id_counter": store.position_id_counter,
        "voters": {
            str(k): v.to_dict() for k, v in store.voters.items()
        },
        "voter_id_counter": store.voter_id_counter,
        "admins": {
            str(k): v.to_dict() for k, v in store.admins.items()
        },
        "admin_id_counter": store.admin_id_counter,
        "votes": [v.to_dict() for v in store.votes],
        "audit_log": [e.to_dict() for e in store.audit_log],
    }
    try:
        with open(DATA_FILE_PATH, "w") as fh:
            json.dump(data, fh, indent=2)
    except Exception as exc:
        raise IOError(f"Error saving data: {exc}") from exc


def load_data(store):
    """Load persisted data from the JSON file into *store*."""
    if not os.path.exists(DATA_FILE_PATH):
        return

    try:
        with open(DATA_FILE_PATH, "r") as fh:
            data = json.load(fh)

        store.candidates = {
            int(k): Candidate.from_dict(v)
            for k, v in data.get("candidates", {}).items()
        }
        store.candidate_id_counter = data.get("candidate_id_counter", 1)

        store.voting_stations = {
            int(k): VotingStation.from_dict(v)
            for k, v in data.get("voting_stations", {}).items()
        }
        store.station_id_counter = data.get("station_id_counter", 1)

        store.polls = {
            int(k): Poll.from_dict(v)
            for k, v in data.get("polls", {}).items()
        }
        store.poll_id_counter = data.get("poll_id_counter", 1)

        store.positions = {
            int(k): Position.from_dict(v)
            for k, v in data.get("positions", {}).items()
        }
        store.position_id_counter = data.get("position_id_counter", 1)

        store.voters = {
            int(k): Voter.from_dict(v)
            for k, v in data.get("voters", {}).items()
        }
        store.voter_id_counter = data.get("voter_id_counter", 1)

        store.admins = {
            int(k): Admin.from_dict(v)
            for k, v in data.get("admins", {}).items()
        }
        store.admin_id_counter = data.get("admin_id_counter", 1)

        store.votes = [
            Vote.from_dict(v) for v in data.get("votes", [])
        ]
        store.audit_log = [
            AuditEntry.from_dict(e) for e in data.get("audit_log", [])
        ]
    except Exception as exc:
        raise IOError(f"Error loading data: {exc}") from exc
