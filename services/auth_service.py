"""Authentication service."""

import hashlib


class AuthService:
    """Handles credential verification for admin and voter logins."""

    def __init__(self, store):
        self.store = store

    @staticmethod
    def hash_password(password):
        """Return the SHA-256 hex digest of *password*."""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_admin(self, username, password):
        """
        Attempt to authenticate an admin.

        Returns a tuple ``(admin_obj, error_message)``.
        On success *error_message* is None; on failure *admin_obj* is None.
        """
        hashed = self.hash_password(password)
        for admin in self.store.admins.values():
            if admin.username == username and admin.password == hashed:
                if not admin.is_active:
                    return None, "This account has been deactivated."
                return admin, None
        return None, "Invalid credentials."

    def authenticate_voter(self, voter_card, password):
        """
        Attempt to authenticate a voter.

        Returns ``(voter_obj, error_message)``.
        """
        hashed = self.hash_password(password)
        for voter in self.store.voters.values():
            if voter.voter_card_number == voter_card and voter.password == hashed:
                if not voter.is_active:
                    return None, "This voter account has been deactivated."
                if not voter.is_verified:
                    return None, "NOT_VERIFIED"
                return voter, None
        return None, "Invalid voter card number or password."
