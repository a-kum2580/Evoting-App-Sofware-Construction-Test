"""
PollScreens — Admin screens for position and poll management.

Positions and polls are kept together because they are tightly coupled:
a poll always references positions, and position eligibility drives
candidate assignment to polls.

Handles:
  Positions — create, view, update, delete
  Polls — create, view, update, delete, open/close, assign candidates

Delegates all business logic to PollService and CandidateService.
"""

from e_voting.constants import (
    VALID_POSITION_LEVELS, MIN_CANDIDATE_AGE, PREVIEW_MAX_LENGTH,
    POLL_STATUS_OPEN, POLL_STATUS_DRAFT,
)
from e_voting.ui.console import (
    clear_screen, header, subheader, table_header, table_divider,
    menu_item, prompt, error, success, warning, info, status_badge, pause,
    THEME_ADMIN, THEME_ADMIN_ACCENT, GREEN, YELLOW, RED, DIM, RESET, BOLD,
)


class PollScreens:
    """Admin UI screens for position and poll management."""

    def __init__(self, store, poll_service, candidate_service, station_service):
        self._store = store
        self._polls = poll_service
        self._candidates = candidate_service
        self._stations = station_service

    # ── Position Management ──────────────────────────────────

    def create_position(self):
        clear_screen()
        header("CREATE POSITION", THEME_ADMIN)
        print()
        title = prompt(
            "Position Title (e.g. President, Governor, Senator): "
        )
        if not title:
            error("Title cannot be empty."); pause(); return
        description = prompt("Description: ")
        level = prompt("Level (National/Regional/Local): ")
        if level.lower() not in VALID_POSITION_LEVELS:
            error("Invalid level."); pause(); return
        try:
            max_winners = int(prompt("Number of winners/seats: "))
            min_seats = 1
            if max_winners < min_seats:
                error("Must be at least 1."); pause(); return
        except ValueError:
            error("Invalid number."); pause(); return
        min_age_str = prompt(
            f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: "
        )
        min_age = (int(min_age_str) if min_age_str.isdigit()
                   else MIN_CANDIDATE_AGE)

        position = self._polls.create_position(
            title, description, level, max_winners, min_age,
            self._store.current_user.username
        )
        print()
        success(f"Position '{title}' created! ID: {position.id}")
        pause()

    def view_positions(self):
        clear_screen()
        header("ALL POSITIONS", THEME_ADMIN)
        positions = self._polls.get_all_positions()
        if not positions:
            print(); info("No positions found."); pause(); return
        print()
        col_id, col_title, col_level, col_seats, col_age, col_status = 5, 25, 12, 8, 10, 10
        table_width = col_id + col_title + col_level + col_seats + col_age + col_status
        table_header(
            f"{'ID':<{col_id}} {'Title':<{col_title}} {'Level':<{col_level}} {'Seats':<{col_seats}} "
            f"{'Min Age':<{col_age}} {'Status':<{col_status}}", THEME_ADMIN
        )
        table_divider(table_width, THEME_ADMIN)
        for position in positions.values():
            status = (status_badge("Active", True) if position.is_active
                      else status_badge("Inactive", False))
            print(f"  {position.id:<{col_id}} {position.title:<{col_title}} "
                  f"{position.level:<{col_level}} {position.max_winners:<{col_seats}} "
                  f"{position.min_candidate_age:<{col_age}} {status}")
        print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
        pause()

    def update_position(self):
        clear_screen()
        header("UPDATE POSITION", THEME_ADMIN)
        positions = self._polls.get_all_positions()
        if not positions:
            print(); info("No positions found."); pause(); return
        print()
        for position in positions.values():
            print(f"  {THEME_ADMIN}{position.id}.{RESET} {position.title} "
                  f"{DIM}({position.level}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to update: "))
        except ValueError:
            error("Invalid input."); pause(); return
        position = self._store.positions.get(pid)
        if not position:
            error("Position not found."); pause(); return

        print(f"\n  {BOLD}Updating: {position.title}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {}
        new_title = prompt(f"Title [{position.title}]: ")
        if new_title:
            updates["title"] = new_title
        new_desc = prompt(f"Description [{position.description[:PREVIEW_MAX_LENGTH]}]: ")
        if new_desc:
            updates["description"] = new_desc
        new_level = prompt(f"Level [{position.level}]: ")
        if new_level and new_level.lower() in VALID_POSITION_LEVELS:
            updates["level"] = new_level.capitalize()
        new_seats = prompt(f"Seats [{position.max_winners}]: ")
        if new_seats:
            try:
                updates["max_winners"] = int(new_seats)
            except ValueError:
                warning("Keeping old value.")

        self._polls.update_position(
            pid, updates, self._store.current_user.username
        )
        print()
        success("Position updated!")
        pause()

    def delete_position(self):
        clear_screen()
        header("DELETE POSITION", THEME_ADMIN)
        positions = self._polls.get_all_positions()
        if not positions:
            print(); info("No positions found."); pause(); return
        print()
        for position in positions.values():
            print(f"  {THEME_ADMIN}{position.id}.{RESET} {position.title} "
                  f"{DIM}({position.level}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to delete: "))
        except ValueError:
            error("Invalid input."); pause(); return
        if pid not in positions:
            error("Position not found."); pause(); return

        can_delete, reason = self._polls.can_deactivate_position(pid)
        if not can_delete:
            error(reason); pause(); return

        position = positions[pid]
        if prompt(f"Confirm deactivation of '{position.title}'? "
                  "(yes/no): ").lower() == "yes":
            self._polls.deactivate_position(
                pid, self._store.current_user.username
            )
            print()
            success("Position deactivated.")
        pause()

    # ── Poll Management ──────────────────────────────────────

    def create_poll(self):
        clear_screen()
        header("CREATE POLL / ELECTION", THEME_ADMIN)
        print()
        title = prompt("Poll/Election Title: ")
        if not title:
            error("Title cannot be empty."); pause(); return
        description = prompt("Description: ")
        election_type = prompt(
            "Election Type (General/Primary/By-election/Referendum): "
        )
        start_date = prompt("Start Date (YYYY-MM-DD): ")
        end_date = prompt("End Date (YYYY-MM-DD): ")

        _, _, date_err = self._polls.validate_poll_dates(start_date, end_date)
        if date_err:
            error(date_err); pause(); return

        active_positions = self._polls.get_active_positions()
        if not active_positions:
            error("No active positions. Create positions first.")
            pause(); return

        subheader("Available Positions", THEME_ADMIN_ACCENT)
        for position in active_positions.values():
            print(f"    {THEME_ADMIN}{position.id}.{RESET} {position.title} "
                  f"{DIM}({position.level}) - "
                  f"{position.max_winners} seat(s){RESET}")
        try:
            selected_ids = [
                int(x.strip()) for x in
                prompt("\nEnter Position IDs (comma-separated): ").split(",")
            ]
        except ValueError:
            error("Invalid input."); pause(); return

        active_stations = self._stations.get_active()
        if not active_stations:
            error("No voting stations. Create stations first.")
            pause(); return

        subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        for station in active_stations.values():
            print(f"    {THEME_ADMIN}{station.id}.{RESET} {station.name} "
                  f"{DIM}({station.location}){RESET}")
        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            station_ids = list(active_stations.keys())
        else:
            try:
                station_ids = [
                    int(x.strip()) for x in
                    prompt("Enter Station IDs (comma-separated): ").split(",")
                ]
            except ValueError:
                error("Invalid input."); pause(); return

        poll, poll_err = self._polls.create_poll(
            title, description, election_type, start_date, end_date,
            selected_ids, station_ids,
            self._store.current_user.username
        )
        if poll_err:
            error(poll_err); pause(); return

        print()
        success(f"Poll '{title}' created! ID: {poll.id}")
        warning("Status: DRAFT - Assign candidates and then open the poll.")
        pause()

    def view_all_polls(self):
        clear_screen()
        header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        for poll in polls.values():
            status_color = self._poll_status_color(poll.status)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll.id}: "
                  f"{poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  "
                  f"{DIM}│  Status:{RESET} {status_color}{BOLD}"
                  f"{poll.status.upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll.start_date} to "
                  f"{poll.end_date}  {DIM}│  Votes:{RESET} "
                  f"{poll.total_votes_cast}")
            for pos in poll.positions:
                cand_names = [
                    self._store.candidates[cid].full_name
                    for cid in pos.candidate_ids
                    if cid in self._store.candidates
                ]
                cand_display = (', '.join(cand_names) if cand_names
                                else f"{DIM}None assigned{RESET}")
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} "
                      f"{pos.position_title}: {cand_display}")
        print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
        pause()

    def update_poll(self):
        clear_screen()
        header("UPDATE POLL", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        self._display_poll_list(polls)
        try:
            pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return
        if poll.is_open():
            error("Cannot update an open poll. Close it first.")
            pause(); return
        if poll.is_closed() and poll.total_votes_cast:
            error("Cannot update a poll with votes."); pause(); return

        print(f"\n  {BOLD}Updating: {poll.title}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {}
        new_title = prompt(f"Title [{poll.title}]: ")
        if new_title:
            updates["title"] = new_title
        new_desc = prompt(f"Description [{poll.description[:PREVIEW_MAX_LENGTH]}]: ")
        if new_desc:
            updates["description"] = new_desc
        new_type = prompt(f"Election Type [{poll.election_type}]: ")
        if new_type:
            updates["election_type"] = new_type
        new_start = prompt(f"Start Date [{poll.start_date}]: ")
        if new_start:
            _, _, err = self._polls.validate_poll_dates(
                new_start, poll.end_date
            )
            if not err:
                updates["start_date"] = new_start
            else:
                warning("Invalid date, keeping old value.")
        new_end = prompt(f"End Date [{poll.end_date}]: ")
        if new_end:
            start = updates.get("start_date", poll.start_date)
            _, _, err = self._polls.validate_poll_dates(start, new_end)
            if not err:
                updates["end_date"] = new_end
            else:
                warning("Invalid date, keeping old value.")

        self._polls.update_poll(
            pid, updates, self._store.current_user.username
        )
        print()
        success("Poll updated!")
        pause()

    def delete_poll(self):
        clear_screen()
        header("DELETE POLL", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} "
                  f"{DIM}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return
        if poll.is_open():
            error("Cannot delete an open poll. Close it first.")
            pause(); return
        if poll.total_votes_cast:
            warning(f"This poll has {poll.total_votes_cast} votes recorded.")
        if prompt(f"Confirm deletion of '{poll.title}'? "
                  "(yes/no): ").lower() == "yes":
            self._polls.delete_poll(
                pid, self._store.current_user.username
            )
            print()
            success(f"Poll '{poll.title}' deleted.")
        pause()

    def open_close_poll(self):
        clear_screen()
        header("OPEN / CLOSE POLL", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        for poll in polls.values():
            sc = self._poll_status_color(poll.status)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title}  "
                  f"{sc}{BOLD}{poll.status.upper()}{RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return

        username = self._store.current_user.username
        if poll.is_draft():
            if not poll.has_any_candidates():
                error("Cannot open - no candidates assigned.")
                pause(); return
            if prompt(f"Open poll '{poll.title}'? Voting will begin. "
                      "(yes/no): ").lower() == "yes":
                self._polls.open_poll(pid, username)
                print()
                success(f"Poll '{poll.title}' is now OPEN for voting!")
        elif poll.is_open():
            if prompt(f"Close poll '{poll.title}'? No more votes accepted. "
                      "(yes/no): ").lower() == "yes":
                self._polls.close_poll(pid, username)
                print()
                success(f"Poll '{poll.title}' is now CLOSED.")
        elif poll.is_closed():
            info("This poll is already closed.")
            if prompt("Reopen it? (yes/no): ").lower() == "yes":
                self._polls.reopen_poll(pid, username)
                print()
                success("Poll reopened!")
        pause()

    def assign_candidates(self):
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        if not self._candidates.get_all():
            print(); info("No candidates found."); pause(); return
        print()
        for poll in polls.values():
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} "
                  f"{DIM}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return
        if poll.is_open():
            error("Cannot modify candidates of an open poll.")
            pause(); return

        for idx, pos in enumerate(poll.positions):
            subheader(f"Position: {pos.position_title}",
                      THEME_ADMIN_ACCENT)
            current_cands = [
                f"{cid}: {self._store.candidates[cid].full_name}"
                for cid in pos.candidate_ids
                if cid in self._store.candidates
            ]
            if current_cands:
                print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
            else:
                info("No candidates assigned yet.")

            eligible = self._polls.get_eligible_candidates(pos.position_id)
            if not eligible:
                info("No eligible candidates found.")
                continue

            subheader("Available Candidates", THEME_ADMIN)
            for candidate in eligible.values():
                marker = (f" {GREEN}[ASSIGNED]{RESET}"
                          if candidate.id in pos.candidate_ids else "")
                print(f"    {THEME_ADMIN}{candidate.id}.{RESET} "
                      f"{candidate.full_name} {DIM}({candidate.party}) "
                      f"- Age: {candidate.age}, "
                      f"Edu: {candidate.education}{RESET}{marker}")

            if prompt(f"\nModify candidates for {pos.position_title}? "
                      "(yes/no): ").lower() == "yes":
                try:
                    new_ids = [
                        int(x.strip()) for x in
                        prompt("Enter Candidate IDs "
                               "(comma-separated): ").split(",")
                    ]
                    count = self._polls.assign_candidates_to_position(
                        pid, idx, new_ids,
                        self._store.current_user.username
                    )
                    success(f"{count} candidate(s) assigned.")
                except ValueError:
                    error("Invalid input. Skipping this position.")
        pause()

    # ── Helpers ──────────────────────────────────────────────

    def _display_poll_list(self, polls):
        """Print a compact numbered list of polls with status colour."""
        for poll in polls.values():
            sc = self._poll_status_color(poll.status)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} "
                  f"{sc}({poll.status}){RESET}")

    @staticmethod
    def _poll_status_color(status):
        """Return an ANSI colour code for the given poll status."""
        if status == POLL_STATUS_OPEN:
            return GREEN
        if status == POLL_STATUS_DRAFT:
            return YELLOW
        return RED
