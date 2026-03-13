"""
Application-wide constants for the National E-Voting System.

All magic numbers and magic strings from the original monolith are
extracted here so they can be changed in one place (DRY principle).
Grouped by domain area for readability.
"""

# ── Poll Status Strings ─────────────────────────────────────
POLL_STATUS_DRAFT = "draft"
POLL_STATUS_OPEN = "open"
POLL_STATUS_CLOSED = "closed"

# ── User Role Strings ───────────────────────────────────────
ROLE_ADMIN = "admin"
ROLE_VOTER = "voter"

# ── Audit Log Filter Types ──────────────────────────────────
AUDIT_FILTER_LAST = "last"
AUDIT_FILTER_ACTION = "action"
AUDIT_FILTER_USER = "user"

# ── Default Admin Seed Data ─────────────────────────────────
DEFAULT_ADMIN_ID = 1
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULL_NAME = "System Administrator"
DEFAULT_ADMIN_EMAIL = "admin@evote.com"
DEFAULT_ADMIN_ROLE = "super_admin"

# ── ID Counter Seed Values ──────────────────────────────────
# All entity IDs start at 1; admin starts at 2 because ID 1 is the default admin
INITIAL_ENTITY_ID = 1
INITIAL_ADMIN_ID_COUNTER = 2

# ── Candidate Eligibility Rules ──────────────────────────────
# Candidates must fall within this age range to stand for election
MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75

# Only candidates with these education levels are accepted
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"
]

# ── Voter Eligibility Rules ──────────────────────────────────
MIN_VOTER_AGE = 18
MIN_PASSWORD_LENGTH = 6

# ── Validation Sets ──────────────────────────────────────────
VALID_GENDERS = ["M", "F", "OTHER"]
VALID_POSITION_LEVELS = ["national", "regional", "local"]

# ── Persistence & Security ───────────────────────────────────
DATA_FILE_PATH = "evoting_data.json"
VOTER_CARD_LENGTH = 12       # Random alphanumeric voter card ID length
VOTE_HASH_LENGTH = 16        # Truncated SHA-256 hash shown as vote receipt

# ── Voting ───────────────────────────────────────────────────
ABSTAIN_CHOICE = 0           # Menu index representing an abstain vote
FIRST_CANDIDATE_INDEX = 1    # First valid candidate menu option

# ── Percentage and Counting ──────────────────────────────────
PERCENTAGE_BASE = 100        # Denominator for percentage calculations


def safe_percentage(part, whole):
    """Calculate a percentage safely, returning 0.0 when the denominator is zero."""
    return (part / whole * PERCENTAGE_BASE) if whole else 0.0

# ── Display / Reporting ──────────────────────────────────────
AUDIT_LOG_DEFAULT_LIMIT = 20
BAR_CHART_WIDTH = 50         # Max characters for the result bar chart
PREVIEW_MAX_LENGTH = 50      # Truncation length for text previews in forms
MANIFESTO_PREVIEW_LENGTH = 80  # Longer preview for candidate manifestos

# Turnout percentage thresholds for color-coding in reports
TURNOUT_HIGH_THRESHOLD = 50
TURNOUT_MEDIUM_THRESHOLD = 25

# Station capacity utilisation thresholds (percentage)
STATION_LOAD_WARNING_PERCENT = 75
STATION_LOAD_CRITICAL_PERCENT = 100

# ── Age Group Boundaries for Demographics ───────────────────
AGE_GROUP_YOUNG = 25
AGE_GROUP_ADULT = 35
AGE_GROUP_MIDDLE = 45
AGE_GROUP_SENIOR = 55
AGE_GROUP_ELDER = 65

# ── Console UI Layout ───────────────────────────────────────
HEADER_BOX_WIDTH = 58       # Width of the double-line header box
MENU_NUMBER_WIDTH = 3        # Alignment width for menu item numbers
ANSI_BADGE_OVERHEAD = 9     # Extra chars ANSI escape codes add to status badges
TIMESTAMP_DISPLAY_LENGTH = 19  # ISO timestamp without microseconds
DETAIL_MAX_DISPLAY_LENGTH = 50  # Truncation length for audit log details

# ── Age Group Display Widths ────────────────────────────────
AGE_GROUP_LABEL_WIDTH = 5
AGE_GROUP_COUNT_WIDTH = 3

# ── Profile Display ─────────────────────────────────────────
PROFILE_LABEL_WIDTH = 16     # Alignment width for profile field labels

# ── Admin Role Definitions ───────────────────────────────────
# Maps menu choice number to internal role name
ADMIN_ROLES = {
    "1": "super_admin",
    "2": "election_officer",
    "3": "station_manager",
    "4": "auditor",
}

# Human-readable descriptions shown in the admin creation menu
ADMIN_ROLE_DESCRIPTIONS = {
    "super_admin": "Full access",
    "election_officer": "Manage polls and candidates",
    "station_manager": "Manage stations and verify voters",
    "auditor": "Read-only access",
}
