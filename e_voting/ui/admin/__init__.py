"""
e_voting.ui.admin — Admin dashboard sub-package.

Re-exports AdminUI so that callers can continue to import it with:
    from e_voting.ui.admin import AdminUI
"""

from e_voting.ui.admin.admin_ui import AdminUI

__all__ = ["AdminUI"]