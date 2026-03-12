"""Admin domain model."""

import datetime
import hashlib


class Admin:
    """Represents an administrator account in the E-Voting system."""

    VALID_ROLES = ("super_admin", "election_officer", "station_manager", "auditor")

    def __init__(self, admin_id, username, password_hash, full_name,
                 email, role, created_at=None, is_active=True):
        self.id = admin_id
        self.username = username
        self.password = password_hash
        self.full_name = full_name
        self.email = email
        self.role = role
        self.created_at = created_at or str(datetime.datetime.now())
        self.is_active = is_active

    def check_password(self, password):
        """Return True if the plain-text password matches the stored hash."""
        return hashlib.sha256(password.encode()).hexdigest() == self.password

    def is_super_admin(self):
        """Return True if this admin has the super_admin role."""
        return self.role == "super_admin"

    def to_dict(self):
        """Serialise to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialise from a dictionary."""
        return cls(
            admin_id=data["id"],
            username=data["username"],
            password_hash=data["password"],
            full_name=data["full_name"],
            email=data["email"],
            role=data["role"],
            created_at=data.get("created_at"),
            is_active=data.get("is_active", True),
        )
