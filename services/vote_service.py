"""Vote casting and result tallying service."""

import datetime
import hashlib

from models.vote import Vote


class VoteService:
    """Ballot casting, duplicate prevention, and result computation."""

    def __init__(self, store):
        self.store = store

    def get_available_polls_for_voter(self, voter):
        """Return polls that are open and the voter hasn't voted in yet."""
        open_polls = {pid: p for pid, p in self.store.polls.items()
                      if p.status == "open"}
        available = {}
        for pid, poll in open_polls.items():
            if (pid not in voter.has_voted_in and
                    voter.station_id in poll.station_ids):
                available[pid] = poll
        return available

    def cast_votes(self, voter, poll, vote_selections):
        """
        Record the voter's ballot.

        *vote_selections* is a list of dicts:
          [{"position_id": int, "candidate_id": int|None, "abstained": bool}, ...]

        Returns the vote reference hash.
        """
        vote_timestamp = str(datetime.datetime.now())
        vote_hash = hashlib.sha256(
            f"{voter.id}{poll.id}{vote_timestamp}".encode()
        ).hexdigest()[:16]

        for sel in vote_selections:
            vote = Vote(
                vote_id=vote_hash + str(sel["position_id"]),
                poll_id=poll.id,
                position_id=sel["position_id"],
                candidate_id=sel.get("candidate_id"),
                voter_id=voter.id,
                station_id=voter.station_id,
                timestamp=vote_timestamp,
                abstained=sel.get("abstained", False),
            )
            self.store.votes.append(vote)

        # Mark voter as having voted
        voter.has_voted_in.append(poll.id)
        for v in self.store.voters.values():
            if v.id == voter.id:
                if poll.id not in v.has_voted_in:
                    v.has_voted_in.append(poll.id)
                break

        poll.total_votes_cast += 1
        return vote_hash

    def get_votes_for_poll(self, poll_id):
        """Return all votes cast in a given poll."""
        return [v for v in self.store.votes if v.poll_id == poll_id]

    def get_votes_for_voter_in_poll(self, voter_id, poll_id):
        """Return one voter's ballot entries for a poll."""
        return [v for v in self.store.votes
                if v.poll_id == poll_id and v.voter_id == voter_id]

    def tally_position(self, poll_id, position_id):
        """
        Compute vote counts for a position in a poll.

        Returns (vote_counts_dict, abstain_count, total).
        vote_counts_dict maps candidate_id -> count.
        """
        vote_counts = {}
        abstain_count = 0
        total = 0
        for v in self.store.votes:
            if v.poll_id == poll_id and v.position_id == position_id:
                total += 1
                if v.abstained:
                    abstain_count += 1
                else:
                    vote_counts[v.candidate_id] = vote_counts.get(
                        v.candidate_id, 0) + 1
        return vote_counts, abstain_count, total

    def tally_position_for_station(self, poll_id, position_id, station_id):
        """Same as tally_position but filtered by a specific station."""
        vote_counts = {}
        abstain_count = 0
        total = 0
        for v in self.store.votes:
            if (v.poll_id == poll_id and
                    v.position_id == position_id and
                    v.station_id == station_id):
                total += 1
                if v.abstained:
                    abstain_count += 1
                else:
                    vote_counts[v.candidate_id] = vote_counts.get(
                        v.candidate_id, 0) + 1
        return vote_counts, abstain_count, total

    def count_station_voters(self, poll_id, station_id):
        """Count unique voters who cast ballots at a station for a poll."""
        station_votes = [
            v for v in self.store.votes
            if v.poll_id == poll_id and v.station_id == station_id
        ]
        return len(set(v.voter_id for v in station_votes))

    def get_eligible_voter_count(self, poll):
        """Count verified, active voters at stations in this poll."""
        return sum(
            1 for v in self.store.voters.values()
            if v.is_verified and v.is_active and v.station_id in poll.station_ids
        )
