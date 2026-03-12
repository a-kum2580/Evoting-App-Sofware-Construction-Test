"""Login and voter-registration screens."""

from ui.console import (
    clear_screen, header, subheader, menu_item, prompt, masked_input,
    error, success, warning, info, pause,
    THEME_LOGIN, THEME_ADMIN, THEME_VOTER,
    BRIGHT_BLUE, BRIGHT_YELLOW, BOLD, DIM, RESET,
)


class LoginUI:
    """Handles the main login menu and voter self-registration screen."""

    def __init__(self, store, auth_service, voter_service, station_service,
                 audit_service, persistence_module):
        self.store = store
        self.auth = auth_service
        self.voter_svc = voter_service
        self.station_svc = station_service
        self.audit = audit_service
        self.persistence = persistence_module

    # ------------------------------------------------------------------
    # Main login menu
    # ------------------------------------------------------------------
    def show(self):
        """
        Display the main login screen.

        Returns True and sets store.current_user / current_role on
        successful login.  Returns False otherwise.
        """
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
            return self._admin_login()
        elif choice == "2":
            return self._voter_login()
        elif choice == "3":
            self._register_voter()
            return False
        elif choice == "4":
            print()
            info("Goodbye!")
            self.persistence.save_data(self.store)
            exit()
        else:
            error("Invalid choice.")
            pause()
            return False

    # ------------------------------------------------------------------
    # Admin login
    # ------------------------------------------------------------------
    def _admin_login(self):
        clear_screen()
        header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = prompt("Username: ")
        password = masked_input("Password: ").strip()

        admin, err = self.auth.authenticate_admin(username, password)
        if admin:
            self.store.current_user = admin
            self.store.current_role = "admin"
            self.audit.log("LOGIN", username, "Admin login successful")
            print()
            success(f"Welcome, {admin.full_name}!")
            pause()
            return True

        error(err)
        if "deactivated" in (err or ""):
            self.audit.log("LOGIN_FAILED", username, "Account deactivated")
        else:
            self.audit.log("LOGIN_FAILED", username, "Invalid admin credentials")
        pause()
        return False

    # ------------------------------------------------------------------
    # Voter login
    # ------------------------------------------------------------------
    def _voter_login(self):
        clear_screen()
        header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = prompt("Voter Card Number: ")
        password = masked_input("Password: ").strip()

        voter, err = self.auth.authenticate_voter(voter_card, password)
        if voter:
            self.store.current_user = voter
            self.store.current_role = "voter"
            self.audit.log("LOGIN", voter_card, "Voter login successful")
            print()
            success(f"Welcome, {voter.full_name}!")
            pause()
            return True

        if err == "NOT_VERIFIED":
            warning("Your voter registration has not been verified yet.")
            info("Please contact an admin to verify your registration.")
            self.audit.log("LOGIN_FAILED", voter_card, "Voter not verified")
        elif "deactivated" in (err or ""):
            error("This voter account has been deactivated.")
            self.audit.log("LOGIN_FAILED", voter_card, "Voter account deactivated")
        else:
            error("Invalid voter card number or password.")
            self.audit.log("LOGIN_FAILED", voter_card, "Invalid voter credentials")
        pause()
        return False

    # ------------------------------------------------------------------
    # Voter self-registration
    # ------------------------------------------------------------------
    def _register_voter(self):
        clear_screen()
        header("VOTER REGISTRATION", THEME_VOTER)
        print()

        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty."); pause(); return

        national_id = prompt("National ID Number: ")
        if not national_id:
            error("National ID cannot be empty."); pause(); return
        if self.voter_svc.national_id_exists(national_id):
            error("A voter with this National ID already exists."); pause(); return

        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        age, age_err = self.voter_svc.validate_dob(dob_str)
        if age_err:
            error(age_err); pause(); return

        gender = prompt("Gender (M/F/Other): ").upper()
        if gender not in ("M", "F", "OTHER"):
            error("Invalid gender selection."); pause(); return

        address = prompt("Residential Address: ")
        phone = prompt("Phone Number: ")
        email = prompt("Email Address: ")

        password = masked_input("Create Password: ").strip()
        if len(password) < 6:
            error("Password must be at least 6 characters."); pause(); return
        confirm_password = masked_input("Confirm Password: ").strip()
        if password != confirm_password:
            error("Passwords do not match."); pause(); return

        active_stations = self.station_svc.get_active()
        if not active_stations:
            error("No voting stations available. Contact admin."); pause(); return

        subheader("Available Voting Stations", THEME_VOTER)
        for sid, station in active_stations.items():
            print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station.name} "
                  f"{DIM}- {station.location}{RESET}")

        try:
            station_choice = int(prompt("\nSelect your voting station ID: "))
            if station_choice not in active_stations:
                error("Invalid station selection."); pause(); return
        except ValueError:
            error("Invalid input."); pause(); return

        voter = self.voter_svc.register(
            full_name=full_name,
            national_id=national_id,
            dob_str=dob_str,
            age=age,
            gender=gender,
            address=address,
            phone=phone,
            email=email,
            password=password,
            station_id=station_choice,
        )

        self.audit.log("REGISTER", full_name,
                       f"New voter registered with card: {voter.voter_card_number}")
        print()
        success("Registration successful!")
        print(f"  {BOLD}Your Voter Card Number: "
              f"{BRIGHT_YELLOW}{voter.voter_card_number}{RESET}")
        warning("IMPORTANT: Save this number! You need it to login.")
        info("Your registration is pending admin verification.")
        self.persistence.save_data(self.store)
        pause()
