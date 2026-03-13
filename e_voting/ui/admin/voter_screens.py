"""
VoterScreens — Admin screens for voter management.

Handles: view all voters, verify (single/bulk), deactivate, and search.
Delegates all business logic to VoterService.
"""

from e_voting.constants import ANSI_BADGE_OVERHEAD
from e_voting.ui.console import (
    clear_screen, header, subheader, table_header, table_divider,
    menu_item, prompt, error, success, info, status_badge, pause,
    THEME_ADMIN, THEME_ADMIN_ACCENT, DIM, RESET, BOLD,
)


