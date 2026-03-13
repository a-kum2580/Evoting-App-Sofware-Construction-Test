"""
VoteService — Business logic for the ballot casting process.

This is the core of the voting system. It handles:
  - Determining which polls a voter can participate in
  - Recording individual ballot choices (one per position)
  - Generating a unique vote receipt hash for transparency
  - Enforcing the one-vote-per-poll rule (duplicate prevention)
  - Updating the voter's voting history and poll vote counters

The vote hash is generated from voter_id + poll_id + timestamp
using SHA-256, then truncated to 16 characters for display as
a receipt the voter can reference later.
"""

import datetime
import hashlib

from e_voting.constants import VOTE_HASH_LENGTH
from e_voting.models.vote import Vote


class VoteService:
    """Business logic for the voting process."""

    def __init__(self, store):
        self._store = store

    def get_available_polls(self, voter):
        """Return polls the voter can vote in. A poll is available when:
        1. It is currently open (status == "open")
        2. The voter has not already voted in it
        3. The voter's assigned station is included in the poll's station list"""
        available = {}
        for poll_id, poll in self._store.polls.items():
            if (poll.is_open()
                    and not voter.has_voted_in_poll(poll_id)
                    and voter.station_id in poll.station_ids):
                available[poll_id] = poll
        return available

    def get_open_polls(self):
        """Return all currently open polls (for display purposes)."""
        return {
            pid: p for pid, p in self._store.polls.items()
            if p.is_open()
        }

    def get_closed_polls(self):
        """Return all closed polls (for viewing results)."""
        return {
            pid: p for pid, p in self._store.polls.items()
            if p.is_closed()
        }

    def cast_votes(self, voter, poll_id, choices):
        """Record all ballot choices for a voter in a specific poll.

        Args:
            voter: The Voter object casting the ballot.
            poll_id: The ID of the poll being voted in.
            choices: List of dicts, each containing:
                - position_id: Which position this choice is for
                - candidate_id: Selected candidate ID (or None if abstained)
                - abstained: Boolean flag

        Returns:
            The truncated vote hash string (receipt for the voter),
            or None if the poll was not found.
        """
        poll = self._store.polls.get(poll_id)
        if not poll:
            return None

        # Generate a unique hash receipt from voter+poll+timestamp
        vote_timestamp = str(datetime.datetime.now())
        raw_hash = f"{voter.id}{poll_id}{vote_timestamp}"
        vote_hash = hashlib.sha256(
            raw_hash.encode()
        ).hexdigest()[:VOTE_HASH_LENGTH]

        # Create one Vote record per position choice
        for choice in choices:
            vote = Vote(
                vote_id=vote_hash + str(choice["position_id"]),
                poll_id=poll_id,
                position_id=choice["position_id"],
                candidate_id=choice["candidate_id"],
                voter_id=voter.id,
                station_id=voter.station_id,
                timestamp=vote_timestamp,
                abstained=choice["abstained"],
            )
            self._store.votes.append(vote)

        # Mark the voter as having voted in this poll (duplicate prevention)
        voter.record_vote(poll_id)

        # Also update the stored voter object to keep the store in sync
        # (the session voter and the stored voter may be the same reference,
        # but we ensure consistency regardless)
        for stored_voter in self._store.voters.values():
            if stored_voter.id == voter.id:
                if poll_id not in stored_voter.has_voted_in:
                    stored_voter.record_vote(poll_id)
                break

        # Increment the poll's total vote counter
        poll.record_vote()
        self._store.log_action(
            "CAST_VOTE", voter.voter_card_number,
            f"Voted in poll: {poll.title} (Hash: {vote_hash})"
        )
        self._store.save()
        return vote_hash

    def get_voter_votes_in_poll(self, voter_id, poll_id):
        """Retrieve all Vote records for a specific voter in a specific poll.
        Used to display the voter's voting history."""
        return [
            v for v in self._store.votes
            if v.poll_id == poll_id and v.voter_id == voter_id
        ]
