"""
AuthService — Handles authentication and voter self-registration.

This service encapsulates all login/registration logic that was
previously mixed into the UI functions. It handles:
  - Password hashing (SHA-256)
  - Admin credential verification
  - Voter credential verification (with active/verified checks)
  - Voter registration field validation
  - New voter account creation with auto-generated card numbers

The service never prints or reads input — it returns results/errors
that the UI layer displays to the user (Separation of Concerns).
"""

import datetime
import hashlib
import random
import string

from e_voting.constants import (
    MIN_VOTER_AGE, MIN_PASSWORD_LENGTH, VALID_GENDERS, VOTER_CARD_LENGTH,
)
from e_voting.models.voter import Voter


class AuthService:
    """Handles authentication and voter self-registration."""

    def __init__(self, store):
        self._store = store

    @staticmethod
    def hash_password(password):
        """One-way SHA-256 hash — passwords are never stored in plain text."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_voter_card_number():
        """Generate a random 12-character alphanumeric voter card number.
        This serves as the voter's unique login credential."""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=VOTER_CARD_LENGTH))

    def authenticate_admin(self, username, password):
        """Verify admin credentials against stored hashed passwords.
        Returns (admin, None) on success or (None, error_message) on failure.
        Also checks that the account is not deactivated."""
        hashed = self.hash_password(password)
        for admin in self._store.admins.values():
            if admin.username == username and admin.password == hashed:
                if not admin.is_active:
                    self._store.log_action(
                        "LOGIN_FAILED", username, "Account deactivated"
                    )
                    return None, "This account has been deactivated."
                self._store.log_action(
                    "LOGIN", username, "Admin login successful"
                )
                return admin, None
        self._store.log_action(
            "LOGIN_FAILED", username, "Invalid admin credentials"
        )
        return None, "Invalid credentials."

    def authenticate_voter(self, voter_card, password):
        """Verify voter credentials using their card number and password.
        Returns (voter, None) on success or (None, error_message) on failure.
        Returns special sentinel "NOT_VERIFIED" so the UI can show a
        different message for unverified vs invalid credentials."""
        hashed = self.hash_password(password)
        for voter in self._store.voters.values():
            if (voter.voter_card_number == voter_card
                    and voter.password == hashed):
                if not voter.is_active:
                    self._store.log_action(
                        "LOGIN_FAILED", voter_card,
                        "Voter account deactivated"
                    )
                    return None, "This voter account has been deactivated."
                if not voter.is_verified:
                    self._store.log_action(
                        "LOGIN_FAILED", voter_card, "Voter not verified"
                    )
                    return None, "NOT_VERIFIED"
                self._store.log_action(
                    "LOGIN", voter_card, "Voter login successful"
                )
                return voter, None
        self._store.log_action(
            "LOGIN_FAILED", voter_card, "Invalid voter credentials"
        )
        return None, "Invalid voter card number or password."

    def validate_voter_registration(self, full_name, national_id, dob_str,
                                    gender, password, confirm_password):
        """Run all validation checks on voter registration fields.
        Returns None if all checks pass, or an error message string
        describing the first validation failure found."""
        if not full_name:
            return "Name cannot be empty."
        if not national_id:
            return "National ID cannot be empty."
        # Ensure no duplicate National IDs
        for voter in self._store.voters.values():
            if voter.national_id == national_id:
                return "A voter with this National ID already exists."
        # Age check — must be at least MIN_VOTER_AGE
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
            if age < MIN_VOTER_AGE:
                return (f"You must be at least {MIN_VOTER_AGE} years old "
                        "to register.")
        except ValueError:
            return "Invalid date format."
        if gender not in VALID_GENDERS:
            return "Invalid gender selection."
        if len(password) < MIN_PASSWORD_LENGTH:
            return (f"Password must be at least "
                    f"{MIN_PASSWORD_LENGTH} characters.")
        if password != confirm_password:
            return "Passwords do not match."
        # Must have at least one station for the voter to be assigned to
        if not self._store.voting_stations:
            return "No voting stations available. Contact admin."
        return None

    def register_voter(self, full_name, national_id, dob_str, gender,
                       address, phone, email, password, station_id):
        """Create a new voter account with a generated card number.
        The voter starts as unverified — an admin must verify them
        before they can log in. Returns (voter, voter_card_number)."""
        dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
        age = (datetime.datetime.now() - dob).days // 365
        voter_card = self.generate_voter_card_number()
        voter_id = self._store.next_id("voter")

        voter = Voter(
            voter_id=voter_id,
            full_name=full_name,
            national_id=national_id,
            date_of_birth=dob_str,
            age=age,
            gender=gender,
            address=address,
            phone=phone,
            email=email,
            password=self.hash_password(password),
            voter_card_number=voter_card,
            station_id=station_id,
        )
        self._store.voters[voter_id] = voter
        self._store.log_action(
            "REGISTER", full_name,
            f"New voter registered with card: {voter_card}"
        )
        self._store.save()
        return voter, voter_card
