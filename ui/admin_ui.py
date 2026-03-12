"""Admin dashboard UI – candidate, station, position, poll, voter, admin management, results."""
from ui.console import (
    clear_screen, header, subheader, menu_item, prompt, masked_input,
    error, success, warning, info, pause, table_header, table_divider, status_badge,
    THEME_ADMIN, THEME_ADMIN_ACCENT, THEME_VOTER, BRIGHT_WHITE, BRIGHT_YELLOW,
    BRIGHT_GREEN, BRIGHT_BLUE, GREEN, YELLOW, RED, GRAY, BLACK, BOLD, DIM, ITALIC,
    BG_GREEN, RESET,
)
from config import REQUIRED_EDUCATION_LEVELS, MIN_CANDIDATE_AGE


class AdminUI:
    def __init__(self, store, candidate_svc, station_svc, position_svc,
                 poll_svc, voter_svc, admin_svc, vote_svc, audit_svc, persistence):
        self.store = store
        self.cand = candidate_svc
        self.station = station_svc
        self.pos = position_svc
        self.poll = poll_svc
        self.voter = voter_svc
        self.admin = admin_svc
        self.vote = vote_svc
        self.audit = audit_svc
        self.persistence = persistence

    def _save(self):
        self.persistence.save_data(self.store)

    def _user(self):
        return self.store.current_user

    def run(self):
        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            u = self._user()
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{u.full_name}{RESET}  {DIM}│  Role: {u.role}{RESET}")
            subheader("Candidate Management", THEME_ADMIN_ACCENT)
            menu_item(1,"Create Candidate",THEME_ADMIN); menu_item(2,"View All Candidates",THEME_ADMIN)
            menu_item(3,"Update Candidate",THEME_ADMIN); menu_item(4,"Delete Candidate",THEME_ADMIN)
            menu_item(5,"Search Candidates",THEME_ADMIN)
            subheader("Voting Station Management", THEME_ADMIN_ACCENT)
            menu_item(6,"Create Voting Station",THEME_ADMIN); menu_item(7,"View All Stations",THEME_ADMIN)
            menu_item(8,"Update Station",THEME_ADMIN); menu_item(9,"Delete Station",THEME_ADMIN)
            subheader("Polls & Positions", THEME_ADMIN_ACCENT)
            menu_item(10,"Create Position",THEME_ADMIN); menu_item(11,"View Positions",THEME_ADMIN)
            menu_item(12,"Update Position",THEME_ADMIN); menu_item(13,"Delete Position",THEME_ADMIN)
            menu_item(14,"Create Poll",THEME_ADMIN); menu_item(15,"View All Polls",THEME_ADMIN)
            menu_item(16,"Update Poll",THEME_ADMIN); menu_item(17,"Delete Poll",THEME_ADMIN)
            menu_item(18,"Open/Close Poll",THEME_ADMIN); menu_item(19,"Assign Candidates to Poll",THEME_ADMIN)
            subheader("Voter Management", THEME_ADMIN_ACCENT)
            menu_item(20,"View All Voters",THEME_ADMIN); menu_item(21,"Verify Voter",THEME_ADMIN)
            menu_item(22,"Deactivate Voter",THEME_ADMIN); menu_item(23,"Search Voters",THEME_ADMIN)
            subheader("Admin Management", THEME_ADMIN_ACCENT)
            menu_item(24,"Create Admin Account",THEME_ADMIN); menu_item(25,"View Admins",THEME_ADMIN)
            menu_item(26,"Deactivate Admin",THEME_ADMIN)
            subheader("Results & Reports", THEME_ADMIN_ACCENT)
            menu_item(27,"View Poll Results",THEME_ADMIN); menu_item(28,"View Detailed Statistics",THEME_ADMIN)
            menu_item(29,"View Audit Log",THEME_ADMIN); menu_item(30,"Station-wise Results",THEME_ADMIN)
            subheader("System", THEME_ADMIN_ACCENT)
            menu_item(31,"Save Data",THEME_ADMIN); menu_item(32,"Logout",THEME_ADMIN)
            print()
            c = prompt("Enter choice: ")
            dispatch = {"1":self._create_candidate,"2":self._view_candidates,"3":self._update_candidate,
                "4":self._delete_candidate,"5":self._search_candidates,"6":self._create_station,
                "7":self._view_stations,"8":self._update_station,"9":self._delete_station,
                "10":self._create_position,"11":self._view_positions,"12":self._update_position,
                "13":self._delete_position,"14":self._create_poll,"15":self._view_polls,
                "16":self._update_poll,"17":self._delete_poll,"18":self._open_close_poll,
                "19":self._assign_candidates,"20":self._view_voters,"21":self._verify_voter,
                "22":self._deactivate_voter,"23":self._search_voters,"24":self._create_admin,
                "25":self._view_admins,"26":self._deactivate_admin,"27":self._view_results,
                "28":self._view_statistics,"29":self._view_audit_log,"30":self._station_results}
            if c == "31": self._save(); pause()
            elif c == "32":
                self.audit.log("LOGOUT", self._user().username, "Admin logged out"); self._save(); break
            elif c in dispatch: dispatch[c]()
            else: error("Invalid choice."); pause()

    # ── Candidate CRUD ────────────────────────────────────────────────
    def _create_candidate(self):
        clear_screen(); header("CREATE NEW CANDIDATE", THEME_ADMIN); print()
        full_name = prompt("Full Name: ")
        if not full_name: error("Name cannot be empty."); pause(); return
        national_id = prompt("National ID: ")
        if not national_id: error("National ID cannot be empty."); pause(); return
        if self.cand.national_id_exists(national_id):
            error("A candidate with this National ID already exists."); pause(); return
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        age, age_err = self.cand.calculate_age(dob_str)
        if age_err: error(age_err); pause(); return
        v_err = self.cand.validate_age(age)
        if v_err: error(v_err); pause(); return
        gender = prompt("Gender (M/F/Other): ").upper()
        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, lvl in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {lvl}")
        try:
            ec = int(prompt("Select education level: "))
            if ec < 1 or ec > len(REQUIRED_EDUCATION_LEVELS): error("Invalid choice."); pause(); return
            education = REQUIRED_EDUCATION_LEVELS[ec - 1]
        except ValueError: error("Invalid input."); pause(); return
        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: "); phone = prompt("Phone: "); email = prompt("Email: ")
        cr = prompt("Has Criminal Record? (yes/no): ").lower()
        if cr == "yes":
            error("Candidates with criminal records are not eligible.")
            self.audit.log("CANDIDATE_REJECTED", self._user().username,
                           f"Candidate {full_name} rejected - criminal record"); pause(); return
        yrs = prompt("Years of Public Service/Political Experience: ")
        try: yrs = int(yrs)
        except ValueError: yrs = 0
        c = self.cand.create(full_name, national_id, dob_str, age, gender, education,
                             party, manifesto, address, phone, email, False, yrs, self._user().username)
        self.audit.log("CREATE_CANDIDATE", self._user().username,
                       f"Created candidate: {full_name} (ID: {c.id})")
        print(); success(f"Candidate '{full_name}' created successfully! ID: {c.id}")
        self._save(); pause()

    def _view_candidates(self):
        clear_screen(); header("ALL CANDIDATES", THEME_ADMIN)
        cands = self.cand.get_all()
        if not cands: print(); info("No candidates found."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
        table_divider(85, THEME_ADMIN)
        for c in cands.values():
            st = status_badge("Active", True) if c.is_active else status_badge("Inactive", False)
            print(f"  {c.id:<5} {c.full_name:<25} {c.party:<20} {c.age:<5} {c.education:<20} {st}")
        print(f"\n  {DIM}Total Candidates: {len(cands)}{RESET}"); pause()

    def _update_candidate(self):
        clear_screen(); header("UPDATE CANDIDATE", THEME_ADMIN)
        cands = self.cand.get_all()
        if not cands: print(); info("No candidates found."); pause(); return
        print()
        for c in cands.values():
            print(f"  {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}){RESET}")
        try: cid = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError: error("Invalid input."); pause(); return
        c = self.cand.get_by_id(cid)
        if not c: error("Candidate not found."); pause(); return
        print(f"\n  {BOLD}Updating: {c.full_name}{RESET}"); info("Press Enter to keep current value\n")
        nn = prompt(f"Full Name [{c.full_name}]: "); np = prompt(f"Party [{c.party}]: ")
        nm = prompt(f"Manifesto [{c.manifesto[:50]}...]: "); nph = prompt(f"Phone [{c.phone}]: ")
        ne = prompt(f"Email [{c.email}]: "); na = prompt(f"Address [{c.address}]: ")
        nexp = prompt(f"Years Experience [{c.years_experience}]: ")
        exp_val = None
        if nexp:
            try: exp_val = int(nexp)
            except ValueError: warning("Invalid number, keeping old value.")
        self.cand.update(cid, full_name=nn or None, party=np or None,
                         manifesto=nm or None, phone=nph or None, email=ne or None,
                         address=na or None, years_experience=exp_val)
        self.audit.log("UPDATE_CANDIDATE", self._user().username,
                       f"Updated candidate: {c.full_name} (ID: {cid})")
        print(); success(f"Candidate '{c.full_name}' updated successfully!")
        self._save(); pause()

    def _delete_candidate(self):
        clear_screen(); header("DELETE CANDIDATE", THEME_ADMIN)
        cands = self.cand.get_all()
        if not cands: print(); info("No candidates found."); pause(); return
        print()
        for c in cands.values():
            st = status_badge("Active", True) if c.is_active else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}){RESET} {st}")
        try: cid = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError: error("Invalid input."); pause(); return
        if cid not in cands: error("Candidate not found."); pause(); return
        poll_title = self.cand.is_in_active_poll(cid)
        if poll_title: error(f"Cannot delete - candidate is in active poll: {poll_title}"); pause(); return
        confirm = prompt(f"Are you sure you want to delete '{cands[cid].full_name}'? (yes/no): ").lower()
        if confirm == "yes":
            name = cands[cid].full_name; self.cand.deactivate(cid)
            self.audit.log("DELETE_CANDIDATE", self._user().username, f"Deactivated candidate: {name} (ID: {cid})")
            print(); success(f"Candidate '{name}' has been deactivated."); self._save()
        else: info("Deletion cancelled.")
        pause()

    def _search_candidates(self):
        clear_screen(); header("SEARCH CANDIDATES", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1,"Name",THEME_ADMIN); menu_item(2,"Party",THEME_ADMIN)
        menu_item(3,"Education Level",THEME_ADMIN); menu_item(4,"Age Range",THEME_ADMIN)
        ch = prompt("\nChoice: "); results = []
        if ch == "1": results = self.cand.search_by_name(prompt("Enter name to search: "))
        elif ch == "2": results = self.cand.search_by_party(prompt("Enter party name: "))
        elif ch == "3":
            subheader("Education Levels", THEME_ADMIN_ACCENT)
            for i, lvl in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {lvl}")
            try:
                ec = int(prompt("Select: ")); results = self.cand.search_by_education(REQUIRED_EDUCATION_LEVELS[ec-1])
            except (ValueError, IndexError): error("Invalid choice."); pause(); return
        elif ch == "4":
            try: results = self.cand.search_by_age_range(int(prompt("Min age: ")), int(prompt("Max age: ")))
            except ValueError: error("Invalid input."); pause(); return
        else: error("Invalid choice."); pause(); return
        if not results: print(); info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", THEME_ADMIN)
            table_divider(75, THEME_ADMIN)
            for c in results:
                print(f"  {c.id:<5} {c.full_name:<25} {c.party:<20} {c.age:<5} {c.education:<20}")
        pause()

    # ── Station CRUD ──────────────────────────────────────────────────
    def _create_station(self):
        clear_screen(); header("CREATE VOTING STATION", THEME_ADMIN); print()
        name = prompt("Station Name: ")
        if not name: error("Name cannot be empty."); pause(); return
        location = prompt("Location/Address: ")
        if not location: error("Location cannot be empty."); pause(); return
        region = prompt("Region/District: ")
        try:
            cap = int(prompt("Voter Capacity: "))
            if cap <= 0: error("Capacity must be positive."); pause(); return
        except ValueError: error("Invalid capacity."); pause(); return
        sup = prompt("Station Supervisor Name: "); contact = prompt("Contact Phone: ")
        ot = prompt("Opening Time (e.g. 08:00): "); ct = prompt("Closing Time (e.g. 17:00): ")
        s = self.station.create(name, location, region, cap, sup, contact, ot, ct, self._user().username)
        self.audit.log("CREATE_STATION", self._user().username, f"Created station: {name} (ID: {s.id})")
        print(); success(f"Voting Station '{name}' created! ID: {s.id}")
        self._save(); pause()

    def _view_stations(self):
        clear_screen(); header("ALL VOTING STATIONS", THEME_ADMIN)
        stations = self.station.get_all()
        if not stations: print(); info("No voting stations found."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN)
        table_divider(96, THEME_ADMIN)
        for s in stations.values():
            rc = self.station.count_registered_voters(s.id)
            st = status_badge("Active", True) if s.is_active else status_badge("Inactive", False)
            print(f"  {s.id:<5} {s.name:<25} {s.location:<25} {s.region:<15} {s.capacity:<8} {rc:<8} {st}")
        print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}"); pause()

    def _update_station(self):
        clear_screen(); header("UPDATE VOTING STATION", THEME_ADMIN)
        stations = self.station.get_all()
        if not stations: print(); info("No stations found."); pause(); return
        print()
        for s in stations.values():
            print(f"  {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}- {s.location}{RESET}")
        try: sid = int(prompt("\nEnter Station ID to update: "))
        except ValueError: error("Invalid input."); pause(); return
        s = self.station.get_by_id(sid)
        if not s: error("Station not found."); pause(); return
        print(f"\n  {BOLD}Updating: {s.name}{RESET}"); info("Press Enter to keep current value\n")
        nn = prompt(f"Name [{s.name}]: "); nl = prompt(f"Location [{s.location}]: ")
        nr = prompt(f"Region [{s.region}]: "); nc = prompt(f"Capacity [{s.capacity}]: ")
        cap_val = None
        if nc:
            try: cap_val = int(nc)
            except ValueError: warning("Invalid number, keeping old value.")
        ns = prompt(f"Supervisor [{s.supervisor}]: "); nco = prompt(f"Contact [{s.contact}]: ")
        self.station.update(sid, name=nn or None, location=nl or None, region=nr or None,
                            capacity=cap_val, supervisor=ns or None, contact=nco or None)
        self.audit.log("UPDATE_STATION", self._user().username, f"Updated station: {s.name} (ID: {sid})")
        print(); success(f"Station '{s.name}' updated successfully!"); self._save(); pause()

    def _delete_station(self):
        clear_screen(); header("DELETE VOTING STATION", THEME_ADMIN)
        stations = self.station.get_all()
        if not stations: print(); info("No stations found."); pause(); return
        print()
        for s in stations.values():
            st = status_badge("Active", True) if s.is_active else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}({s.location}){RESET} {st}")
        try: sid = int(prompt("\nEnter Station ID to delete: "))
        except ValueError: error("Invalid input."); pause(); return
        if sid not in stations: error("Station not found."); pause(); return
        vc = self.station.count_registered_voters(sid)
        if vc > 0:
            warning(f"{vc} voters are registered at this station.")
            if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes": info("Cancelled."); pause(); return
        if prompt(f"Confirm deactivation of '{stations[sid].name}'? (yes/no): ").lower() == "yes":
            self.station.deactivate(sid)
            self.audit.log("DELETE_STATION", self._user().username, f"Deactivated station: {stations[sid].name}")
            print(); success(f"Station '{stations[sid].name}' deactivated."); self._save()
        else: info("Cancelled.")
        pause()

    # ── Position CRUD ─────────────────────────────────────────────────
    def _create_position(self):
        clear_screen(); header("CREATE POSITION", THEME_ADMIN); print()
        title = prompt("Position Title (e.g. President, Governor, Senator): ")
        if not title: error("Title cannot be empty."); pause(); return
        desc = prompt("Description: ")
        level = prompt("Level (National/Regional/Local): ")
        if level.lower() not in ("national","regional","local"): error("Invalid level."); pause(); return
        try:
            mw = int(prompt("Number of winners/seats: "))
            if mw <= 0: error("Must be at least 1."); pause(); return
        except ValueError: error("Invalid number."); pause(); return
        mca = prompt(f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: ")
        mca = int(mca) if mca.isdigit() else MIN_CANDIDATE_AGE
        p = self.pos.create(title, desc, level.capitalize(), mw, mca, self._user().username)
        self.audit.log("CREATE_POSITION", self._user().username, f"Created position: {title} (ID: {p.id})")
        print(); success(f"Position '{title}' created! ID: {p.id}"); self._save(); pause()

    def _view_positions(self):
        clear_screen(); header("ALL POSITIONS", THEME_ADMIN)
        positions = self.pos.get_all()
        if not positions: print(); info("No positions found."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}", THEME_ADMIN)
        table_divider(70, THEME_ADMIN)
        for p in positions.values():
            st = status_badge("Active", True) if p.is_active else status_badge("Inactive", False)
            print(f"  {p.id:<5} {p.title:<25} {p.level:<12} {p.max_winners:<8} {p.min_candidate_age:<10} {st}")
        print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}"); pause()

    def _update_position(self):
        clear_screen(); header("UPDATE POSITION", THEME_ADMIN)
        positions = self.pos.get_all()
        if not positions: print(); info("No positions found."); pause(); return
        print()
        for p in positions.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}){RESET}")
        try: pid = int(prompt("\nEnter Position ID to update: "))
        except ValueError: error("Invalid input."); pause(); return
        p = self.pos.get_by_id(pid)
        if not p: error("Position not found."); pause(); return
        print(f"\n  {BOLD}Updating: {p.title}{RESET}"); info("Press Enter to keep current value\n")
        nt = prompt(f"Title [{p.title}]: "); nd = prompt(f"Description [{p.description[:50]}]: ")
        nl = prompt(f"Level [{p.level}]: ")
        level_val = nl.capitalize() if nl and nl.lower() in ("national","regional","local") else None
        ns = prompt(f"Seats [{p.max_winners}]: ")
        seats_val = None
        if ns:
            try: seats_val = int(ns)
            except ValueError: warning("Keeping old value.")
        self.pos.update(pid, title=nt or None, description=nd or None,
                        level=level_val, max_winners=seats_val)
        self.audit.log("UPDATE_POSITION", self._user().username, f"Updated position: {p.title}")
        print(); success("Position updated!"); self._save(); pause()

    def _delete_position(self):
        clear_screen(); header("DELETE POSITION", THEME_ADMIN)
        positions = self.pos.get_all()
        if not positions: print(); info("No positions found."); pause(); return
        print()
        for p in positions.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}){RESET}")
        try: pid = int(prompt("\nEnter Position ID to delete: "))
        except ValueError: error("Invalid input."); pause(); return
        if pid not in positions: error("Position not found."); pause(); return
        pt = self.pos.is_in_active_poll(pid)
        if pt: error(f"Cannot delete - in active poll: {pt}"); pause(); return
        if prompt(f"Confirm deactivation of '{positions[pid].title}'? (yes/no): ").lower() == "yes":
            self.pos.deactivate(pid)
            self.audit.log("DELETE_POSITION", self._user().username, f"Deactivated position: {positions[pid].title}")
            print(); success("Position deactivated."); self._save()
        pause()

    # ── Poll CRUD ─────────────────────────────────────────────────────
    def _create_poll(self):
        clear_screen(); header("CREATE POLL / ELECTION", THEME_ADMIN); print()
        title = prompt("Poll/Election Title: ")
        if not title: error("Title cannot be empty."); pause(); return
        desc = prompt("Description: ")
        etype = prompt("Election Type (General/Primary/By-election/Referendum): ")
        sd = prompt("Start Date (YYYY-MM-DD): "); ed = prompt("End Date (YYYY-MM-DD): ")
        _, _, derr = self.poll.validate_dates(sd, ed)
        if derr: error(derr); pause(); return
        positions = self.pos.get_active()
        if not positions: error("No positions available. Create positions first."); pause(); return
        subheader("Available Positions", THEME_ADMIN_ACCENT)
        for p in positions.values():
            print(f"    {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}) - {p.max_winners} seat(s){RESET}")
        try: sel_pids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError: error("Invalid input."); pause(); return
        pp = []
        for spid in sel_pids:
            if spid not in positions: warning(f"Position ID {spid} not found or inactive. Skipping."); continue
            pp.append({"position_id": spid, "position_title": positions[spid].title,
                        "candidate_ids": [], "max_winners": positions[spid].max_winners})
        if not pp: error("No valid positions selected."); pause(); return
        stations = self.station.get_active()
        if not stations: error("No voting stations. Create stations first."); pause(); return
        subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        for s in stations.values():
            print(f"    {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}({s.location}){RESET}")
        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            sel_sids = list(stations.keys())
        else:
            try: sel_sids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError: error("Invalid input."); pause(); return
        poll = self.poll.create(title, desc, etype, sd, ed, pp, sel_sids, self._user().username)
        self.audit.log("CREATE_POLL", self._user().username, f"Created poll: {title} (ID: {poll.id})")
        print(); success(f"Poll '{title}' created! ID: {poll.id}")
        warning("Status: DRAFT - Assign candidates and then open the poll.")
        self._save(); pause()

    def _view_polls(self):
        clear_screen(); header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        polls = self.poll.get_all()
        if not polls: print(); info("No polls found."); pause(); return
        candidates = self.cand.get_all()
        for poll in polls.values():
            sc = GREEN if poll.status=='open' else (YELLOW if poll.status=='draft' else RED)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll.id}: {poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll.status.upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll.start_date} to {poll.end_date}  {DIM}│  Votes:{RESET} {poll.total_votes_cast}")
            for pos in poll.positions:
                cn = [candidates[ccid].full_name for ccid in pos["candidate_ids"] if ccid in candidates]
                cd = ', '.join(cn) if cn else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cd}")
        print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}"); pause()

    def _update_poll(self):
        clear_screen(); header("UPDATE POLL", THEME_ADMIN)
        polls = self.poll.get_all()
        if not polls: print(); info("No polls found."); pause(); return
        print()
        for p in polls.values():
            sc = GREEN if p.status=='open' else (YELLOW if p.status=='draft' else RED)
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {sc}({p.status}){RESET}")
        try: pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError: error("Invalid input."); pause(); return
        p = self.poll.get_by_id(pid)
        if not p: error("Poll not found."); pause(); return
        if p.status == "open": error("Cannot update an open poll. Close it first."); pause(); return
        if p.status == "closed" and p.total_votes_cast > 0: error("Cannot update a poll with votes."); pause(); return
        print(f"\n  {BOLD}Updating: {p.title}{RESET}"); info("Press Enter to keep current value\n")
        nt = prompt(f"Title [{p.title}]: "); nd = prompt(f"Description [{p.description[:50]}]: ")
        nty = prompt(f"Election Type [{p.election_type}]: ")
        nsd = prompt(f"Start Date [{p.start_date}]: ")
        if nsd and not self.poll.validate_single_date(nsd): warning("Invalid date, keeping old value."); nsd = ""
        ned = prompt(f"End Date [{p.end_date}]: ")
        if ned and not self.poll.validate_single_date(ned): warning("Invalid date, keeping old value."); ned = ""
        self.poll.update(pid, title=nt or None, description=nd or None, election_type=nty or None,
                         start_date=nsd or None, end_date=ned or None)
        self.audit.log("UPDATE_POLL", self._user().username, f"Updated poll: {p.title}")
        print(); success("Poll updated!"); self._save(); pause()

    def _delete_poll(self):
        clear_screen(); header("DELETE POLL", THEME_ADMIN)
        polls = self.poll.get_all()
        if not polls: print(); info("No polls found."); pause(); return
        print()
        for p in polls.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.status}){RESET}")
        try: pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError: error("Invalid input."); pause(); return
        p = self.poll.get_by_id(pid)
        if not p: error("Poll not found."); pause(); return
        if p.status == "open": error("Cannot delete an open poll. Close it first."); pause(); return
        if p.total_votes_cast > 0: warning(f"This poll has {p.total_votes_cast} votes recorded.")
        if prompt(f"Confirm deletion of '{p.title}'? (yes/no): ").lower() == "yes":
            title = p.title; self.poll.delete(pid)
            self.audit.log("DELETE_POLL", self._user().username, f"Deleted poll: {title}")
            print(); success(f"Poll '{title}' deleted."); self._save()
        pause()

    def _open_close_poll(self):
        clear_screen(); header("OPEN / CLOSE POLL", THEME_ADMIN)
        polls = self.poll.get_all()
        if not polls: print(); info("No polls found."); pause(); return
        print()
        for p in polls.values():
            sc = GREEN if p.status=='open' else (YELLOW if p.status=='draft' else RED)
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title}  {sc}{BOLD}{p.status.upper()}{RESET}")
        try: pid = int(prompt("\nEnter Poll ID: "))
        except ValueError: error("Invalid input."); pause(); return
        p = self.poll.get_by_id(pid)
        if not p: error("Poll not found."); pause(); return
        if p.status == "draft":
            if not self.poll.has_candidates_assigned(p):
                error("Cannot open - no candidates assigned."); pause(); return
            if prompt(f"Open poll '{p.title}'? Voting will begin. (yes/no): ").lower() == "yes":
                self.poll.open_poll(pid)
                self.audit.log("OPEN_POLL", self._user().username, f"Opened poll: {p.title}")
                print(); success(f"Poll '{p.title}' is now OPEN for voting!"); self._save()
        elif p.status == "open":
            if prompt(f"Close poll '{p.title}'? No more votes accepted. (yes/no): ").lower() == "yes":
                self.poll.close_poll(pid)
                self.audit.log("CLOSE_POLL", self._user().username, f"Closed poll: {p.title}")
                print(); success(f"Poll '{p.title}' is now CLOSED."); self._save()
        elif p.status == "closed":
            info("This poll is already closed.")
            if prompt("Reopen it? (yes/no): ").lower() == "yes":
                self.poll.open_poll(pid)
                self.audit.log("REOPEN_POLL", self._user().username, f"Reopened poll: {p.title}")
                print(); success("Poll reopened!"); self._save()
        pause()

    def _assign_candidates(self):
        clear_screen(); header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        polls = self.poll.get_all(); cands = self.cand.get_all()
        if not polls: print(); info("No polls found."); pause(); return
        if not cands: print(); info("No candidates found."); pause(); return
        print()
        for p in polls.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.status}){RESET}")
        try: pid = int(prompt("\nEnter Poll ID: "))
        except ValueError: error("Invalid input."); pause(); return
        p = self.poll.get_by_id(pid)
        if not p: error("Poll not found."); pause(); return
        if p.status == "open": error("Cannot modify candidates of an open poll."); pause(); return
        positions = self.pos.get_all()
        for i, pos in enumerate(p.positions):
            subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
            cur = [f"{ccid}: {cands[ccid].full_name}" for ccid in pos["candidate_ids"] if ccid in cands]
            if cur: print(f"  {DIM}Current:{RESET} {', '.join(cur)}")
            else: info("No candidates assigned yet.")
            active_c = {cid: c for cid, c in cands.items() if c.is_active and c.is_approved}
            pos_data = positions.get(pos["position_id"])
            min_age = pos_data.min_candidate_age if pos_data else MIN_CANDIDATE_AGE
            eligible = {cid: c for cid, c in active_c.items() if c.age >= min_age}
            if not eligible: info("No eligible candidates found."); continue
            subheader("Available Candidates", THEME_ADMIN)
            for c in eligible.values():
                marker = f" {GREEN}[ASSIGNED]{RESET}" if c.id in pos["candidate_ids"] else ""
                print(f"    {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}) - Age: {c.age}, Edu: {c.education}{RESET}{marker}")
            if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
                try:
                    new_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                    valid = []
                    for ncid in new_ids:
                        if ncid in eligible: valid.append(ncid)
                        else: warning(f"Candidate {ncid} not eligible. Skipping.")
                    pos["candidate_ids"] = valid; success(f"{len(valid)} candidate(s) assigned.")
                except ValueError: error("Invalid input. Skipping this position.")
        self.audit.log("ASSIGN_CANDIDATES", self._user().username, f"Updated candidates for poll: {p.title}")
        self._save(); pause()

    # ── Voter Management ──────────────────────────────────────────────
    def _view_voters(self):
        clear_screen(); header("ALL REGISTERED VOTERS", THEME_ADMIN)
        voters = self.voter.get_all()
        if not voters: print(); info("No voters registered."); pause(); return
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}", THEME_ADMIN)
        table_divider(70, THEME_ADMIN)
        for v in voters.values():
            ver = status_badge("Yes", True) if v.is_verified else status_badge("No", False)
            act = status_badge("Yes", True) if v.is_active else status_badge("No", False)
            print(f"  {v.id:<5} {v.full_name:<25} {v.voter_card_number:<15} {v.station_id:<6} {ver:<19} {act}")
        vc = self.voter.count_verified(); uc = self.voter.count_unverified()
        print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {vc}  │  Unverified: {uc}{RESET}"); pause()

    def _verify_voter(self):
        clear_screen(); header("VERIFY VOTER", THEME_ADMIN)
        unv = self.voter.get_unverified()
        if not unv: print(); info("No unverified voters."); pause(); return
        subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for v in unv.values():
            print(f"  {THEME_ADMIN}{v.id}.{RESET} {v.full_name} {DIM}│ NID: {v.national_id} │ Card: {v.voter_card_number}{RESET}")
        print(); menu_item(1,"Verify a single voter",THEME_ADMIN); menu_item(2,"Verify all pending voters",THEME_ADMIN)
        ch = prompt("\nChoice: ")
        if ch == "1":
            try: vid = int(prompt("Enter Voter ID: "))
            except ValueError: error("Invalid input."); pause(); return
            if vid not in self.voter.get_all(): error("Voter not found."); pause(); return
            v = self.voter.get_by_id(vid)
            if v.is_verified: info("Already verified."); pause(); return
            self.voter.verify(vid)
            self.audit.log("VERIFY_VOTER", self._user().username, f"Verified voter: {v.full_name}")
            print(); success(f"Voter '{v.full_name}' verified!"); self._save()
        elif ch == "2":
            count = self.voter.verify_all_pending()
            self.audit.log("VERIFY_ALL_VOTERS", self._user().username, f"Verified {count} voters")
            print(); success(f"{count} voters verified!"); self._save()
        pause()

    def _deactivate_voter(self):
        clear_screen(); header("DEACTIVATE VOTER", THEME_ADMIN)
        if not self.voter.get_all(): print(); info("No voters found."); pause(); return
        print()
        try: vid = int(prompt("Enter Voter ID to deactivate: "))
        except ValueError: error("Invalid input."); pause(); return
        v = self.voter.get_by_id(vid)
        if not v: error("Voter not found."); pause(); return
        if not v.is_active: info("Already deactivated."); pause(); return
        if prompt(f"Deactivate '{v.full_name}'? (yes/no): ").lower() == "yes":
            self.voter.deactivate(vid)
            self.audit.log("DEACTIVATE_VOTER", self._user().username, f"Deactivated voter: {v.full_name}")
            print(); success("Voter deactivated."); self._save()
        pause()

    def _search_voters(self):
        clear_screen(); header("SEARCH VOTERS", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1,"Name",THEME_ADMIN); menu_item(2,"Voter Card Number",THEME_ADMIN)
        menu_item(3,"National ID",THEME_ADMIN); menu_item(4,"Station",THEME_ADMIN)
        ch = prompt("\nChoice: "); results = []
        if ch == "1": results = self.voter.search_by_name(prompt("Name: "))
        elif ch == "2": results = self.voter.search_by_card(prompt("Card Number: "))
        elif ch == "3": results = self.voter.search_by_national_id(prompt("National ID: "))
        elif ch == "4":
            try: results = self.voter.search_by_station(int(prompt("Station ID: ")))
            except ValueError: error("Invalid input."); pause(); return
        else: error("Invalid choice."); pause(); return
        if not results: print(); info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for v in results:
                ver = status_badge("Verified", True) if v.is_verified else status_badge("Unverified", False)
                print(f"  {THEME_ADMIN}ID:{RESET} {v.id}  {DIM}│{RESET}  {v.full_name}  {DIM}│  Card:{RESET} {v.voter_card_number}  {DIM}│{RESET}  {ver}")
        pause()

    # ── Admin Management ──────────────────────────────────────────────
    def _create_admin(self):
        clear_screen(); header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
        if self._user().role != "super_admin":
            print(); error("Only super admins can create admin accounts."); pause(); return
        print()
        username = prompt("Username: ")
        if not username: error("Username cannot be empty."); pause(); return
        if self.admin.username_exists(username): error("Username already exists."); pause(); return
        full_name = prompt("Full Name: "); email = prompt("Email: ")
        password = masked_input("Password: ").strip()
        if len(password) < 6: error("Password must be at least 6 characters."); pause(); return
        subheader("Available Roles", THEME_ADMIN_ACCENT)
        menu_item(1,f"super_admin {DIM}─ Full access{RESET}",THEME_ADMIN)
        menu_item(2,f"election_officer {DIM}─ Manage polls and candidates{RESET}",THEME_ADMIN)
        menu_item(3,f"station_manager {DIM}─ Manage stations and verify voters{RESET}",THEME_ADMIN)
        menu_item(4,f"auditor {DIM}─ Read-only access{RESET}",THEME_ADMIN)
        rc = prompt("\nSelect role (1-4): ")
        if rc not in self.admin.ROLE_MAP: error("Invalid role."); pause(); return
        role = self.admin.ROLE_MAP[rc]
        a = self.admin.create(username, password, full_name, email, role)
        self.audit.log("CREATE_ADMIN", self._user().username, f"Created admin: {username} (Role: {role})")
        print(); success(f"Admin '{username}' created with role: {role}"); self._save(); pause()

    def _view_admins(self):
        clear_screen(); header("ALL ADMIN ACCOUNTS", THEME_ADMIN); print()
        table_header(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}", THEME_ADMIN)
        table_divider(78, THEME_ADMIN)
        for a in self.admin.get_all().values():
            act = status_badge("Yes", True) if a.is_active else status_badge("No", False)
            print(f"  {a.id:<5} {a.username:<20} {a.full_name:<25} {a.role:<20} {act}")
        print(f"\n  {DIM}Total Admins: {len(self.admin.get_all())}{RESET}"); pause()

    def _deactivate_admin(self):
        clear_screen(); header("DEACTIVATE ADMIN", THEME_ADMIN)
        if self._user().role != "super_admin":
            print(); error("Only super admins can deactivate admins."); pause(); return
        print()
        for a in self.admin.get_all().values():
            act = status_badge("Active", True) if a.is_active else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{a.id}.{RESET} {a.username} {DIM}({a.role}){RESET} {act}")
        try: aid = int(prompt("\nEnter Admin ID to deactivate: "))
        except ValueError: error("Invalid input."); pause(); return
        if aid not in self.admin.get_all(): error("Admin not found."); pause(); return
        if aid == self._user().id: error("Cannot deactivate your own account."); pause(); return
        if prompt(f"Deactivate '{self.admin.get_by_id(aid).username}'? (yes/no): ").lower() == "yes":
            self.admin.deactivate(aid)
            self.audit.log("DEACTIVATE_ADMIN", self._user().username,
                           f"Deactivated admin: {self.admin.get_by_id(aid).username}")
            print(); success("Admin deactivated."); self._save()
        pause()

    # ── Results & Reports ─────────────────────────────────────────────
    def _view_results(self):
        clear_screen(); header("POLL RESULTS", THEME_ADMIN)
        polls = self.poll.get_all(); cands = self.cand.get_all()
        if not polls: print(); info("No polls found."); pause(); return
        print()
        for p in polls.values():
            sc = GREEN if p.status=='open' else (YELLOW if p.status=='draft' else RED)
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {sc}({p.status}){RESET}")
        try: pid = int(prompt("\nEnter Poll ID: "))
        except ValueError: error("Invalid input."); pause(); return
        p = self.poll.get_by_id(pid)
        if not p: error("Poll not found."); pause(); return
        print(); header(f"RESULTS: {p.title}", THEME_ADMIN)
        sc = GREEN if p.status=='open' else RED
        print(f"  {DIM}Status:{RESET} {sc}{BOLD}{p.status.upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{p.total_votes_cast}{RESET}")
        te = self.vote.get_eligible_voter_count(p)
        turnout = (p.total_votes_cast / te * 100) if te > 0 else 0
        tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
        print(f"  {DIM}Eligible:{RESET} {te}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")
        for pos in p.positions:
            subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
            vc, ac, total = self.vote.tally_position(pid, pos["position_id"])
            for rank, (cid, count) in enumerate(sorted(vc.items(), key=lambda x: x[1], reverse=True), 1):
                cand = cands.get(cid)
                pct = (count / total * 100) if total > 0 else 0
                bl = int(pct / 2)
                bar = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.full_name if cand else '?'}{RESET} {DIM}({cand.party if cand else '?'}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if ac > 0: print(f"    {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
            if not vc: info("    No votes recorded for this position.")
        pause()

    def _view_statistics(self):
        clear_screen(); header("DETAILED STATISTICS", THEME_ADMIN)
        cands = self.cand.get_all(); voters = self.voter.get_all()
        stations = self.station.get_all(); polls = self.poll.get_all()
        subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        tc = len(cands); ac = sum(1 for c in cands.values() if c.is_active)
        tv = len(voters); vv = sum(1 for v in voters.values() if v.is_verified)
        av = sum(1 for v in voters.values() if v.is_active)
        ts = len(stations); ast = sum(1 for s in stations.values() if s.is_active)
        tp = len(polls)
        op = sum(1 for p in polls.values() if p.status=="open")
        cp = sum(1 for p in polls.values() if p.status=="closed")
        dp = sum(1 for p in polls.values() if p.status=="draft")
        print(f"  {THEME_ADMIN}Candidates:{RESET}  {tc} {DIM}(Active: {ac}){RESET}")
        print(f"  {THEME_ADMIN}Voters:{RESET}      {tv} {DIM}(Verified: {vv}, Active: {av}){RESET}")
        print(f"  {THEME_ADMIN}Stations:{RESET}    {ts} {DIM}(Active: {ast}){RESET}")
        print(f"  {THEME_ADMIN}Polls:{RESET}       {tp} {DIM}({GREEN}Open: {op}{RESET}{DIM}, {RED}Closed: {cp}{RESET}{DIM}, {YELLOW}Draft: {dp}{RESET}{DIM}){RESET}")
        print(f"  {THEME_ADMIN}Total Votes:{RESET} {len(self.store.votes)}")
        subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        gc = {}; ag = {"18-25":0,"26-35":0,"36-45":0,"46-55":0,"56-65":0,"65+":0}
        for v in voters.values():
            gc[v.gender] = gc.get(v.gender, 0) + 1
            a = v.age
            if a <= 25: ag["18-25"] += 1
            elif a <= 35: ag["26-35"] += 1
            elif a <= 45: ag["36-45"] += 1
            elif a <= 55: ag["46-55"] += 1
            elif a <= 65: ag["56-65"] += 1
            else: ag["65+"] += 1
        for g, count in gc.items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {g}: {count} ({pct:.1f}%)")
        print(f"  {BOLD}Age Distribution:{RESET}")
        for group, count in ag.items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")
        subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for s in stations.values():
            vc = self.station.count_registered_voters(s.id)
            lp = (vc / s.capacity * 100) if s.capacity > 0 else 0
            lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
            st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
            print(f"    {s.name}: {vc}/{s.capacity} {lc}({lp:.0f}%){RESET} {st}")
        subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
        pc = {}
        for c in cands.values():
            if c.is_active: pc[c.party] = pc.get(c.party, 0) + 1
        for party, count in sorted(pc.items(), key=lambda x: x[1], reverse=True):
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")
        subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
        ec = {}
        for c in cands.values():
            if c.is_active: ec[c.education] = ec.get(c.education, 0) + 1
        for edu, count in ec.items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        pause()

    def _station_results(self):
        clear_screen(); header("STATION-WISE RESULTS", THEME_ADMIN)
        polls = self.poll.get_all(); cands = self.cand.get_all()
        if not polls: print(); info("No polls found."); pause(); return
        print()
        for p in polls.values():
            sc = GREEN if p.status=='open' else (YELLOW if p.status=='draft' else RED)
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {sc}({p.status}){RESET}")
        try: pid = int(prompt("\nEnter Poll ID: "))
        except ValueError: error("Invalid input."); pause(); return
        p = self.poll.get_by_id(pid)
        if not p: error("Poll not found."); pause(); return
        print(); header(f"STATION RESULTS: {p.title}", THEME_ADMIN)
        stations = self.station.get_all(); voters = self.voter.get_all()
        for sid in p.station_ids:
            if sid not in stations: continue
            s = stations[sid]
            subheader(f"{s.name}  ({s.location})", BRIGHT_WHITE)
            svc = self.vote.count_station_voters(pid, sid)
            ras = sum(1 for v in voters.values() if v.station_id == sid and v.is_verified and v.is_active)
            st = (svc / ras * 100) if ras > 0 else 0
            tc = GREEN if st > 50 else (YELLOW if st > 25 else RED)
            print(f"  {DIM}Registered:{RESET} {ras}  {DIM}│  Voted:{RESET} {svc}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{st:.1f}%{RESET}")
            for pos in p.positions:
                print(f"    {THEME_ADMIN_ACCENT}▸ {pos['position_title']}:{RESET}")
                vc, ac, total = self.vote.tally_position_for_station(pid, pos["position_id"], sid)
                for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                    cand = cands.get(cid)
                    pct = (count / total * 100) if total > 0 else 0
                    print(f"      {cand.full_name if cand else '?'} {DIM}({cand.party if cand else '?'}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
                if ac > 0: print(f"      {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
        pause()

    def _view_audit_log(self):
        clear_screen(); header("AUDIT LOG", THEME_ADMIN)
        all_entries = self.audit.get_all()
        if not all_entries: print(); info("No audit records."); pause(); return
        print(f"\n  {DIM}Total Records: {len(all_entries)}{RESET}")
        subheader("Filter", THEME_ADMIN_ACCENT)
        menu_item(1,"Last 20 entries",THEME_ADMIN); menu_item(2,"All entries",THEME_ADMIN)
        menu_item(3,"Filter by action type",THEME_ADMIN); menu_item(4,"Filter by user",THEME_ADMIN)
        ch = prompt("\nChoice: ")
        entries = all_entries
        if ch == "1": entries = self.audit.get_last_n(20)
        elif ch == "3":
            action_types = self.audit.get_action_types()
            for i, at in enumerate(action_types, 1): print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
            try:
                atc = int(prompt("Select action type: "))
                entries = self.audit.filter_by_action(action_types[atc - 1])
            except (ValueError, IndexError): error("Invalid choice."); pause(); return
        elif ch == "4": entries = self.audit.filter_by_user(prompt("Enter username/card number: "))
        print()
        table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
        table_divider(100, THEME_ADMIN)
        for e in entries:
            ac = GREEN if "CREATE" in e.action or e.action == "LOGIN" else (RED if "DELETE" in e.action or "DEACTIVATE" in e.action else (YELLOW if "UPDATE" in e.action else RESET))
            print(f"  {DIM}{e.timestamp[:19]}{RESET}  {ac}{e.action:<25}{RESET} {e.user:<20} {DIM}{e.details[:50]}{RESET}")
        pause()
