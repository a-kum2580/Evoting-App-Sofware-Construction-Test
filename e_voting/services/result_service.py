"""
ResultService — Election result tallying, statistics, and reporting.

This service is responsible for all read-only analytical operations:
  - Vote counting and ranking for each position in a poll
  - Turnout calculations (votes cast vs eligible voters)
  - System-wide statistics (entity counts by status)
  - Voter demographics (gender distribution, age groups)
  - Station load analysis (capacity utilisation)
  - Party and education distribution among candidates
  - Station-by-station result breakdowns
  - Audit log retrieval with filtering

All methods return raw data structures — the UI layer is responsible
for formatting and displaying the results with charts and colors.
"""

from e_voting.constants import (
    BAR_CHART_WIDTH, TURNOUT_HIGH_THRESHOLD, TURNOUT_MEDIUM_THRESHOLD,
    STATION_LOAD_WARNING_PERCENT, STATION_LOAD_CRITICAL_PERCENT,
    AUDIT_FILTER_ACTION, AUDIT_FILTER_USER, AUDIT_FILTER_LAST,
    AGE_GROUP_YOUNG, AGE_GROUP_ADULT, AGE_GROUP_MIDDLE,
    AGE_GROUP_SENIOR, AGE_GROUP_ELDER, safe_percentage,
)


class ResultService:
    """Calculates election results, statistics, and station breakdowns."""

    def __init__(self, store):
        self._store = store

    # ── Vote Tallying ────────────────────────────────────────

    def get_position_tally(self, poll_id, position_id):
        """Count votes for each candidate in a specific position.
        Returns a tuple of:
          - vote_counts: dict mapping candidate_id -> vote count
          - abstain_count: number of voters who abstained
          - total: total votes (including abstentions)"""
        vote_counts = {}
        abstain_count = 0
        for vote in self._store.votes:
            if vote.poll_id == poll_id and vote.position_id == position_id:
                if vote.abstained:
                    abstain_count += 1
                else:
                    cid = vote.candidate_id
                    vote_counts[cid] = vote_counts.get(cid, 0) + 1
        total = sum(vote_counts.values()) + abstain_count
        return vote_counts, abstain_count, total

    # ── Turnout Calculations ─────────────────────────────────

    def get_eligible_voter_count(self, poll):
        """Count voters who are verified, active, and registered at
        a station that is included in this poll."""
        return sum(
            1 for v in self._store.voters.values()
            if v.is_verified and v.is_active
            and v.station_id in poll.station_ids
        )

    def calculate_turnout(self, poll):
        """Calculate voter turnout percentage for a poll.
        Returns (turnout_percentage, eligible_voter_count)."""
        eligible = self.get_eligible_voter_count(poll)
        return safe_percentage(poll.total_votes_cast, eligible), eligible

    # ── System-wide Statistics ───────────────────────────────

    def get_system_statistics(self):
        """Aggregate counts across all entity types, broken down by status.
        Returns a flat dictionary used by the statistics display."""
        candidates = self._store.candidates
        voters = self._store.voters
        stations = self._store.voting_stations
        polls = self._store.polls

        return {
            "total_candidates": len(candidates),
            "active_candidates": sum(
                1 for c in candidates.values() if c.is_active
            ),
            "total_voters": len(voters),
            "verified_voters": sum(
                1 for v in voters.values() if v.is_verified
            ),
            "active_voters": sum(
                1 for v in voters.values() if v.is_active
            ),
            "total_stations": len(stations),
            "active_stations": sum(
                1 for s in stations.values() if s.is_active
            ),
            "total_polls": len(polls),
            "open_polls": sum(
                1 for p in polls.values() if p.is_open()
            ),
            "closed_polls": sum(
                1 for p in polls.values() if p.is_closed()
            ),
            "draft_polls": sum(
                1 for p in polls.values() if p.is_draft()
            ),
            "total_votes": len(self._store.votes),
        }

    # ── Voter Demographics ───────────────────────────────────

    def get_voter_demographics(self):
        """Break down registered voters by gender and age group.
        Returns (gender_counts_dict, age_groups_dict, total_voters)."""
        voters = self._store.voters
        total_voters = len(voters)
        gender_counts = {}
        age_groups = {
            "18-25": 0, "26-35": 0, "36-45": 0,
            "46-55": 0, "56-65": 0, "65+": 0,
        }
        for voter in voters.values():
            gender = voter.gender or "?"
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
            age = voter.age or 0
            if age <= AGE_GROUP_YOUNG:
                age_groups["18-25"] += 1
            elif age <= AGE_GROUP_ADULT:
                age_groups["26-35"] += 1
            elif age <= AGE_GROUP_MIDDLE:
                age_groups["36-45"] += 1
            elif age <= AGE_GROUP_SENIOR:
                age_groups["46-55"] += 1
            elif age <= AGE_GROUP_ELDER:
                age_groups["56-65"] += 1
            else:
                age_groups["65+"] += 1
        return gender_counts, age_groups, total_voters

    # ── Station Load Analysis ────────────────────────────────

    def get_station_load(self):
        """Calculate capacity utilisation for each voting station.
        Returns a list of dicts with station, voter_count, load_percent,
        and is_overloaded flag."""
        results = []
        for sid, station in self._store.voting_stations.items():
            voter_count = sum(
                1 for v in self._store.voters.values()
                if v.station_id == sid
            )
            load_percent = safe_percentage(voter_count, station.capacity)
            results.append({
                "station": station,
                "voter_count": voter_count,
                "load_percent": load_percent,
                "is_overloaded": load_percent > STATION_LOAD_CRITICAL_PERCENT,
            })
        return results

    # ── Candidate Distributions ──────────────────────────────

    def get_party_distribution(self):
        """Count active candidates per political party.
        Returns a dict sorted by count (highest first)."""
        party_counts = {}
        for candidate in self._store.candidates.values():
            if candidate.is_active:
                party = candidate.party
                party_counts[party] = party_counts.get(party, 0) + 1
        return dict(
            sorted(party_counts.items(), key=lambda x: x[1], reverse=True)
        )

    def get_education_distribution(self):
        """Count active candidates per education level."""
        edu_counts = {}
        for candidate in self._store.candidates.values():
            if candidate.is_active:
                edu = candidate.education
                edu_counts[edu] = edu_counts.get(edu, 0) + 1
        return edu_counts

    # ── Station-by-Station Results ───────────────────────────

    def get_station_results(self, poll_id):
        """Break down poll results by individual voting station.
        For each station, calculates turnout and per-position vote counts.
        Returns a list of dicts with station info and position results."""
        poll = self._store.polls.get(poll_id)
        if not poll:
            return None

        station_data = []
        for sid in poll.station_ids:
            station = self._store.voting_stations.get(sid)
            if not station:
                continue

            # Get all votes from this specific station for this poll
            station_votes = [
                v for v in self._store.votes
                if v.poll_id == poll_id and v.station_id == sid
            ]
            unique_voters = len(set(v.voter_id for v in station_votes))
            registered = sum(
                1 for v in self._store.voters.values()
                if v.station_id == sid and v.is_verified and v.is_active
            )
            turnout = safe_percentage(unique_voters, registered)

            # Tally votes per position at this station
            position_results = []
            for pos in poll.positions:
                pos_votes = [
                    v for v in station_votes
                    if v.position_id == pos.position_id
                ]
                vote_counts = {}
                abstain_count = 0
                for vote in pos_votes:
                    if vote.abstained:
                        abstain_count += 1
                    else:
                        cid = vote.candidate_id
                        vote_counts[cid] = vote_counts.get(cid, 0) + 1
                total = sum(vote_counts.values()) + abstain_count
                position_results.append({
                    "position_title": pos.position_title,
                    "vote_counts": vote_counts,
                    "abstain_count": abstain_count,
                    "total": total,
                })

            station_data.append({
                "station": station,
                "unique_voters": unique_voters,
                "registered": registered,
                "turnout": turnout,
                "position_results": position_results,
            })

        return station_data

    # ── Audit Log ────────────────────────────────────────────

    def get_audit_log(self, filter_type=None, filter_value=None, limit=None):
        """Retrieve audit log entries with optional filtering.
        filter_type can be:
          - "action": filter by action type (exact match)
          - "user": filter by username (case-insensitive partial match)
          - "last": return only the last N entries (use limit parameter)"""
        entries = self._store.audit_log

        if filter_type == AUDIT_FILTER_ACTION and filter_value:
            entries = [
                e for e in entries if e["action"] == filter_value
            ]
        elif filter_type == AUDIT_FILTER_USER and filter_value:
            entries = [
                e for e in entries
                if filter_value.lower() in e["user"].lower()
            ]
        elif filter_type == AUDIT_FILTER_LAST and limit:
            entries = entries[-limit:]

        return entries

    def get_unique_action_types(self):
        """Return a deduplicated list of all action types that appear
        in the audit log (for building filter menus)."""
        return list(set(e["action"] for e in self._store.audit_log))