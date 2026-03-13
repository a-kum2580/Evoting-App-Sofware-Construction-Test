"""
VoterUI — Voter dashboard and all voter-facing screens.

This module implements the voter's interface after they log in:
  1. View open polls — see which elections are available
  2. Cast vote — walk through each position and select a candidate
  3. View voting history — see past ballots and receipts
  4. View results — see outcomes of closed polls
  5. View profile — display personal information
  6. Change password — update login credentials

The voting flow (cast_vote) is the most complex screen:
  - The voter selects a poll
  - For each position in the poll, they see eligible candidates
  - They choose a candidate or abstain
  - A confirmation is shown before committing
  - A unique vote hash (receipt) is generated
"""

from e_voting.constants import (
    BAR_CHART_WIDTH, MIN_PASSWORD_LENGTH, MANIFESTO_PREVIEW_LENGTH,
    PROFILE_LABEL_WIDTH, ABSTAIN_CHOICE, FIRST_CANDIDATE_INDEX,
    PERCENTAGE_BASE, safe_percentage,
)
from e_voting.ui.console import (
    clear_screen, header, subheader, menu_item, prompt, masked_input,
    error, success, warning, info, status_badge, pause,
    THEME_VOTER, THEME_VOTER_ACCENT, BRIGHT_WHITE, BRIGHT_YELLOW,
    BRIGHT_GREEN, BRIGHT_CYAN, GREEN, YELLOW, RED, GRAY,
    DIM, RESET, BOLD, ITALIC, BLACK, BG_GREEN,
)


class VoterUI:
    """Voter-facing interface — polls, voting, results, and profile.

    Dependencies injected via constructor:
      - store: for session state and direct entity lookups
      - vote_service: for casting ballots and viewing voting history
      - result_service: for poll results and vote tallies
      - auth_service: for password hashing during password change
      - voter_service: for updating the voter's password in the store
    """

    def __init__(self, store, vote_service, result_service, auth_service,
                 voter_service):
        self._store = store
        self._votes = vote_service
        self._results = result_service
        self._auth = auth_service
        self._voter_service = voter_service

    def show_dashboard(self):
        """Main voter loop — displays the menu and routes to screens."""
        while True:
            clear_screen()
            header("VOTER DASHBOARD", THEME_VOTER)
            voter = self._store.current_user
            station = self._store.voting_stations.get(voter.station_id)
            station_name = station.name if station else "Unknown"
            print(f"  {THEME_VOTER}  ● {RESET}{BOLD}"
                  f"{voter.full_name}{RESET}")
            print(f"  {DIM}    Card: {voter.voter_card_number}  "
                  f"│  Station: {station_name}{RESET}")
            print()
            menu_item(1, "View Open Polls", THEME_VOTER)
            menu_item(2, "Cast Vote", THEME_VOTER)
            menu_item(3, "View My Voting History", THEME_VOTER)
            menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
            menu_item(5, "View My Profile", THEME_VOTER)
            menu_item(6, "Change Password", THEME_VOTER)
            menu_item(7, "Logout", THEME_VOTER)
            print()
            choice = prompt("Enter choice: ")

            if choice == "1":
                self._view_open_polls()
            elif choice == "2":
                self._cast_vote()
            elif choice == "3":
                self._view_voting_history()
            elif choice == "4":
                self._view_closed_results()
            elif choice == "5":
                self._view_profile()
            elif choice == "6":
                self._change_password()
            elif choice == "7":
                self._store.log_action(
                    "LOGOUT", voter.voter_card_number,
                    "Voter logged out"
                )
                self._store.save()
                break
            else:
                error("Invalid choice.")
                pause()

    def _view_open_polls(self):
        clear_screen()
        header("OPEN POLLS", THEME_VOTER)
        open_polls = self._votes.get_open_polls()
        voter = self._store.current_user
        if not open_polls:
            print(); info("No open polls at this time."); pause(); return

        for poll_id, poll in open_polls.items():
            already_voted = voter.has_voted_in_poll(poll_id)
            vote_status = (f" {GREEN}[VOTED]{RESET}" if already_voted
                           else f" {YELLOW}[NOT YET VOTED]{RESET}")
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll.id}: "
                  f"{poll.title}{RESET}{vote_status}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  "
                  f"{DIM}│  Period:{RESET} {poll.start_date} to "
                  f"{poll.end_date}")
            for pos in poll.positions:
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} "
                      f"{BOLD}{pos.position_title}{RESET}")
                for cid in pos.candidate_ids:
                    candidate = self._store.candidates.get(cid)
                    if candidate:
                        print(f"      {DIM}•{RESET} "
                              f"{candidate.full_name} "
                              f"{DIM}({candidate.party}) "
                              f"│ Age: {candidate.age} "
                              f"│ Edu: {candidate.education}{RESET}")
        pause()

    def _cast_vote(self):
        clear_screen()
        header("CAST YOUR VOTE", THEME_VOTER)
        voter = self._store.current_user
        available_polls = self._votes.get_available_polls(voter)
        if not available_polls:
            print()
            info("No available polls to vote in.")
            pause(); return

        subheader("Available Polls", THEME_VOTER_ACCENT)
        for poll in available_polls.values():
            print(f"  {THEME_VOTER}{poll.id}.{RESET} {poll.title} "
                  f"{DIM}({poll.election_type}){RESET}")
        try:
            pid = int(prompt("\nSelect Poll ID to vote: "))
        except ValueError:
            error("Invalid input."); pause(); return
        if pid not in available_polls:
            error("Invalid poll selection."); pause(); return

        poll = self._store.polls[pid]
        print()
        header(f"Voting: {poll.title}", THEME_VOTER)
        info("Please select ONE candidate for each position.\n")

        choices = []
        for pos in poll.positions:
            subheader(pos.position_title, THEME_VOTER_ACCENT)
            if not pos.candidate_ids:
                info("No candidates for this position.")
                continue

            for idx, cid in enumerate(pos.candidate_ids, 1):
                candidate = self._store.candidates.get(cid)
                if candidate:
                    print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} "
                          f"{candidate.full_name} "
                          f"{DIM}({candidate.party}){RESET}")
                    print(f"       {DIM}Age: {candidate.age} "
                          f"│ Edu: {candidate.education} "
                          f"│ Exp: {candidate.years_experience} "
                          f"yrs{RESET}")
                    if candidate.manifesto:
                        print(f"       {ITALIC}{DIM}"
                              f"{candidate.manifesto[:MANIFESTO_PREVIEW_LENGTH]}...{RESET}")
            print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")

            try:
                vote_choice = int(
                    prompt(f"\nYour choice for {pos.position_title}: ")
                )
            except ValueError:
                warning("Invalid input. Skipping.")
                vote_choice = ABSTAIN_CHOICE

            if vote_choice == ABSTAIN_CHOICE:
                choices.append({
                    "position_id": pos.position_id,
                    "position_title": pos.position_title,
                    "candidate_id": None,
                    "candidate_name": None,
                    "abstained": True,
                })
            elif FIRST_CANDIDATE_INDEX <= vote_choice <= len(pos.candidate_ids):
                selected_cid = pos.candidate_ids[vote_choice - 1]
                cand = self._store.candidates[selected_cid]
                choices.append({
                    "position_id": pos.position_id,
                    "position_title": pos.position_title,
                    "candidate_id": selected_cid,
                    "candidate_name": cand.full_name,
                    "abstained": False,
                })
            else:
                warning("Invalid choice. Marking as abstain.")
                choices.append({
                    "position_id": pos.position_id,
                    "position_title": pos.position_title,
                    "candidate_id": None,
                    "candidate_name": None,
                    "abstained": True,
                })

        subheader("VOTE SUMMARY", BRIGHT_WHITE)
        for choice in choices:
            if choice["abstained"]:
                print(f"  {choice['position_title']}: "
                      f"{GRAY}ABSTAINED{RESET}")
            else:
                print(f"  {choice['position_title']}: "
                      f"{BRIGHT_GREEN}{BOLD}"
                      f"{choice['candidate_name']}{RESET}")
        print()

        if prompt("Confirm your votes? This cannot be undone. "
                  "(yes/no): ").lower() != "yes":
            info("Vote cancelled.")
            pause(); return

        vote_hash = self._votes.cast_votes(voter, pid, choices)
        print()
        success("Your vote has been recorded successfully!")
        print(f"  {DIM}Vote Reference:{RESET} "
              f"{BRIGHT_YELLOW}{vote_hash}{RESET}")
        print(f"  {BRIGHT_CYAN}Thank you for participating in "
              f"the democratic process!{RESET}")
        pause()

    def _view_voting_history(self):
        clear_screen()
        header("MY VOTING HISTORY", THEME_VOTER)
        voter = self._store.current_user
        voted_polls = voter.has_voted_in
        if not voted_polls:
            print()
            info("You have not voted in any polls yet.")
            pause(); return

        print(f"\n  {DIM}You have voted in "
              f"{len(voted_polls)} poll(s):{RESET}\n")
        for pid in voted_polls:
            poll = self._store.polls.get(pid)
            if not poll:
                continue
            sc = GREEN if poll.is_open() else RED
            print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: "
                  f"{poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  "
                  f"{DIM}│  Status:{RESET} {sc}"
                  f"{poll.status.upper()}{RESET}")

            voter_votes = self._votes.get_voter_votes_in_poll(
                voter.id, pid
            )
            for vote_record in voter_votes:
                pos_title = "Unknown"
                for pos in poll.positions:
                    if pos.position_id == vote_record.position_id:
                        pos_title = pos.position_title
                        break
                if vote_record.abstained:
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} "
                          f"{pos_title}: {GRAY}ABSTAINED{RESET}")
                else:
                    cand = self._store.candidates.get(
                        vote_record.candidate_id
                    )
                    name = cand.full_name if cand else "Unknown"
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} "
                          f"{pos_title}: {BRIGHT_GREEN}{name}{RESET}")
            print()
        pause()

    def _view_closed_results(self):
        clear_screen()
        header("ELECTION RESULTS", THEME_VOTER)
        closed_polls = self._votes.get_closed_polls()
        if not closed_polls:
            print()
            info("No closed polls with results.")
            pause(); return

        for pid, poll in closed_polls.items():
            print(f"\n  {BOLD}{THEME_VOTER}{poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  "
                  f"{DIM}│  Votes:{RESET} {poll.total_votes_cast}")
            for pos in poll.positions:
                subheader(pos.position_title, THEME_VOTER_ACCENT)
                vote_counts, abstain_count, total = (
                    self._results.get_position_tally(pid, pos.position_id)
                )
                sorted_counts = sorted(
                    vote_counts.items(),
                    key=lambda x: x[1], reverse=True
                )
                for rank, (cid, count) in enumerate(sorted_counts, 1):
                    cand = self._store.candidates.get(cid)
                    pct = safe_percentage(count, total)
                    bar_len = int(pct * BAR_CHART_WIDTH / PERCENTAGE_BASE)
                    bar = (f"{THEME_VOTER}{'█' * bar_len}"
                           f"{GRAY}{'░' * (BAR_CHART_WIDTH - bar_len)}"
                           f"{RESET}")
                    winner = (
                        f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}"
                        if rank <= pos.max_winners else ""
                    )
                    name = cand.full_name if cand else "?"
                    party = cand.party if cand else "?"
                    print(f"    {BOLD}{rank}. {name}{RESET} "
                          f"{DIM}({party}){RESET}")
                    print(f"       {bar} {BOLD}{count}{RESET} "
                          f"({pct:.1f}%){winner}")
                if abstain_count:
                    pct = safe_percentage(abstain_count, total)
                    print(f"    {GRAY}Abstained: {abstain_count} "
                          f"({pct:.1f}%){RESET}")
        pause()

    def _view_profile(self):
        clear_screen()
        header("MY PROFILE", THEME_VOTER)
        voter = self._store.current_user
        station = self._store.voting_stations.get(voter.station_id)
        station_name = station.name if station else "Unknown"
        print()
        profile_fields = [
            ("Name", voter.full_name),
            ("National ID", voter.national_id),
            ("Voter Card",
             f"{BRIGHT_YELLOW}{voter.voter_card_number}{RESET}"),
            ("Date of Birth", voter.date_of_birth),
            ("Age", voter.age),
            ("Gender", voter.gender),
            ("Address", voter.address),
            ("Phone", voter.phone),
            ("Email", voter.email),
            ("Station", station_name),
            ("Verified",
             status_badge('Yes', True) if voter.is_verified
             else status_badge('No', False)),
            ("Registered", voter.registered_at),
            ("Polls Voted", len(voter.has_voted_in)),
        ]
        for label, value in profile_fields:
            print(f"  {THEME_VOTER}{label + ':':<{PROFILE_LABEL_WIDTH}}{RESET} {value}")
        pause()

    def _change_password(self):
        clear_screen()
        header("CHANGE PASSWORD", THEME_VOTER)
        print()
        voter = self._store.current_user
        old_pass = masked_input("Current Password: ").strip()
        if self._auth.hash_password(old_pass) != voter.password:
            error("Incorrect current password.")
            pause(); return
        new_pass = masked_input("New Password: ").strip()
        if len(new_pass) < MIN_PASSWORD_LENGTH:
            error(f"Password must be at least "
                  f"{MIN_PASSWORD_LENGTH} characters.")
            pause(); return
        confirm_pass = masked_input("Confirm New Password: ").strip()
        if new_pass != confirm_pass:
            error("Passwords do not match.")
            pause(); return

        new_hash = self._auth.hash_password(new_pass)
        self._voter_service.change_password(
            voter.id, new_hash, voter.voter_card_number
        )
        print()
        success("Password changed successfully!")
        pause()