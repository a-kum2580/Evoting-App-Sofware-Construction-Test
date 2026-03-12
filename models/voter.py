"""Voter domain model."""

import datetime


class Voter:
    """Represents a registered voter."""

    def __init__(self, voter_id, full_name, national_id, date_of_birth,
                 age, gender, address, phone, email, password_hash,
                 voter_card_number, station_id, is_verified=False,
                 is_active=True, has_voted_in=None, registered_at=None,
                 role="voter"):
        self.id = voter_id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password_hash
        self.voter_card_number = voter_card_number
        self.station_id = station_id
        self.is_verified = is_verified
        self.is_active = is_active
        self.has_voted_in = has_voted_in if has_voted_in is not None else []
        self.registered_at = registered_at or str(datetime.datetime.now())
        self.role = role

    def check_password(self, password_hash):
        """Return True if the given hash matches."""
        return self.password == password_hash

    def to_dict(self):
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
            password_hash=data["password"],
            voter_card_number=data["voter_card_number"],
            station_id=data["station_id"],
            is_verified=data.get("is_verified", False),
            is_active=data.get("is_active", True),
            has_voted_in=data.get("has_voted_in", []),
            registered_at=data.get("registered_at"),
            role=data.get("role", "voter"),
        )
