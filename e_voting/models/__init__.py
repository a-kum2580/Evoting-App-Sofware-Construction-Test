"""
Models package — Domain entity classes for the E-Voting system.

Each model encapsulates the state and behaviour of one domain concept.
Models provide:
  - Validated construction via __init__
  - Domain-specific methods (e.g. voter.has_voted_in_poll())
  - Serialisation to/from plain dicts for JSON persistence
"""

from e_voting.models.admin import Admin
from e_voting.models.candidate import Candidate
from e_voting.models.poll import Poll, PollPosition
from e_voting.models.position import Position
from e_voting.models.vote import Vote
from e_voting.models.voter import Voter
from e_voting.models.voting_station import VotingStation

__all__ = [
    "Admin", "Candidate", "Poll", "PollPosition",
    "Position", "Vote", "Voter", "VotingStation",
]
