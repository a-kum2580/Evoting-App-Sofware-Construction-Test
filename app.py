"""
National E-Voting System — Main Entry Point.

This module is the composition root of the application. It:
  1. Creates the single DataStore instance (data layer)
  2. Creates all Service instances, injecting the DataStore (business layer)
  3. Creates all UI instances, injecting their required services (UI layer)
  4. Loads persisted data from disk
  5. Enters the main application loop (login → dashboard → logout)

Architecture overview (layered, bottom-up):
  ┌────────────────────────────────────────────┐
  │  UI Layer (auth_ui, admin_ui, voter_ui)    │  ← Handles all I/O
  ├────────────────────────────────────────────┤
  │  Service Layer (8 services)                │  ← Business logic
  ├────────────────────────────────────────────┤
  │  Data Layer (DataStore + Models)           │  ← Persistence & state
  └────────────────────────────────────────────┘

Dependencies flow downward only — UI depends on Services, Services
depend on DataStore. This follows the Dependency Inversion Principle
as all dependencies are injected through constructors.
"""

import time

from e_voting.store import DataStore
from e_voting.services.auth_service import AuthService
from e_voting.services.candidate_service import CandidateService
from e_voting.services.station_service import StationService
from e_voting.services.poll_service import PollService
from e_voting.services.voter_service import VoterService
from e_voting.services.admin_service import AdminService
from e_voting.services.vote_service import VoteService
from e_voting.services.result_service import ResultService
from e_voting.constants import ROLE_ADMIN, ROLE_VOTER
from e_voting.ui.console import clear_screen, info, THEME_LOGIN
from e_voting.ui.auth_ui import AuthUI
from e_voting.ui.admin import AdminUI
from e_voting.ui.voter_ui import VoterUI


def main():
    """Wire up all layers and run the application loop."""

    # ── Data Layer ───────────────────────────────────────────
    store = DataStore()

    # ── Service Layer ────────────────────────────────────────
    # Each service receives the shared DataStore via constructor injection
    auth_service = AuthService(store)
    candidate_service = CandidateService(store)
    station_service = StationService(store)
    poll_service = PollService(store)
    voter_service = VoterService(store)
    admin_service = AdminService(store)
    vote_service = VoteService(store)
    result_service = ResultService(store)

    # ── UI Layer ─────────────────────────────────────────────
    # Each UI receives its required services via constructor injection
    auth_ui = AuthUI(store, auth_service)
    admin_ui = AdminUI(
        store, candidate_service, station_service, poll_service,
        voter_service, admin_service, result_service, auth_service,
    )
    voter_ui = VoterUI(
        store, vote_service, result_service, auth_service, voter_service,
    )

    # ── Load Persisted Data ──────────────────────────────────
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...\033[0m")
    try:
        store.load()
        info("Data loaded successfully")
    except IOError as load_error:
        info(str(load_error))
    time.sleep(1)

    # ── Main Application Loop ────────────────────────────────
    # Each iteration: show login → route to dashboard → logout
    while True:
        clear_screen()
        logged_in = auth_ui.show_login_menu()
        if logged_in:
            if store.current_role == ROLE_ADMIN:
                admin_ui.show_dashboard()
            elif store.current_role == ROLE_VOTER:
                voter_ui.show_dashboard()
            store.logout()


if __name__ == "__main__":
    main()