"""
AuthUI — Authentication and voter registration screens.

This module implements the three public-facing screens:
  1. Main login menu (admin login / voter login / voter registration)
  2. Admin login screen (username + password)
  3. Voter login screen (card number + password)
  4. Voter self-registration form

It delegates all business logic to the AuthService and only handles
user input collection and message display (Separation of Concerns).
"""

from e_voting.ui.console import (
    clear_screen, header, subheader, menu_item, prompt, masked_input,
    error, success, warning, info, pause,
    THEME_LOGIN, THEME_ADMIN, THEME_VOTER, BRIGHT_BLUE, BRIGHT_YELLOW,
    DIM, RESET, BOLD,
)


class AuthUI:
    """Handles the login menu, authentication screens, and voter registration.

    Dependencies are injected via the constructor (Dependency Inversion):
      - store: for session management and direct station lookups
      - auth_service: for credential verification and registration logic
    """

    def __init__(self, store, auth_service):
        self._store = store
        self._auth = auth_service

    def show_login_menu(self):
        """Shows the main login menu. Returns True if login succeeded."""
        clear_screen()
        header("E-VOTING SYSTEM", THEME_LOGIN)
        print()
        menu_item(1, "Login as Admin", THEME_LOGIN)
        menu_item(2, "Login as Voter", THEME_LOGIN)
        menu_item(3, "Register as Voter", THEME_LOGIN)
        menu_item(4, "Exit", THEME_LOGIN)
        print()
        choice = prompt("Enter choice: ")

        if choice == "1":
            return self._handle_admin_login()
        elif choice == "2":
            return self._handle_voter_login()
        elif choice == "3":
            self._handle_voter_registration()
            return False
        elif choice == "4":
            print()
            info("Goodbye!")
            self._store.save()
            exit()
        else:
            error("Invalid choice.")
            pause()
            return False

    def _handle_admin_login(self):
        clear_screen()
        header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = prompt("Username: ")
        password = masked_input("Password: ").strip()

        admin, err = self._auth.authenticate_admin(username, password)
        if err:
            error(err)
            pause()
            return False

        self._store.login(admin, "admin")
        print()
        success(f"Welcome, {admin.full_name}!")
        pause()
        return True

    def _handle_voter_login(self):
        clear_screen()
        header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = prompt("Voter Card Number: ")
        password = masked_input("Password: ").strip()

        voter, err = self._auth.authenticate_voter(voter_card, password)
        if err == "NOT_VERIFIED":
            warning("Your voter registration has not been verified yet.")
            info("Please contact an admin to verify your registration.")
            pause()
            return False
        if err:
            error(err)
            pause()
            return False

        self._store.login(voter, "voter")
        print()
        success(f"Welcome, {voter.full_name}!")
        pause()
        return True

    def _handle_voter_registration(self):
        clear_screen()
        header("VOTER REGISTRATION", THEME_VOTER)
        print()
        full_name = prompt("Full Name: ")
        national_id = prompt("National ID Number: ")
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        gender = prompt("Gender (M/F/Other): ").upper()
        address = prompt("Residential Address: ")
        phone = prompt("Phone Number: ")
        email = prompt("Email Address: ")
        password = masked_input("Create Password: ").strip()
        confirm_password = masked_input("Confirm Password: ").strip()

        validation_error = self._auth.validate_voter_registration(
            full_name, national_id, dob_str, gender,
            password, confirm_password
        )
        if validation_error:
            error(validation_error)
            pause()
            return

        active_stations = {
            sid: s for sid, s in self._store.voting_stations.items()
            if s.is_active
        }
        if not active_stations:
            error("No voting stations available. Contact admin.")
            pause()
            return

        subheader("Available Voting Stations", THEME_VOTER)
        for sid, station in active_stations.items():
            print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station.name} "
                  f"{DIM}- {station.location}{RESET}")

        try:
            station_choice = int(prompt("\nSelect your voting station ID: "))
            if (station_choice not in self._store.voting_stations
                    or not self._store.voting_stations[station_choice].is_active):
                error("Invalid station selection.")
                pause()
                return
        except ValueError:
            error("Invalid input.")
            pause()
            return

        voter, voter_card = self._auth.register_voter(
            full_name, national_id, dob_str, gender,
            address, phone, email, password, station_choice
        )
        print()
        success("Registration successful!")
        print(f"  {BOLD}Your Voter Card Number: "
              f"{BRIGHT_YELLOW}{voter_card}{RESET}")
        warning("IMPORTANT: Save this number! You need it to login.")
        info("Your registration is pending admin verification.")
        pause()
