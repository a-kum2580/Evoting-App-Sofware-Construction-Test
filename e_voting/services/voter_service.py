"""
VoterService — Business logic for admin-side voter management.

This handles operations that admins perform on voter accounts:
  - Viewing and searching voters
  - Verifying voter registrations (single or bulk)
  - Deactivating voter accounts
  - Password changes

Note: Voter self-registration and login are handled by AuthService.
This service focuses on the admin management perspective.
"""


class VoterService:
    """Business logic for voter management (admin-side)."""

    def __init__(self, store):
        self._store = store

    def get_all(self):
        """Return the full dictionary of all registered voters."""
        return self._store.voters

    def get(self, voter_id):
        """Look up a single voter by ID."""
        return self._store.voters.get(voter_id)

    def get_unverified(self):
        """Return only voters whose registration has not been verified.
        These are pending admin approval before they can log in."""
        return {
            vid: v for vid, v in self._store.voters.items()
            if not v.is_verified
        }

    def get_verified_count(self):
        """Count of voters who have been verified by an admin."""
        return sum(1 for v in self._store.voters.values() if v.is_verified)

    def get_unverified_count(self):
        """Count of voters still awaiting verification."""
        return sum(
            1 for v in self._store.voters.values() if not v.is_verified
        )

    def verify(self, voter_id, verified_by):
        """Mark a single voter as verified, allowing them to log in.
        Returns (success: bool, error_message: str or None)."""
        voter = self._store.voters.get(voter_id)
        if not voter:
            return False, "Voter not found."
        if voter.is_verified:
            return False, "Already verified."
        voter.verify()
        self._store.log_action(
            "VERIFY_VOTER", verified_by,
            f"Verified voter: {voter.full_name}"
        )
        self._store.save()
        return True, None

    def verify_all_unverified(self, verified_by):
        """Bulk verify all pending voter registrations.
        Returns the count of voters that were verified."""
        count = 0
        for voter in self._store.voters.values():
            if not voter.is_verified:
                voter.verify()
                count += 1
        self._store.log_action(
            "VERIFY_ALL_VOTERS", verified_by,
            f"Verified {count} voters"
        )
        self._store.save()
        return count

    def deactivate(self, voter_id, deactivated_by):
        """Soft-delete a voter account.
        Returns (success: bool, error_message: str or None)."""
        voter = self._store.voters.get(voter_id)
        if not voter:
            return False, "Voter not found."
        if not voter.is_active:
            return False, "Already deactivated."
        voter.deactivate()
        self._store.log_action(
            "DEACTIVATE_VOTER", deactivated_by,
            f"Deactivated voter: {voter.full_name}"
        )
        self._store.save()
        return True, None

    # ── Search Methods ───────────────────────────────────────

    def search_by_name(self, term):
        """Case-insensitive partial match on voter full name."""
        term_lower = term.lower()
        return [
            v for v in self._store.voters.values()
            if term_lower in v.full_name.lower()
        ]

    def search_by_card(self, card_number):
        """Exact match on voter card number."""
        return [
            v for v in self._store.voters.values()
            if v.voter_card_number == card_number
        ]

    def search_by_national_id(self, national_id):
        """Exact match on national ID."""
        return [
            v for v in self._store.voters.values()
            if v.national_id == national_id
        ]

    def search_by_station(self, station_id):
        """Return all voters registered at the given station."""
        return [
            v for v in self._store.voters.values()
            if v.station_id == station_id
        ]

    def change_password(self, voter_id, new_password_hash, changed_by):
        """Update a voter's password hash. The caller is responsible
        for hashing the password before passing it here.
        Returns True on success, False if voter not found."""
        voter = self._store.voters.get(voter_id)
        if not voter:
            return False
        voter.password = new_password_hash
        self._store.log_action(
            "CHANGE_PASSWORD", changed_by, "Password changed"
        )
        self._store.save()
        return True
