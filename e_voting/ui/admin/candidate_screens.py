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

    