"""
DataStore — Central data persistence and session management layer.

This module replaces the 14+ global variables from the original monolith
with a single DataStore class that:
  1. Holds all entity collections (candidates, voters, polls, etc.)
  2. Manages auto-incrementing ID counters for each entity type
  3. Tracks the current logged-in user (session state)
  4. Handles JSON serialisation/deserialisation for persistence
  5. Records all actions to an audit log

The DataStore is injected into every Service via constructor injection
(Dependency Inversion Principle), ensuring services never depend on
global state.
"""

import datetime
import hashlib
import json
import os

from e_voting.constants import (
    DATA_FILE_PATH, ROLE_ADMIN, ROLE_VOTER,
    DEFAULT_ADMIN_ID, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_FULL_NAME, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_ROLE,
    INITIAL_ENTITY_ID, INITIAL_ADMIN_ID_COUNTER,
)
from e_voting.models.admin import Admin
from e_voting.models.candidate import Candidate
from e_voting.models.poll import Poll
from e_voting.models.position import Position
from e_voting.models.vote import Vote
from e_voting.models.voter import Voter
from e_voting.models.voting_station import VotingStation


class DataStore:
    """Central data persistence layer. Holds all entity collections,
    manages ID counters, session state, and JSON serialization."""

    def __init__(self):
        # Entity collections — keyed by integer ID for fast lookup
        self.candidates = {}        # int -> Candidate
        self.voters = {}            # int -> Voter
        self.admins = {}            # int -> Admin
        self.voting_stations = {}   # int -> VotingStation
        self.polls = {}             # int -> Poll
        self.positions = {}         # int -> Position
        self.votes = []             # List[Vote] — append-only log of all ballots
        self.audit_log = []         # List[dict] — timestamped action records

        self._id_counters = {
            "candidate": INITIAL_ENTITY_ID,
            "voter": INITIAL_ENTITY_ID,
            "admin": INITIAL_ADMIN_ID_COUNTER,
            "station": INITIAL_ENTITY_ID,
            "poll": INITIAL_ENTITY_ID,
            "position": INITIAL_ENTITY_ID,
        }

        # Session state — tracks who is currently logged in
        self.current_user = None    # Admin or Voter object (or None)
        self.current_role = None    # "admin" or "voter" (or None)

        self._init_default_admin()

    def _init_default_admin(self):
        """Create the built-in super_admin account (admin/admin123).
        This ensures the system is usable on first launch without
        needing a separate setup process."""
        default_admin = Admin(
            admin_id=DEFAULT_ADMIN_ID,
            username=DEFAULT_ADMIN_USERNAME,
            password=hashlib.sha256(
                DEFAULT_ADMIN_PASSWORD.encode()
            ).hexdigest(),
            full_name=DEFAULT_ADMIN_FULL_NAME,
            email=DEFAULT_ADMIN_EMAIL,
            role=DEFAULT_ADMIN_ROLE,
        )
        self.admins[DEFAULT_ADMIN_ID] = default_admin

    # ── ID Generation ────────────────────────────────────────

    def next_id(self, entity_type):
        """Return the next available ID for the given entity type
        and auto-increment the counter. Thread-safe is not required
        since this is a single-user console application."""
        current = self._id_counters[entity_type]
        self._id_counters[entity_type] = current + 1
        return current

    # ── Audit Logging ────────────────────────────────────────

    def log_action(self, action, user, details):
        """Append a timestamped record to the audit log.
        Every significant action (login, CRUD, voting) is recorded
        for accountability and reporting."""
        self.audit_log.append({
            "timestamp": str(datetime.datetime.now()),
            "action": action,
            "user": user,
            "details": details,
        })

    # ── Session Management ───────────────────────────────────

    def login(self, user, role):
        """Set the currently authenticated user and their role."""
        self.current_user = user
        self.current_role = role

    def logout(self):
        """Clear the session — called after the user logs out."""
        self.current_user = None
        self.current_role = None

    @property
    def is_logged_in(self):
        """Convenience check for whether someone is logged in."""
        return self.current_user is not None

    # ── Data Persistence (JSON) ──────────────────────────────

    def save(self):
        """Serialise all entity collections and counters to a JSON file.
        Each model's to_dict() method handles its own serialisation.
        Dict keys are converted to strings because JSON requires string keys."""
        data = {
            "candidates": {
                str(k): v.to_dict() for k, v in self.candidates.items()
            },
            "candidate_id_counter": self._id_counters["candidate"],
            "voting_stations": {
                str(k): v.to_dict() for k, v in self.voting_stations.items()
            },
            "station_id_counter": self._id_counters["station"],
            "polls": {
                str(k): v.to_dict() for k, v in self.polls.items()
            },
            "poll_id_counter": self._id_counters["poll"],
            "positions": {
                str(k): v.to_dict() for k, v in self.positions.items()
            },
            "position_id_counter": self._id_counters["position"],
            "voters": {
                str(k): v.to_dict() for k, v in self.voters.items()
            },
            "voter_id_counter": self._id_counters["voter"],
            "admins": {
                str(k): v.to_dict() for k, v in self.admins.items()
            },
            "admin_id_counter": self._id_counters["admin"],
            "votes": [v.to_dict() for v in self.votes],
            "audit_log": self.audit_log,
        }
        try:
            with open(DATA_FILE_PATH, "w") as file_handle:
                json_indent = 2
                json.dump(data, file_handle, indent=json_indent)
        except OSError as exc:
            raise IOError(f"Error saving data: {exc}") from exc

    def load(self):
        """Load all entity collections from the JSON file on disk.
        Each model's from_dict() class method reconstructs the object.
        JSON string keys are converted back to integers for in-memory use."""
        if not os.path.exists(DATA_FILE_PATH):
            return

        try:
            with open(DATA_FILE_PATH, "r") as file_handle:
                data = json.load(file_handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise IOError(f"Error loading data: {exc}") from exc

        # Reconstruct each entity collection from stored dictionaries
        self.candidates = {
            int(k): Candidate.from_dict(v)
            for k, v in data.get("candidates", {}).items()
        }
        self._id_counters["candidate"] = data.get(
            "candidate_id_counter", INITIAL_ENTITY_ID
        )

        self.voting_stations = {
            int(k): VotingStation.from_dict(v)
            for k, v in data.get("voting_stations", {}).items()
        }
        self._id_counters["station"] = data.get(
            "station_id_counter", INITIAL_ENTITY_ID
        )

        self.polls = {
            int(k): Poll.from_dict(v)
            for k, v in data.get("polls", {}).items()
        }
        self._id_counters["poll"] = data.get(
            "poll_id_counter", INITIAL_ENTITY_ID
        )

        self.positions = {
            int(k): Position.from_dict(v)
            for k, v in data.get("positions", {}).items()
        }
        self._id_counters["position"] = data.get(
            "position_id_counter", INITIAL_ENTITY_ID
        )

        self.voters = {
            int(k): Voter.from_dict(v)
            for k, v in data.get("voters", {}).items()
        }
        self._id_counters["voter"] = data.get(
            "voter_id_counter", INITIAL_ENTITY_ID
        )

        self.admins = {
            int(k): Admin.from_dict(v)
            for k, v in data.get("admins", {}).items()
        }
        self._id_counters["admin"] = data.get(
            "admin_id_counter", INITIAL_ENTITY_ID
        )

        self.votes = [
            Vote.from_dict(v) for v in data.get("votes", [])
        ]
        self.audit_log = data.get("audit_log", [])
