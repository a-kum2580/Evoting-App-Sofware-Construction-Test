"""
System-wide constants for the E-Voting application.
Eliminates magic numbers and centralises configuration.
"""

# Candidate eligibility
MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate",
]

# Voter eligibility
MIN_VOTER_AGE = 18

# Persistence
DATA_FILE_PATH = "evoting_data.json"
