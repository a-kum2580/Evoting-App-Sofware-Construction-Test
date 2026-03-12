"""Voter management service."""

import datetime
import hashlib
import random
import string

from models.voter import Voter
from config import MIN_VOTER_AGE


class VoterService:
    """Registration, verification, and management of voters."""

    def __init__(self, store):
        self.store = store

    def get_all(self):
        return self.store.voters

    def get_by_id(self, voter_id):
        return self.store.voters.get(voter_id)

    def national_id_exists(self, national_id):
        return any(v.national_id == national_id
                   for v in self.store.voters.values())

    @staticmethod
    def validate_dob(dob_str):
        """Return (age, error)."""
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
            if age < MIN_VOTER_AGE:
                return None, f"You must be at least {MIN_VOTER_AGE} years old to register."
            return age, None
        except ValueError:
            return None, "Invalid date format."

    @staticmethod
    def generate_voter_card_number():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, full_name, national_id, dob_str, age, gender,
                 address, phone, email, password, station_id):
        """
        Create a new voter record.
        Returns the Voter object (unverified by default).
        """
        voter_card = self.generate_voter_card_number()
        vid = self.store.voter_id_counter
        voter = Voter(
            voter_id=vid,
            full_name=full_name,
            national_id=national_id,
            date_of_birth=dob_str,
            age=age,
            gender=gender,
            address=address,
            phone=phone,
            email=email,
            password_hash=self.hash_password(password),
            voter_card_number=voter_card,
            station_id=station_id,
        )
        self.store.voters[vid] = voter
        self.store.voter_id_counter += 1
        return voter

    def get_unverified(self):
        return {vid: v for vid, v in self.store.voters.items()
                if not v.is_verified}

    def verify(self, voter_id):
        voter = self.store.voters.get(voter_id)
        if voter:
            voter.is_verified = True
        return voter

    def verify_all_pending(self):
        unverified = self.get_unverified()
        for vid in unverified:
            self.store.voters[vid].is_verified = True
        return len(unverified)

    def deactivate(self, voter_id):
        voter = self.store.voters.get(voter_id)
        if voter:
            voter.is_active = False
        return voter

    def change_password(self, voter_id, new_password_hash):
        voter = self.store.voters.get(voter_id)
        if voter:
            voter.password = new_password_hash
        return voter

    def search_by_name(self, term):
        return [v for v in self.store.voters.values()
                if term.lower() in v.full_name.lower()]

    def search_by_card(self, card_number):
        return [v for v in self.store.voters.values()
                if v.voter_card_number == card_number]

    def search_by_national_id(self, national_id):
        return [v for v in self.store.voters.values()
                if v.national_id == national_id]

    def search_by_station(self, station_id):
        return [v for v in self.store.voters.values()
                if v.station_id == station_id]

    def count_verified(self):
        return sum(1 for v in self.store.voters.values() if v.is_verified)

    def count_unverified(self):
        return sum(1 for v in self.store.voters.values() if not v.is_verified)
