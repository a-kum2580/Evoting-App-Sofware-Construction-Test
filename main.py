"""
E-Voting System - Entry Point.

Bootstrap the application by:
1. Initialising the DataStore and loading persisted data.
2. Instantiating all business logic services (Dependency Injection).
3. Instantiating UI handlers with their required services.
4. Entering the main login loop.
"""

import sys
import time
from data.data_store import DataStore
from data import persistence
from services.auth_service import AuthService
from services.candidate_service import CandidateService
from services.station_service import StationService
from services.position_service import PositionService
from services.poll_service import PollService
from services.voter_service import VoterService
from services.admin_service import AdminService
from services.vote_service import VoteService
from services.audit_service import AuditService
from ui.console import clear_screen, THEME_LOGIN, RESET
from ui.login_ui import LoginUI
from ui.admin_ui import AdminUI
from ui.voter_ui import VoterUI


def main():
    # 1. Initialise data layer
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")
    store = DataStore()
    try:
        persistence.load_data(store)
    except Exception as e:
        print(f"  Warning: Could not load existing data: {e}")
    
    time.sleep(1)

    # 2. Instantiate services (Dependency Injection)
    audit_svc = AuditService(store)
    auth_svc = AuthService(store)
    cand_svc = CandidateService(store)
    stat_svc = StationService(store)
    pos_svc = PositionService(store)
    poll_svc = PollService(store)
    voter_svc = VoterService(store)
    admin_svc = AdminService(store)
    vote_svc = VoteService(store)

    # 3. Instantiate UI components
    login_ui = LoginUI(store, auth_svc, voter_svc, stat_svc, audit_svc, persistence)
    admin_ui = AdminUI(store, cand_svc, stat_svc, pos_svc, poll_svc, voter_svc, admin_svc, vote_svc, audit_svc, persistence)
    voter_ui = VoterUI(store, poll_svc, vote_svc, voter_svc, audit_svc, cand_svc, stat_svc, persistence)

    # 4. Main Application Loop
    while True:
        clear_screen()
        # Reset session state on each return to login
        store.current_user = None
        store.current_role = None
        
        logged_in = login_ui.show()
        
        if logged_in:
            if store.current_role == "admin":
                admin_ui.run()
            elif store.current_role == "voter":
                voter_ui.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  System interrupted. Exiting...")
        sys.exit(0)
