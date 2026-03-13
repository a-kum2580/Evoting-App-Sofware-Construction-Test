"""
ResultsScreens — Admin screens for results, statistics, and audit log.

Handles: view poll results, detailed statistics, audit log, station-wise results.
Delegates all business logic to ResultService and PollService.
"""

from e_voting.constants import (
    BAR_CHART_WIDTH, TURNOUT_HIGH_THRESHOLD, TURNOUT_MEDIUM_THRESHOLD,
    STATION_LOAD_WARNING_PERCENT, STATION_LOAD_CRITICAL_PERCENT,
    PERCENTAGE_BASE, AUDIT_LOG_DEFAULT_LIMIT, AUDIT_FILTER_LAST,
    AUDIT_FILTER_ACTION, AUDIT_FILTER_USER, TIMESTAMP_DISPLAY_LENGTH,
    DETAIL_MAX_DISPLAY_LENGTH, AGE_GROUP_LABEL_WIDTH, AGE_GROUP_COUNT_WIDTH,
    POLL_STATUS_OPEN, POLL_STATUS_DRAFT, safe_percentage,
)
from e_voting.ui.console import (
    clear_screen, header, subheader, table_header, table_divider,
    menu_item, prompt, error, info, pause,
    THEME_ADMIN, THEME_ADMIN_ACCENT, BRIGHT_WHITE,
    GREEN, YELLOW, RED, GRAY, DIM, RESET, BOLD, BLACK, BG_GREEN,
)


class ResultsScreens:
    """Admin UI screens for results, statistics, and audit trail."""

    def __init__(self, store, result_service, poll_service):
        self._store = store
        self._results = result_service
        self._polls = poll_service

    def view_poll_results(self):
        clear_screen()
        header("POLL RESULTS", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        self._display_poll_list(polls)
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return
        print()
        header(f"RESULTS: {poll.title}", THEME_ADMIN)
        sc = GREEN if poll.is_open() else RED
        print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll.status.upper()}"
              f"{RESET}  {DIM}│  Votes:{RESET} {BOLD}"
              f"{poll.total_votes_cast}{RESET}")

        turnout, eligible = self._results.calculate_turnout(poll)
        tc = (GREEN if turnout > TURNOUT_HIGH_THRESHOLD
              else (YELLOW if turnout > TURNOUT_MEDIUM_THRESHOLD else RED))
        print(f"  {DIM}Eligible:{RESET} {eligible}  "
              f"{DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")

        for pos in poll.positions:
            subheader(f"{pos.position_title} "
                      f"(Seats: {pos.max_winners})", THEME_ADMIN_ACCENT)
            vote_counts, abstain_count, total_pos = (
                self._results.get_position_tally(pid, pos.position_id)
            )
            sorted_counts = sorted(
                vote_counts.items(), key=lambda x: x[1], reverse=True
            )
            for rank, (cid, count) in enumerate(sorted_counts, 1):
                cand = self._store.candidates.get(cid)
                pct = safe_percentage(count, total_pos)
                bar_len = int(pct * BAR_CHART_WIDTH / PERCENTAGE_BASE)
                bar = (f"{THEME_ADMIN}{'█' * bar_len}"
                       f"{GRAY}{'░' * (BAR_CHART_WIDTH - bar_len)}{RESET}")
                winner = (f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}"
                          if rank <= pos.max_winners else "")
                name = cand.full_name if cand else "?"
                party = cand.party if cand else "?"
                print(f"    {BOLD}{rank}. {name}{RESET} "
                      f"{DIM}({party}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} "
                      f"({pct:.1f}%){winner}")
            if abstain_count:
                pct = safe_percentage(abstain_count, total_pos)
                print(f"    {GRAY}Abstained: {abstain_count} "
                      f"({pct:.1f}%){RESET}")
            if not vote_counts:
                info("    No votes recorded for this position.")
        pause()

    def view_detailed_statistics(self):
        clear_screen()
        header("DETAILED STATISTICS", THEME_ADMIN)

        stats = self._results.get_system_statistics()
        subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        print(f"  {THEME_ADMIN}Candidates:{RESET}  "
              f"{stats['total_candidates']} "
              f"{DIM}(Active: {stats['active_candidates']}){RESET}")
        print(f"  {THEME_ADMIN}Voters:{RESET}      "
              f"{stats['total_voters']} "
              f"{DIM}(Verified: {stats['verified_voters']}, "
              f"Active: {stats['active_voters']}){RESET}")
        print(f"  {THEME_ADMIN}Stations:{RESET}    "
              f"{stats['total_stations']} "
              f"{DIM}(Active: {stats['active_stations']}){RESET}")
        print(f"  {THEME_ADMIN}Polls:{RESET}       "
              f"{stats['total_polls']} "
              f"{DIM}({GREEN}Open: {stats['open_polls']}{RESET}{DIM}, "
              f"{RED}Closed: {stats['closed_polls']}{RESET}{DIM}, "
              f"{YELLOW}Draft: {stats['draft_polls']}{RESET}{DIM}){RESET}")
        print(f"  {THEME_ADMIN}Total Votes:{RESET} "
              f"{stats['total_votes']}")

        gender_counts, age_groups, total_voters = (
            self._results.get_voter_demographics()
        )
        subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        for gender, count in gender_counts.items():
            pct = safe_percentage(count, total_voters)
            print(f"    {gender}: {count} ({pct:.1f}%)")
        print(f"  {BOLD}Age Distribution:{RESET}")
        for group, count in age_groups.items():
            pct = safe_percentage(count, total_voters)
            bar_len = int(pct * BAR_CHART_WIDTH / PERCENTAGE_BASE)
            print(f"    {group:>{AGE_GROUP_LABEL_WIDTH}}: {count:>{AGE_GROUP_COUNT_WIDTH}} ({pct:>5.1f}%) "
                  f"{THEME_ADMIN}{'█' * bar_len}{RESET}")

        station_load = self._results.get_station_load()
        subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for entry in station_load:
            station = entry["station"]
            lp = entry["load_percent"]
            vc = entry["voter_count"]
            lc = (RED if lp > STATION_LOAD_CRITICAL_PERCENT
                  else (YELLOW if lp > STATION_LOAD_WARNING_PERCENT
                        else GREEN))
            st = (f"{RED}{BOLD}OVERLOADED{RESET}" if entry["is_overloaded"]
                  else f"{GREEN}OK{RESET}")
            print(f"    {station.name}: {vc}/{station.capacity} "
                  f"{lc}({lp:.0f}%){RESET} {st}")

        party_dist = self._results.get_party_distribution()
        subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
        for party, count in party_dist.items():
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")

        edu_dist = self._results.get_education_distribution()
        subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
        for edu, count in edu_dist.items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        pause()

    def view_audit_log(self):
        clear_screen()
        header("AUDIT LOG", THEME_ADMIN)
        audit_log = self._store.audit_log
        if not audit_log:
            print(); info("No audit records."); pause(); return
        print(f"\n  {DIM}Total Records: {len(audit_log)}{RESET}")
        subheader("Filter", THEME_ADMIN_ACCENT)
        menu_item(1, "Last 20 entries", THEME_ADMIN)
        menu_item(2, "All entries", THEME_ADMIN)
        menu_item(3, "Filter by action type", THEME_ADMIN)
        menu_item(4, "Filter by user", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        entries = audit_log
        if choice == "1":
            entries = self._results.get_audit_log(
                filter_type=AUDIT_FILTER_LAST, limit=AUDIT_LOG_DEFAULT_LIMIT
            )
        elif choice == "3":
            action_types = self._results.get_unique_action_types()
            for i, action_type in enumerate(action_types, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {action_type}")
            try:
                at_choice = int(prompt("Select action type: "))
                entries = self._results.get_audit_log(
                    filter_type=AUDIT_FILTER_ACTION,
                    filter_value=action_types[at_choice - 1]
                )
            except (ValueError, IndexError):
                error("Invalid choice."); pause(); return
        elif choice == "4":
            user_filter = prompt("Enter username/card number: ")
            entries = self._results.get_audit_log(
                filter_type=AUDIT_FILTER_USER, filter_value=user_filter
            )

        print()
        col_time, col_action, col_user, col_detail = 22, 25, 20, 33
        table_width = col_time + col_action + col_user + col_detail
        table_header(
            f"{'Timestamp':<{col_time}} {'Action':<{col_action}} {'User':<{col_user}} {'Details'}",
            THEME_ADMIN
        )
        table_divider(table_width, THEME_ADMIN)
        for entry in entries:
            action = entry["action"]
            if "CREATE" in action or action == "LOGIN":
                ac = GREEN
            elif "DELETE" in action or "DEACTIVATE" in action:
                ac = RED
            elif "UPDATE" in action:
                ac = YELLOW
            else:
                ac = RESET
            print(f"  {DIM}{entry['timestamp'][:TIMESTAMP_DISPLAY_LENGTH]}{RESET}  "
                  f"{ac}{action:<{col_action}}{RESET} {entry['user']:<{col_user}} "
                  f"{DIM}{entry['details'][:DETAIL_MAX_DISPLAY_LENGTH]}{RESET}")
        pause()

    def station_wise_results(self):
        clear_screen()
        header("STATION-WISE RESULTS", THEME_ADMIN)
        polls = self._polls.get_all_polls()
        if not polls:
            print(); info("No polls found."); pause(); return
        print()
        self._display_poll_list(polls)
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input."); pause(); return
        poll = self._polls.get_poll(pid)
        if not poll:
            error("Poll not found."); pause(); return

        print()
        header(f"STATION RESULTS: {poll.title}", THEME_ADMIN)
        station_data = self._results.get_station_results(pid)
        if not station_data:
            info("No station data available."); pause(); return

        for entry in station_data:
            station = entry["station"]
            subheader(f"{station.name}  ({station.location})",
                      BRIGHT_WHITE)
            tc = (GREEN if entry["turnout"] > TURNOUT_HIGH_THRESHOLD
                  else (YELLOW if entry["turnout"] > TURNOUT_MEDIUM_THRESHOLD
                        else RED))
            print(f"  {DIM}Registered:{RESET} {entry['registered']}  "
                  f"{DIM}│  Voted:{RESET} {entry['unique_voters']}  "
                  f"{DIM}│  Turnout:{RESET} {tc}{BOLD}"
                  f"{entry['turnout']:.1f}%{RESET}")

            for pos_result in entry["position_results"]:
                print(f"    {THEME_ADMIN_ACCENT}▸ "
                      f"{pos_result['position_title']}:{RESET}")
                total = pos_result["total"]
                sorted_counts = sorted(
                    pos_result["vote_counts"].items(),
                    key=lambda x: x[1], reverse=True
                )
                for cid, count in sorted_counts:
                    cand = self._store.candidates.get(cid)
                    pct = safe_percentage(count, total)
                    name = cand.full_name if cand else "?"
                    party = cand.party if cand else "?"
                    print(f"      {name} {DIM}({party}){RESET}: "
                          f"{BOLD}{count}{RESET} ({pct:.1f}%)")
                if pos_result["abstain_count"]:
                    ac = pos_result["abstain_count"]
                    pct = safe_percentage(ac, total)
                    print(f"      {GRAY}Abstained: {ac} "
                          f"({pct:.1f}%){RESET}")
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