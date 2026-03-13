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


class VoterScreens:
    """Admin UI screens for voter management."""

    def __init__(self, store, voter_service):
        self._store = store
        self._voters = voter_service

    def view_all(self):
        clear_screen()
        header("ALL REGISTERED VOTERS", THEME_ADMIN)
        voters = self._voters.get_all()
        if not voters:
            print(); info("No voters registered."); pause(); return
        print()
        col_id, col_name, col_card, col_stn, col_ver, col_act = 5, 25, 15, 6, 10, 8
        table_width = col_id + col_name + col_card + col_stn + col_ver + col_act
        col_ver_display = col_ver + ANSI_BADGE_OVERHEAD
        table_header(
            f"{'ID':<{col_id}} {'Name':<{col_name}} {'Card Number':<{col_card}} {'Stn':<{col_stn}} "
            f"{'Verified':<{col_ver}} {'Active':<{col_act}}", THEME_ADMIN
        )
        table_divider(table_width, THEME_ADMIN)
        for voter in voters.values():
            verified = (status_badge("Yes", True) if voter.is_verified
                        else status_badge("No", False))
            active = (status_badge("Yes", True) if voter.is_active
                      else status_badge("No", False))
            print(f"  {voter.id:<{col_id}} {voter.full_name:<{col_name}} "
                  f"{voter.voter_card_number:<{col_card}} {voter.station_id:<{col_stn}} "
                  f"{verified:<{col_ver_display}} {active}")
        verified_count = self._voters.get_verified_count()
        unverified_count = self._voters.get_unverified_count()
        print(f"\n  {DIM}Total: {len(voters)}  │  "
              f"Verified: {verified_count}  │  "
              f"Unverified: {unverified_count}{RESET}")
        pause()

    def verify(self):
        clear_screen()
        header("VERIFY VOTER", THEME_ADMIN)
        unverified = self._voters.get_unverified()
        if not unverified:
            print(); info("No unverified voters."); pause(); return
        subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for voter in unverified.values():
            print(f"  {THEME_ADMIN}{voter.id}.{RESET} {voter.full_name} "
                  f"{DIM}│ NID: {voter.national_id} "
                  f"│ Card: {voter.voter_card_number}{RESET}")
        print()
        menu_item(1, "Verify a single voter", THEME_ADMIN)
        menu_item(2, "Verify all pending voters", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        username = self._store.current_user.username
        if choice == "1":
            try:
                vid = int(prompt("Enter Voter ID: "))
            except ValueError:
                error("Invalid input."); pause(); return
            ok, err = self._voters.verify(vid, username)
            if not ok:
                (error if err != "Already verified." else info)(err)
            else:
                voter = self._voters.get(vid)
                print()
                success(f"Voter '{voter.full_name}' verified!")
        elif choice == "2":
            count = self._voters.verify_all_unverified(username)
            print()
            success(f"{count} voters verified!")
        pause()

    def deactivate(self):
        clear_screen()
        header("DEACTIVATE VOTER", THEME_ADMIN)
        if not self._voters.get_all():
            print(); info("No voters found."); pause(); return
        print()
        try:
            vid = int(prompt("Enter Voter ID to deactivate: "))
        except ValueError:
            error("Invalid input."); pause(); return

        voter = self._voters.get(vid)
        if not voter:
            error("Voter not found."); pause(); return
        if not voter.is_active:
            info("Already deactivated."); pause(); return

        if prompt(f"Deactivate '{voter.full_name}'? "
                  "(yes/no): ").lower() == "yes":
            self._voters.deactivate(
                vid, self._store.current_user.username
            )
            print()
            success("Voter deactivated.")
        pause()

    def search(self):
        clear_screen()
        header("SEARCH VOTERS", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Voter Card Number", THEME_ADMIN)
        menu_item(3, "National ID", THEME_ADMIN)
        menu_item(4, "Station", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        results = []
        if choice == "1":
            term = prompt("Name: ")
            results = self._voters.search_by_name(term)
        elif choice == "2":
            term = prompt("Card Number: ")
            results = self._voters.search_by_card(term)
        elif choice == "3":
            term = prompt("National ID: ")
            results = self._voters.search_by_national_id(term)
        elif choice == "4":
            try:
                sid = int(prompt("Station ID: "))
                results = self._voters.search_by_station(sid)
            except ValueError:
                error("Invalid input."); pause(); return
        else:
            error("Invalid choice."); pause(); return

        if not results:
            print()
            info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for voter in results:
                verified = (status_badge("Verified", True)
                            if voter.is_verified
                            else status_badge("Unverified", False))
                print(f"  {THEME_ADMIN}ID:{RESET} {voter.id}  "
                      f"{DIM}│{RESET}  {voter.full_name}  "
                      f"{DIM}│  Card:{RESET} {voter.voter_card_number}"
                      f"  {DIM}│{RESET}  {verified}")
        pause()