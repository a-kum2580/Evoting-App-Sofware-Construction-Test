"""Candidate management service."""

import datetime

from models.candidate import Candidate
from config import MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS


class CandidateService:
    """CRUD operations and eligibility validation for candidates."""

    def __init__(self, store):
        self.store = store

    def get_all(self):
        """Return all candidates."""
        return self.store.candidates

    def get_by_id(self, candidate_id):
        """Return a single candidate or None."""
        return self.store.candidates.get(candidate_id)

    def national_id_exists(self, national_id):
        """Check if a candidate with this national ID already exists."""
        return any(
            c.national_id == national_id
            for c in self.store.candidates.values()
        )

    @staticmethod
    def calculate_age(dob_str):
        """Return (age, error) from a YYYY-MM-DD string."""
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
            return age, None
        except ValueError:
            return None, "Invalid date format."

    @staticmethod
    def validate_age(age):
        """Return an error string if age is out of range, else None."""
        if age < MIN_CANDIDATE_AGE:
            return f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}"
        if age > MAX_CANDIDATE_AGE:
            return f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}"
        return None

    @staticmethod
    def get_education_levels():
        return list(REQUIRED_EDUCATION_LEVELS)

    def create(self, full_name, national_id, dob_str, age, gender,
               education, party, manifesto, address, phone, email,
               has_criminal_record, years_experience, created_by):
        """Create and store a new candidate. Returns the Candidate object."""
        cid = self.store.candidate_id_counter
        candidate = Candidate(
            candidate_id=cid,
            full_name=full_name,
            national_id=national_id,
            date_of_birth=dob_str,
            age=age,
            gender=gender,
            education=education,
            party=party,
            manifesto=manifesto,
            address=address,
            phone=phone,
            email=email,
            has_criminal_record=has_criminal_record,
            years_experience=years_experience,
            created_by=created_by,
        )
        self.store.candidates[cid] = candidate
        self.store.candidate_id_counter += 1
        return candidate

    def update(self, candidate_id, **fields):
        """Update the specified fields of a candidate."""
        candidate = self.store.candidates.get(candidate_id)
        if candidate is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(candidate, key):
                setattr(candidate, key, value)
        return candidate

    def deactivate(self, candidate_id):
        """Soft-delete a candidate by setting is_active to False."""
        candidate = self.store.candidates.get(candidate_id)
        if candidate:
            candidate.is_active = False
        return candidate

    def is_in_active_poll(self, candidate_id):
        """Return the poll title if the candidate is in an open poll, else None."""
        for poll in self.store.polls.values():
            if poll.status == "open":
                for pos in poll.positions:
                    if candidate_id in pos.get("candidate_ids", []):
                        return poll.title
        return None

    def search_by_name(self, term):
        return [c for c in self.store.candidates.values()
                if term.lower() in c.full_name.lower()]

    def search_by_party(self, term):
        return [c for c in self.store.candidates.values()
                if term.lower() in c.party.lower()]

    def search_by_education(self, education):
        return [c for c in self.store.candidates.values()
                if c.education == education]

    def search_by_age_range(self, min_age, max_age):
        return [c for c in self.store.candidates.values()
                if min_age <= c.age <= max_age]
