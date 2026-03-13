"""
AdminUI — Thin coordinator for the admin dashboard.

Composes six specialised screen-handler classes and maps each menu
choice to the appropriate handler method using a dictionary (strategy
pattern), keeping this module under ~150 lines.

The handler classes are:
  - CandidateScreens  (candidate CRUD + search)
  - StationScreens    (station CRUD)
  - PollScreens       (position + poll management)
  - VoterScreens      (voter view, verify, deactivate, search)
  - AdminMgmtScreens  (admin create, view, deactivate)
  - ResultsScreens    (results, statistics, audit log)
"""

from e_voting.ui.console import (
    clear_screen, header, subheader, menu_item, prompt, error, info, pause,
    THEME_ADMIN, THEME_ADMIN_ACCENT, DIM, RESET, BOLD,
)
from e_voting.ui.admin.candidate_screens import CandidateScreens
from e_voting.ui.admin.station_screens import StationScreens
from e_voting.ui.admin.poll_screens import PollScreens
from e_voting.ui.admin.voter_screens import VoterScreens
from e_voting.ui.admin.admin_mgmt_screens import AdminMgmtScreens
from e_voting.ui.admin.results_screens import ResultsScreens


class AdminUI:
    """Admin dashboard — the central admin control panel.

    All eight service dependencies are injected via the constructor,
    following the Dependency Inversion Principle. The UI never
    instantiates services itself.

    Each service is forwarded to the screen-handler that needs it,
    keeping the handler constructors narrow (Interface Segregation).
    """

    def __init__(self, store, candidate_service, station_service,
                 poll_service, voter_service, admin_service,
                 result_service, auth_service):
        self._store = store
        self._candidate_screens = CandidateScreens(store, candidate_service)
        self._station_screens = StationScreens(store, station_service)
        self._poll_screens = PollScreens(
            store, poll_service, candidate_service, station_service
        )
        self._voter_screens = VoterScreens(store, voter_service)
        self._admin_screens = AdminMgmtScreens(
            store, admin_service, auth_service
        )
        self._result_screens = ResultsScreens(
            store, result_service, poll_service
        )

    def show_dashboard(self):
        """Main admin loop — displays the menu and dispatches actions.

        Uses a dictionary (strategy pattern) instead of long if/elif.
        """
        admin_actions = {
            "1":  self._candidate_screens.create,
            "2":  self._candidate_screens.view_all,
            "3":  self._candidate_screens.update,
            "4":  self._candidate_screens.delete,
            "5":  self._candidate_screens.search,
            "6":  self._station_screens.create,
            "7":  self._station_screens.view_all,
            "8":  self._station_screens.update,
            "9":  self._station_screens.delete,
            "10": self._poll_screens.create_position,
            "11": self._poll_screens.view_positions,
            "12": self._poll_screens.update_position,
            "13": self._poll_screens.delete_position,
            "14": self._poll_screens.create_poll,
            "15": self._poll_screens.view_all_polls,
            "16": self._poll_screens.update_poll,
            "17": self._poll_screens.delete_poll,
            "18": self._poll_screens.open_close_poll,
            "19": self._poll_screens.assign_candidates,
            "20": self._voter_screens.view_all,
            "21": self._voter_screens.verify,
            "22": self._voter_screens.deactivate,
            "23": self._voter_screens.search,
            "24": self._admin_screens.create,
            "25": self._admin_screens.view_all,
            "26": self._admin_screens.deactivate,
            "27": self._result_screens.view_poll_results,
            "28": self._result_screens.view_detailed_statistics,
            "29": self._result_screens.view_audit_log,
            "30": self._result_screens.station_wise_results,
            "31": self._save_data,
        }

        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            user = self._store.current_user
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{user.full_name}{RESET}"
                  f"  {DIM}│  Role: {user.role}{RESET}")

            subheader("Candidate Management", THEME_ADMIN_ACCENT)
            menu_item(1, "Create Candidate", THEME_ADMIN)
            menu_item(2, "View All Candidates", THEME_ADMIN)
            menu_item(3, "Update Candidate", THEME_ADMIN)
            menu_item(4, "Delete Candidate", THEME_ADMIN)
            menu_item(5, "Search Candidates", THEME_ADMIN)

            subheader("Voting Station Management", THEME_ADMIN_ACCENT)
            menu_item(6, "Create Voting Station", THEME_ADMIN)
            menu_item(7, "View All Stations", THEME_ADMIN)
            menu_item(8, "Update Station", THEME_ADMIN)
            menu_item(9, "Delete Station", THEME_ADMIN)

            subheader("Polls & Positions", THEME_ADMIN_ACCENT)
            menu_item(10, "Create Position", THEME_ADMIN)
            menu_item(11, "View Positions", THEME_ADMIN)
            menu_item(12, "Update Position", THEME_ADMIN)
            menu_item(13, "Delete Position", THEME_ADMIN)
            menu_item(14, "Create Poll", THEME_ADMIN)
            menu_item(15, "View All Polls", THEME_ADMIN)
            menu_item(16, "Update Poll", THEME_ADMIN)
            menu_item(17, "Delete Poll", THEME_ADMIN)
            menu_item(18, "Open/Close Poll", THEME_ADMIN)
            menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)

            subheader("Voter Management", THEME_ADMIN_ACCENT)
            menu_item(20, "View All Voters", THEME_ADMIN)
            menu_item(21, "Verify Voter", THEME_ADMIN)
            menu_item(22, "Deactivate Voter", THEME_ADMIN)
            menu_item(23, "Search Voters", THEME_ADMIN)

            subheader("Admin Management", THEME_ADMIN_ACCENT)
            menu_item(24, "Create Admin Account", THEME_ADMIN)
            menu_item(25, "View Admins", THEME_ADMIN)
            menu_item(26, "Deactivate Admin", THEME_ADMIN)

            subheader("Results & Reports", THEME_ADMIN_ACCENT)
            menu_item(27, "View Poll Results", THEME_ADMIN)
            menu_item(28, "View Detailed Statistics", THEME_ADMIN)
            menu_item(29, "View Audit Log", THEME_ADMIN)
            menu_item(30, "Station-wise Results", THEME_ADMIN)

            subheader("System", THEME_ADMIN_ACCENT)
            menu_item(31, "Save Data", THEME_ADMIN)
            menu_item(32, "Logout", THEME_ADMIN)
            print()
            choice = prompt("Enter choice: ")

            if choice in admin_actions:
                admin_actions[choice]()
            elif choice == "32":
                self._store.log_action(
                    "LOGOUT", user.username, "Admin logged out"
                )
                self._store.save()
                break
            else:
                error("Invalid choice.")
                pause()

    def _save_data(self):
        """Persist all data to disk."""
        self._store.save()
        info("Data saved successfully")
        pause()