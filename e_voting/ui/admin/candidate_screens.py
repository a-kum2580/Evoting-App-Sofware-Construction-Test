"""
CandidateScreens — Admin screens for candidate management.

Handles: create, view all, update, delete, and search candidates.
Delegates all business logic to CandidateService.
"""

from e_voting.constants import REQUIRED_EDUCATION_LEVELS, PREVIEW_MAX_LENGTH
from e_voting.ui.console import (
    clear_screen, header, subheader, table_header, table_divider,
    menu_item, prompt, error, success, warning, info, status_badge, pause,
    THEME_ADMIN, THEME_ADMIN_ACCENT, DIM, RESET, BOLD,
)


class CandidateScreens:
    """Admin UI screens for candidate CRUD and search."""

    def __init__(self, store, candidate_service):
        self._store = store
        self._candidates = candidate_service

    def create(self):
        clear_screen()
        header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty."); pause(); return
        national_id = prompt("National ID: ")
        if not national_id:
            error("National ID cannot be empty."); pause(); return
        if not self._candidates.is_national_id_unique(national_id):
            error("A candidate with this National ID already exists.")
            pause(); return

        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        age, age_err = self._candidates.validate_candidate_age(dob_str)
        if age_err:
            error(age_err); pause(); return

        gender = prompt("Gender (M/F/Other): ").upper()
        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(prompt("Select education level: "))
            first_option = 1
            if edu_choice < first_option or edu_choice > len(REQUIRED_EDUCATION_LEVELS):
                error("Invalid choice."); pause(); return
            education = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except ValueError:
            error("Invalid input."); pause(); return

        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: ")
        phone = prompt("Phone: ")
        email = prompt("Email: ")
        criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()
        if criminal_record == "yes":
            error("Candidates with criminal records are not eligible.")
            self._store.log_action(
                "CANDIDATE_REJECTED", self._store.current_user.username,
                f"Candidate {full_name} rejected - criminal record"
            )
            pause(); return

        years_exp_str = prompt(
            "Years of Public Service/Political Experience: "
        )
        try:
            years_experience = int(years_exp_str)
        except ValueError:
            default_experience = 0
            years_experience = default_experience

        candidate = self._candidates.create(
            full_name, national_id, dob_str, age, gender, education,
            party, manifesto, address, phone, email, years_experience,
            self._store.current_user.username
        )
        print()
        success(f"Candidate '{full_name}' created successfully! "
                f"ID: {candidate.id}")
        pause()

    def view_all(self):
        clear_screen()
        header("ALL CANDIDATES", THEME_ADMIN)
        candidates = self._candidates.get_all()
        if not candidates:
            print(); info("No candidates found."); pause(); return
        print()
        col_id, col_name, col_party, col_age, col_edu, col_status = 5, 25, 20, 5, 20, 10
        table_width = col_id + col_name + col_party + col_age + col_edu + col_status
        table_header(
            f"{'ID':<{col_id}} {'Name':<{col_name}} {'Party':<{col_party}} {'Age':<{col_age}} "
            f"{'Education':<{col_edu}} {'Status':<{col_status}}", THEME_ADMIN
        )
        table_divider(table_width, THEME_ADMIN)
        for candidate in candidates.values():
            status = (status_badge("Active", True) if candidate.is_active
                      else status_badge("Inactive", False))
            print(f"  {candidate.id:<{col_id}} {candidate.full_name:<{col_name}} "
                  f"{candidate.party:<{col_party}} {candidate.age:<{col_age}} "
                  f"{candidate.education:<{col_edu}} {status}")
        print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
        pause()

    def update(self):
        clear_screen()
        header("UPDATE CANDIDATE", THEME_ADMIN)
        candidates = self._candidates.get_all()
        if not candidates:
            print(); info("No candidates found."); pause(); return
        print()
        for candidate in candidates.values():
            print(f"  {THEME_ADMIN}{candidate.id}.{RESET} "
                  f"{candidate.full_name} {DIM}({candidate.party}){RESET}")
        try:
            cid = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError:
            error("Invalid input."); pause(); return
        candidate = self._candidates.get(cid)
        if not candidate:
            error("Candidate not found."); pause(); return

        print(f"\n  {BOLD}Updating: {candidate.full_name}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {}
        new_name = prompt(f"Full Name [{candidate.full_name}]: ")
        if new_name:
            updates["full_name"] = new_name
        new_party = prompt(f"Party [{candidate.party}]: ")
        if new_party:
            updates["party"] = new_party
        new_manifesto = prompt(
            f"Manifesto [{candidate.manifesto[:PREVIEW_MAX_LENGTH]}...]: "
        )
        if new_manifesto:
            updates["manifesto"] = new_manifesto
        new_phone = prompt(f"Phone [{candidate.phone}]: ")
        if new_phone:
            updates["phone"] = new_phone
        new_email = prompt(f"Email [{candidate.email}]: ")
        if new_email:
            updates["email"] = new_email
        new_address = prompt(f"Address [{candidate.address}]: ")
        if new_address:
            updates["address"] = new_address
        new_exp = prompt(
            f"Years Experience [{candidate.years_experience}]: "
        )
        if new_exp:
            try:
                updates["years_experience"] = int(new_exp)
            except ValueError:
                warning("Invalid number, keeping old value.")

        self._candidates.update(
            cid, updates, self._store.current_user.username
        )
        print()
        name = updates.get("full_name", candidate.full_name)
        success(f"Candidate '{name}' updated successfully!")
        pause()

    def delete(self):
        clear_screen()
        header("DELETE CANDIDATE", THEME_ADMIN)
        candidates = self._candidates.get_all()
        if not candidates:
            print(); info("No candidates found."); pause(); return
        print()
        for candidate in candidates.values():
            status = (status_badge("Active", True) if candidate.is_active
                      else status_badge("Inactive", False))
            print(f"  {THEME_ADMIN}{candidate.id}.{RESET} "
                  f"{candidate.full_name} {DIM}({candidate.party}){RESET} "
                  f"{status}")
        try:
            cid = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError:
            error("Invalid input."); pause(); return
        if not self._candidates.get(cid):
            error("Candidate not found."); pause(); return

        can_delete, reason = self._candidates.can_deactivate(cid)
        if not can_delete:
            error(reason); pause(); return

        candidate = self._candidates.get(cid)
        confirm = prompt(
            f"Are you sure you want to delete "
            f"'{candidate.full_name}'? (yes/no): "
        ).lower()
        if confirm == "yes":
            self._candidates.deactivate(
                cid, self._store.current_user.username
            )
            print()
            success(f"Candidate '{candidate.full_name}' has been deactivated.")
        else:
            info("Deletion cancelled.")
        pause()

    def search(self):
        clear_screen()
        header("SEARCH CANDIDATES", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Party", THEME_ADMIN)
        menu_item(3, "Education Level", THEME_ADMIN)
        menu_item(4, "Age Range", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        results = []
        if choice == "1":
            term = prompt("Enter name to search: ")
            results = self._candidates.search_by_name(term)
        elif choice == "2":
            term = prompt("Enter party name: ")
            results = self._candidates.search_by_party(term)
        elif choice == "3":
            subheader("Education Levels", THEME_ADMIN_ACCENT)
            for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
            try:
                edu_choice = int(prompt("Select: "))
                edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = self._candidates.search_by_education(edu)
            except (ValueError, IndexError):
                error("Invalid choice."); pause(); return
        elif choice == "4":
            try:
                min_age = int(prompt("Min age: "))
                max_age = int(prompt("Max age: "))
                results = self._candidates.search_by_age_range(
                    min_age, max_age
                )
            except ValueError:
                error("Invalid input."); pause(); return
        else:
            error("Invalid choice."); pause(); return

        if not results:
            print()
            info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            col_id, col_name, col_party, col_age, col_edu = 5, 25, 20, 5, 20
            table_width = col_id + col_name + col_party + col_age + col_edu
            table_header(
                f"{'ID':<{col_id}} {'Name':<{col_name}} {'Party':<{col_party}} {'Age':<{col_age}} "
                f"{'Education':<{col_edu}}", THEME_ADMIN
            )
            table_divider(table_width, THEME_ADMIN)
            for candidate in results:
                print(f"  {candidate.id:<{col_id}} {candidate.full_name:<{col_name}} "
                      f"{candidate.party:<{col_party}} {candidate.age:<{col_age}} "
                      f"{candidate.education:<{col_edu}}")
        pause() 