"""
Voter model — Represents a registered voter.

A voter self-registers through the public registration screen and
must be verified by an admin before they can log in and cast ballots.
Each voter is assigned to exactly one voting station and receives a
unique voter card number that serves as their login credential.
"""

import datetime


class Voter:
    """Domain entity for a registered voter.

    Attributes:
        id: Unique auto-incremented identifier.
        voter_card_number: Random 12-char alphanumeric string used for login.
        station_id: The voting station this voter is assigned to.
        is_verified: Must be True (admin-verified) before the voter can log in.
        is_active: Soft-delete flag.
        has_voted_in: List of poll IDs the voter has already cast ballots in
                      (used for duplicate-vote prevention).
        password: SHA-256 hash of the voter's password (never stored in plain text).
    """

    def __init__(self, voter_id, full_name, national_id, date_of_birth, age,
                 gender, address, phone, email, password, voter_card_number,
                 station_id, is_verified=False, is_active=True,
                 has_voted_in=None, registered_at=None, role="voter"):
        self.id = voter_id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password
        self.voter_card_number = voter_card_number
        self.station_id = station_id
        self.is_verified = is_verified
        self.is_active = is_active
        # Default to empty list if None; avoids mutable default argument pitfall
        self.has_voted_in = has_voted_in if has_voted_in is not None else []
        self.registered_at = registered_at or str(datetime.datetime.now())
        self.role = role

    def has_voted_in_poll(self, poll_id):
        """Check if this voter has already cast a ballot in the given poll.
        Used to enforce the one-vote-per-poll rule."""
        return poll_id in self.has_voted_in

    def record_vote(self, poll_id):
        """Mark that this voter has voted in the given poll.
        Called after a ballot is successfully cast."""
        self.has_voted_in.append(poll_id)

    def verify(self):
        """Admin action: mark this voter's registration as verified,
        allowing them to log in and vote."""
        self.is_verified = True

    def deactivate(self):
        """Soft-delete: disables the voter account without removing records."""
        self.is_active = False

    def to_dict(self):
        """Serialise to a plain dictionary for JSON persistence."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "national_id": self.national_id,
            "date_of_birth": self.date_of_birth,
            "age": self.age,
            "gender": self.gender,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "password": self.password,
            "voter_card_number": self.voter_card_number,
            "station_id": self.station_id,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "has_voted_in": self.has_voted_in,
            "registered_at": self.registered_at,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Voter instance from a stored dictionary."""
        return cls(
            voter_id=data["id"],
            full_name=data["full_name"],
            national_id=data["national_id"],
            date_of_birth=data["date_of_birth"],
            age=data["age"],
            gender=data["gender"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            password=data["password"],
            voter_card_number=data["voter_card_number"],
            station_id=data["station_id"],
            is_verified=data.get("is_verified", False),
            is_active=data.get("is_active", True),
            has_voted_in=data.get("has_voted_in", []),
            registered_at=data.get("registered_at"),
            role=data.get("role", "voter"),
        )