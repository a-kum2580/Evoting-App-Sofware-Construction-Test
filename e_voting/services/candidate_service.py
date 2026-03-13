"""
CandidateService — Business logic for candidate management.

Handles all candidate-related operations: creation with eligibility
validation, retrieval, updates, soft-deletion (deactivation), and
multi-criteria search. Enforces business rules like:
  - National ID must be unique across all candidates
  - Candidate age must be within MIN_CANDIDATE_AGE..MAX_CANDIDATE_AGE
  - Candidates in active (open) polls cannot be deactivated
"""

import datetime

from e_voting.constants import (
    MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS,
)
from e_voting.models.candidate import Candidate


class CandidateService:
    """Business logic for candidate management."""

    def __init__(self, store):
        self._store = store

    def is_national_id_unique(self, national_id):
        """Check that no existing candidate has this National ID."""
        return all(
            c.national_id != national_id
            for c in self._store.candidates.values()
        )

    def validate_candidate_age(self, dob_str):
        """Parse date of birth string and check age eligibility.
        Returns (age, None) on success, or (None, error_msg) on failure."""
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            return None, "Invalid date format."

        if age < MIN_CANDIDATE_AGE:
            return None, (f"Candidate must be at least {MIN_CANDIDATE_AGE} "
                          f"years old. Current age: {age}")
        if age > MAX_CANDIDATE_AGE:
            return None, (f"Candidate must not be older than "
                          f"{MAX_CANDIDATE_AGE}. Current age: {age}")
        return age, None

    def create(self, full_name, national_id, dob_str, age, gender, education,
               party, manifesto, address, phone, email, years_experience,
               created_by):
        """Create a new candidate record, assign an ID, persist, and
        log the action. Returns the created Candidate object."""
        candidate_id = self._store.next_id("candidate")
        candidate = Candidate(
            candidate_id=candidate_id,
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
            years_experience=years_experience,
            created_by=created_by,
        )
        self._store.candidates[candidate_id] = candidate
        self._store.log_action(
            "CREATE_CANDIDATE", created_by,
            f"Created candidate: {full_name} (ID: {candidate_id})"
        )
        self._store.save()
        return candidate

    def get_all(self):
        """Return the full dictionary of all candidates (active and inactive)."""
        return self._store.candidates

    def get(self, candidate_id):
        """Look up a single candidate by ID. Returns None if not found."""
        return self._store.candidates.get(candidate_id)

    def update(self, candidate_id, updates, updated_by):
        """Apply a dictionary of field updates to an existing candidate.
        Only non-None values for existing attributes are applied.
        Returns the updated Candidate, or None if not found."""
        candidate = self._store.candidates.get(candidate_id)
        if not candidate:
            return None
        for key, value in updates.items():
            if value is not None and hasattr(candidate, key):
                setattr(candidate, key, value)
        self._store.log_action(
            "UPDATE_CANDIDATE", updated_by,
            f"Updated candidate: {candidate.full_name} (ID: {candidate_id})"
        )
        self._store.save()
        return candidate

    def can_deactivate(self, candidate_id):
        """Check whether a candidate can safely be deactivated.
        A candidate cannot be deactivated if they are assigned to
        any position in an open (active) poll.
        Returns (True, None) if safe, or (False, reason_string) if not."""
        for poll in self._store.polls.values():
            if poll.is_open():
                for pos in poll.positions:
                    if candidate_id in pos.candidate_ids:
                        return False, (
                            f"Cannot delete - candidate is in active poll: "
                            f"{poll.title}"
                        )
        return True, None

    def deactivate(self, candidate_id, deactivated_by):
        """Soft-delete a candidate by setting is_active to False.
        Returns True on success, False if the candidate was not found."""
        candidate = self._store.candidates.get(candidate_id)
        if not candidate:
            return False
        candidate.deactivate()
        self._store.log_action(
            "DELETE_CANDIDATE", deactivated_by,
            f"Deactivated candidate: {candidate.full_name} "
            f"(ID: {candidate_id})"
        )
        self._store.save()
        return True

    # ── Search Methods ───────────────────────────────────────
    # Each returns a list of matching Candidate objects.

    def search_by_name(self, term):
        """Case-insensitive partial match on candidate full name."""
        term_lower = term.lower()
        return [
            c for c in self._store.candidates.values()
            if term_lower in c.full_name.lower()
        ]

    def search_by_party(self, term):
        """Case-insensitive partial match on party name."""
        term_lower = term.lower()
        return [
            c for c in self._store.candidates.values()
            if term_lower in c.party.lower()
        ]

    def search_by_education(self, education):
        """Exact match on education level string."""
        return [
            c for c in self._store.candidates.values()
            if c.education == education
        ]

    def search_by_age_range(self, min_age, max_age):
        """Return candidates whose age falls within the given range (inclusive)."""
        return [
            c for c in self._store.candidates.values()
            if min_age <= c.age <= max_age
        ]
