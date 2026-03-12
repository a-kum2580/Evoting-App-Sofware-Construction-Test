"""
Central in-memory data store.

Replaces all global dictionaries and counters from the original monolith
with a single encapsulated object that can be injected into services.
"""

import datetime
import hashlib

from models.admin import Admin


class DataStore:
    """Holds every in-memory registry and ID counter for the application."""

    def __init__(self):
        self.candidates = {}
        self.candidate_id_counter = 1

        self.voting_stations = {}
        self.station_id_counter = 1

        self.polls = {}
        self.poll_id_counter = 1

        self.positions = {}
        self.position_id_counter = 1

        self.voters = {}
        self.voter_id_counter = 1

        self.admins = {}
        self.admin_id_counter = 1

        self.votes = []
        self.audit_log = []

        self.current_user = None
        self.current_role = None

        self._seed_default_admin()

    # ------------------------------------------------------------------
    # Bootstrap
    # ------------------------------------------------------------------
    def _seed_default_admin(self):
        """Create the built-in super-admin account."""
        default_admin = Admin(
            admin_id=1,
            username="admin",
            password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
            full_name="System Administrator",
            email="admin@evote.com",
            role="super_admin",
            created_at=str(datetime.datetime.now()),
            is_active=True,
        )
        self.admins[1] = default_admin
        self.admin_id_counter = 2
