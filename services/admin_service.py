"""Admin account management service."""

import hashlib

from models.admin import Admin


class AdminService:
    """CRUD for admin accounts."""

    def __init__(self, store):
        self.store = store

    ROLE_MAP = {
        "1": "super_admin",
        "2": "election_officer",
        "3": "station_manager",
        "4": "auditor",
    }

    def get_all(self):
        return self.store.admins

    def get_by_id(self, admin_id):
        return self.store.admins.get(admin_id)

    def username_exists(self, username):
        return any(a.username == username for a in self.store.admins.values())

    def create(self, username, password, full_name, email, role):
        aid = self.store.admin_id_counter
        admin = Admin(
            admin_id=aid,
            username=username,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
            full_name=full_name,
            email=email,
            role=role,
        )
        self.store.admins[aid] = admin
        self.store.admin_id_counter += 1
        return admin

    def deactivate(self, admin_id):
        admin = self.store.admins.get(admin_id)
        if admin:
            admin.is_active = False
        return admin
