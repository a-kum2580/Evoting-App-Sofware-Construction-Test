"""Voter dashboard UI – poll viewing, voting, history, profile, password change."""
from ui.console import (
    clear_screen, header, subheader, menu_item, prompt, masked_input,
    error, success, warning, info, pause, status_badge,
    THEME_VOTER, THEME_VOTER_ACCENT, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_CYAN,
    GREEN, YELLOW, RED, GRAY, BLACK, BOLD, DIM, ITALIC, BG_GREEN, RESET,
)
from services.auth_service import AuthService


class VoterUI:
    def __init__(self, store, poll_svc, vote_svc, voter_svc, audit_svc,
                 candidate_svc, station_svc, persistence):
        self.store = store
        self.poll = poll_svc
        self.vote = vote_svc
        self.voter = voter_svc
        self.audit = audit_svc
        self.cand = candidate_svc
        self.station = station_svc
        self.persistence = persistence

    def _save(self):
        self.persistence.save_data(self.store)

    def _user(self):
        return self.store.current_user

    def run(self):
        while True:
            clear_screen(); header("VOTER DASHBOARD", THEME_VOTER)
            u = self._user()
            sn = self.station.get_by_id(u.station_id)
            station_name = sn.name if sn else "Unknown"
            print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{u.full_name}{RESET}")
            print(f"  {DIM}    Card: {u.voter_card_number}  │  Station: {station_name}{RESET}")
            print()
            menu_item(1,"View Open Polls",THEME_VOTER); menu_item(2,"Cast Vote",THEME_VOTER)
            menu_item(3,"View My Voting History",THEME_VOTER); menu_item(4,"View Results (Closed Polls)",THEME_VOTER)
            menu_item(5,"View My Profile",THEME_VOTER); menu_item(6,"Change Password",THEME_VOTER)
            menu_item(7,"Logout",THEME_VOTER)
            print()
            ch = prompt("Enter choice: ")
            if ch == "1": self._view_open_polls()
            elif ch == "2": self._cast_vote()
            elif ch == "3": self._view_history()
            elif ch == "4": self._view_closed_results()
            elif ch == "5": self._view_profile()
            elif ch == "6": self._change_password()
            elif ch == "7":
                self.audit.log("LOGOUT", u.voter_card_number, "Voter logged out"); self._save(); break
            else: error("Invalid choice."); pause()

    def _view_open_polls(self):
        clear_screen(); header("OPEN POLLS", THEME_VOTER)
        open_polls = self.poll.get_open_polls(); cands = self.cand.get_all()
        if not open_polls: print(); info("No open polls at this time."); pause(); return
        u = self._user()
        for pid, poll in open_polls.items():
            av = pid in u.has_voted_in
            vs = f" {GREEN}[VOTED]{RESET}" if av else f" {YELLOW}[NOT YET VOTED]{RESET}"
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll.id}: {poll.title}{RESET}{vs}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Period:{RESET} {poll.start_date} to {poll.end_date}")
            for pos in poll.positions:
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
                for ccid in pos["candidate_ids"]:
                    if ccid in cands:
                        c = cands[ccid]
                        print(f"      {DIM}•{RESET} {c.full_name} {DIM}({c.party}) │ Age: {c.age} │ Edu: {c.education}{RESET}")
        pause()

    def _cast_vote(self):
        clear_screen(); header("CAST YOUR VOTE", THEME_VOTER)
        u = self._user(); cands = self.cand.get_all()
        available = self.vote.get_available_polls_for_voter(u)
        if not available: print(); info("No available polls to vote in."); pause(); return
        subheader("Available Polls", THEME_VOTER_ACCENT)
        for pid, poll in available.items():
            print(f"  {THEME_VOTER}{poll.id}.{RESET} {poll.title} {DIM}({poll.election_type}){RESET}")
        try: pid = int(prompt("\nSelect Poll ID to vote: "))
        except ValueError: error("Invalid input."); pause(); return
        if pid not in available: error("Invalid poll selection."); pause(); return
        poll = self.poll.get_by_id(pid)
        print(); header(f"Voting: {poll.title}", THEME_VOTER)
        info("Please select ONE candidate for each position.\n")
        selections = []
        for pos in poll.positions:
            subheader(pos['position_title'], THEME_VOTER_ACCENT)
            if not pos["candidate_ids"]: info("No candidates for this position."); continue
            for idx, ccid in enumerate(pos["candidate_ids"], 1):
                if ccid in cands:
                    c = cands[ccid]
                    print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c.full_name} {DIM}({c.party}){RESET}")
                    print(f"       {DIM}Age: {c.age} │ Edu: {c.education} │ Exp: {c.years_experience} yrs{RESET}")
                    if c.manifesto: print(f"       {ITALIC}{DIM}{c.manifesto[:80]}...{RESET}")
            print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")
            try: vc = int(prompt(f"\nYour choice for {pos['position_title']}: "))
            except ValueError: warning("Invalid input. Skipping."); vc = 0
            if vc == 0:
                selections.append({"position_id": pos["position_id"], "candidate_id": None, "abstained": True,
                                    "position_title": pos["position_title"]})
            elif 1 <= vc <= len(pos["candidate_ids"]):
                sel_cid = pos["candidate_ids"][vc - 1]
                selections.append({"position_id": pos["position_id"], "candidate_id": sel_cid,
                                    "abstained": False, "position_title": pos["position_title"],
                                    "candidate_name": cands[sel_cid].full_name})
            else:
                warning("Invalid choice. Marking as abstain.")
                selections.append({"position_id": pos["position_id"], "candidate_id": None, "abstained": True,
                                    "position_title": pos["position_title"]})
        subheader("VOTE SUMMARY", RESET)
        for s in selections:
            if s["abstained"]: print(f"  {s['position_title']}: {GRAY}ABSTAINED{RESET}")
            else: print(f"  {s['position_title']}: {BRIGHT_GREEN}{BOLD}{s['candidate_name']}{RESET}")
        print()
        if prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
            info("Vote cancelled."); pause(); return
        vote_hash = self.vote.cast_votes(u, poll, selections)
        self.audit.log("CAST_VOTE", u.voter_card_number, f"Voted in poll: {poll.title} (Hash: {vote_hash})")
        print(); success("Your vote has been recorded successfully!")
        print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{vote_hash}{RESET}")
        print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
        self._save(); pause()

    def _view_history(self):
        clear_screen(); header("MY VOTING HISTORY", THEME_VOTER)
        u = self._user(); voted = u.has_voted_in; cands = self.cand.get_all()
        if not voted: print(); info("You have not voted in any polls yet."); pause(); return
        print(f"\n  {DIM}You have voted in {len(voted)} poll(s):{RESET}\n")
        for pid in voted:
            poll = self.poll.get_by_id(pid)
            if not poll: continue
            sc = GREEN if poll.status=='open' else RED
            print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Status:{RESET} {sc}{poll.status.upper()}{RESET}")
            for vr in self.vote.get_votes_for_voter_in_poll(u.id, pid):
                pt = next((p["position_title"] for p in poll.positions if p["position_id"] == vr.position_id), "Unknown")
                if vr.abstained: print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pt}: {GRAY}ABSTAINED{RESET}")
                else:
                    cn = cands.get(vr.candidate_id)
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pt}: {BRIGHT_GREEN}{cn.full_name if cn else 'Unknown'}{RESET}")
            print()
        pause()

    def _view_closed_results(self):
        clear_screen(); header("ELECTION RESULTS", THEME_VOTER)
        closed = self.poll.get_closed_polls(); cands = self.cand.get_all()
        if not closed: print(); info("No closed polls with results."); pause(); return
        for pid, poll in closed.items():
            print(f"\n  {BOLD}{THEME_VOTER}{poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Votes:{RESET} {poll.total_votes_cast}")
            for pos in poll.positions:
                subheader(pos['position_title'], THEME_VOTER_ACCENT)
                vc, ac, total = self.vote.tally_position(pid, pos["position_id"])
                for rank, (cid, count) in enumerate(sorted(vc.items(), key=lambda x: x[1], reverse=True), 1):
                    cand = cands.get(cid)
                    pct = (count / total * 100) if total > 0 else 0
                    bar = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                    winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank <= pos["max_winners"] else ""
                    print(f"    {BOLD}{rank}. {cand.full_name if cand else '?'}{RESET} {DIM}({cand.party if cand else '?'}){RESET}")
                    print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
                if ac > 0: print(f"    {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
        pause()

    def _view_profile(self):
        clear_screen(); header("MY PROFILE", THEME_VOTER)
        v = self._user()
        sn = self.station.get_by_id(v.station_id)
        station_name = sn.name if sn else "Unknown"
        print()
        for label, value in [
            ("Name", v.full_name), ("National ID", v.national_id),
            ("Voter Card", f"{BRIGHT_YELLOW}{v.voter_card_number}{RESET}"),
            ("Date of Birth", v.date_of_birth), ("Age", v.age), ("Gender", v.gender),
            ("Address", v.address), ("Phone", v.phone), ("Email", v.email),
            ("Station", station_name),
            ("Verified", status_badge('Yes', True) if v.is_verified else status_badge('No', False)),
            ("Registered", v.registered_at), ("Polls Voted", len(v.has_voted_in))]:
            print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
        pause()

    def _change_password(self):
        clear_screen(); header("CHANGE PASSWORD", THEME_VOTER); print()
        old = masked_input("Current Password: ").strip()
        if AuthService.hash_password(old) != self._user().password:
            error("Incorrect current password."); pause(); return
        new = masked_input("New Password: ").strip()
        if len(new) < 6: error("Password must be at least 6 characters."); pause(); return
        confirm = masked_input("Confirm New Password: ").strip()
        if new != confirm: error("Passwords do not match."); pause(); return
        new_hash = AuthService.hash_password(new)
        self._user().password = new_hash
        self.voter.change_password(self._user().id, new_hash)
        self.audit.log("CHANGE_PASSWORD", self._user().voter_card_number, "Password changed")
        print(); success("Password changed successfully!"); self._save(); pause()
