import datetime
import hashlib
import random
import string
import json
import os
import time
import sys


if sys.platform == "win32":
    os.system("")

### base colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

### foreground
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

## backgrounds
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
BG_GRAY = "\033[100m"


### theme colors per context
THEME_LOGIN = BRIGHT_CYAN
THEME_ADMIN = BRIGHT_GREEN
THEME_ADMIN_ACCENT = YELLOW
THEME_VOTER = BRIGHT_BLUE
THEME_VOTER_ACCENT = MAGENTA


def colored(text, color):
    return f"{color}{text}{RESET}"


def header(title, theme_color):
    width = 58
    top = f"  {theme_color}{'═' * width}{RESET}"
    mid = f"  {theme_color}{BOLD} {title.center(width - 2)} {RESET}{theme_color} {RESET}"
    bot = f"  {theme_color}{'═' * width}{RESET}"
    print(top)
    print(mid)
    print(bot)


def subheader(title, theme_color):
    print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")


def table_header(format_str, theme_color):
    print(f"  {theme_color}{BOLD}{format_str}{RESET}")


def table_divider(width, theme_color):
    print(f"  {theme_color}{'─' * width}{RESET}")


def error(msg):
    print(f"  {RED}{BOLD} {msg}{RESET}")


def success(msg):
    print(f"  {GREEN}{BOLD} {msg}{RESET}")


def warning(msg):
    print(f"  {YELLOW}{BOLD} {msg}{RESET}")


def info(msg):
    print(f"  {GRAY}{msg}{RESET}")


def menu_item(number, text, color):
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def status_badge(text, is_good):
    if is_good:
        return f"{GREEN}{text}{RESET}"
    return f"{RED}{text}{RESET}"


def prompt(text):
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text="Password: "):
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""
    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch == "\r" or ch == "\n":
                print()
                break
            elif ch == "\x08" or ch == "\b":
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{YELLOW}*{RESET}")
                sys.stdout.flush()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch == "\r" or ch == "\n":
                    print()
                    break
                elif ch == "\x7f" or ch == "\x08":
                    if len(password) > 0:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{YELLOW}*{RESET}")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return password


### Data storage
candidates = {}
candidate_id_counter = 1
voting_stations = {}
station_id_counter = 1
polls = {}
poll_id_counter = 1
positions = {}
position_id_counter = 1
voters = {}
voter_id_counter = 1
admins = {}
admin_id_counter = 1
votes = []
audit_log = []
current_user = None
current_role = None

MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
REQUIRED_EDUCATION_LEVELS = ["Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"]
MIN_VOTER_AGE = 18

admins[1] = {
    "id": 1, "username": "admin",
    "password": hashlib.sha256("admin123".encode()).hexdigest(),
    "full_name": "System Administrator", "email": "admin@evote.com",
    "role": "super_admin", "created_at": str(datetime.datetime.now()), "is_active": True
}
admin_id_counter = 2


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input(f"\n  {DIM}Press Enter to continue...{RESET}")

def generate_voter_card_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def log_action(action, user, details):
    audit_log.append({"timestamp": str(datetime.datetime.now()), "action": action, "user": user, "details": details})

def save_data():
    data = {
        "candidates": candidates, "candidate_id_counter": candidate_id_counter,
        "voting_stations": voting_stations, "station_id_counter": station_id_counter,
        "polls": polls, "poll_id_counter": poll_id_counter,
        "positions": positions, "position_id_counter": position_id_counter,
        "voters": voters, "voter_id_counter": voter_id_counter,
        "admins": admins, "admin_id_counter": admin_id_counter,
        "votes": votes, "audit_log": audit_log
    }
    try:
        with open("evoting_data.json", "w") as f:
            json.dump(data, f, indent=2)
        info("Data saved successfully")
    except Exception as e:
        error(f"Error saving data: {e}")

def load_data():
    global candidates, candidate_id_counter, voting_stations, station_id_counter
    global polls, poll_id_counter, positions, position_id_counter
    global voters, voter_id_counter, admins, admin_id_counter, votes, audit_log
    try:
        if os.path.exists("evoting_data.json"):
            with open("evoting_data.json", "r") as f:
                data = json.load(f)
            candidates = {int(k): v for k, v in data.get("candidates", {}).items()}
            candidate_id_counter = data.get("candidate_id_counter", 1)
            voting_stations = {int(k): v for k, v in data.get("voting_stations", {}).items()}
            station_id_counter = data.get("station_id_counter", 1)
            polls = {int(k): v for k, v in data.get("polls", {}).items()}
            poll_id_counter = data.get("poll_id_counter", 1)
            positions = {int(k): v for k, v in data.get("positions", {}).items()}
            position_id_counter = data.get("position_id_counter", 1)
            voters = {int(k): v for k, v in data.get("voters", {}).items()}
            voter_id_counter = data.get("voter_id_counter", 1)
            admins = {int(k): v for k, v in data.get("admins", {}).items()}
            admin_id_counter = data.get("admin_id_counter", 1)
            votes = data.get("votes", [])
            audit_log = data.get("audit_log", [])
            info("Data loaded successfully")
    except Exception as e:
        error(f"Error loading data: {e}")


### login 
def login():
    global current_user, current_role
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
        clear_screen()
        header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = prompt("Username: ")
        password = masked_input("Password: ").strip()
        hashed = hash_password(password)
        found = False
        for aid, admin in admins.items():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    error("This account has been deactivated.")
                    log_action("LOGIN_FAILED", username, "Account deactivated")
                    pause()
                    return False
                current_user = admin
                current_role = "admin"
                found = True
                log_action("LOGIN", username, "Admin login successful")
                print()
                success(f"Welcome, {admin['full_name']}!")
                pause()
                return True
        if not found:
            error("Invalid credentials.")
            log_action("LOGIN_FAILED", username, "Invalid admin credentials")
            pause()
            return False

    elif choice == "2":
        clear_screen()
        header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = prompt("Voter Card Number: ")
        password = masked_input("Password: ").strip()
        hashed = hash_password(password)
        found = False
        for vid, voter in voters.items():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    error("This voter account has been deactivated.")
                    log_action("LOGIN_FAILED", voter_card, "Voter account deactivated")
                    pause()
                    return False
                if not voter["is_verified"]:
                    warning("Your voter registration has not been verified yet.")
                    info("Please contact an admin to verify your registration.")
                    log_action("LOGIN_FAILED", voter_card, "Voter not verified")
                    pause()
                    return False
                current_user = voter
                current_role = "voter"
                found = True
                log_action("LOGIN", voter_card, "Voter login successful")
                print()
                success(f"Welcome, {voter['full_name']}!")
                pause()
                return True
        if not found:
            error("Invalid voter card number or password.")
            log_action("LOGIN_FAILED", voter_card, "Invalid voter credentials")
            pause()
            return False

    elif choice == "3":
        register_voter()
        return False
    elif choice == "4":
        print()
        info("Goodbye!")
        save_data()
        exit()
    else:
        error("Invalid choice.")
        pause()
        return False


def register_voter():
    global voter_id_counter
    clear_screen()
    header("VOTER REGISTRATION", THEME_VOTER)
    print()
    full_name = prompt("Full Name: ")
    if not full_name:
        error("Name cannot be empty.")
        pause()
        return
    national_id = prompt("National ID Number: ")
    if not national_id:
        error("National ID cannot be empty.")
        pause()
        return
    for vid, v in voters.items():
        if v["national_id"] == national_id:
            error("A voter with this National ID already exists.")
            pause()
            return
    dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
    try:
        dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
        age = (datetime.datetime.now() - dob).days // 365
        if age < MIN_VOTER_AGE:
            error(f"You must be at least {MIN_VOTER_AGE} years old to register.")
            pause()
            return
    except ValueError:
        error("Invalid date format.")
        pause()
        return
    gender = prompt("Gender (M/F/Other): ").upper()
    if gender not in ["M", "F", "OTHER"]:
        error("Invalid gender selection.")
        pause()
        return
    address = prompt("Residential Address: ")
    phone = prompt("Phone Number: ")
    email = prompt("Email Address: ")
    password = masked_input("Create Password: ").strip()
    if len(password) < 6:
        error("Password must be at least 6 characters.")
        pause()
        return
    confirm_password = masked_input("Confirm Password: ").strip()
    if password != confirm_password:
        error("Passwords do not match.")
        pause()
        return
    if not voting_stations:
        error("No voting stations available. Contact admin.")
        pause()
        return
    subheader("Available Voting Stations", THEME_VOTER)
    for sid, station in voting_stations.items():
        if station["is_active"]:
            print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")
    try:
        station_choice = int(prompt("\nSelect your voting station ID: "))
        if station_choice not in voting_stations or not voting_stations[station_choice]["is_active"]:
            error("Invalid station selection.")
            pause()
            return
    except ValueError:
        error("Invalid input.")
        pause()
        return
    voter_card = generate_voter_card_number()
    voters[voter_id_counter] = {
        "id": voter_id_counter, "full_name": full_name, "national_id": national_id,
        "date_of_birth": dob_str, "age": age, "gender": gender, "address": address,
        "phone": phone, "email": email, "password": hash_password(password),
        "voter_card_number": voter_card, "station_id": station_choice,
        "is_verified": False, "is_active": True, "has_voted_in": [],
        "registered_at": str(datetime.datetime.now()), "role": "voter"
    }
    log_action("REGISTER", full_name, f"New voter registered with card: {voter_card}")
    print()
    success("Registration successful!")
    print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
    warning("IMPORTANT: Save this number! You need it to login.")
    info("Your registration is pending admin verification.")
    voter_id_counter += 1
    save_data()
    pause()


### Admin
def admin_dashboard():
    while True:
        clear_screen()
        header("ADMIN DASHBOARD", THEME_ADMIN)
        print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}  {DIM}│  Role: {current_user['role']}{RESET}")

        subheader("Candidate Management", THEME_ADMIN_ACCENT)
        menu_item(1, "Create Candidate", THEME_ADMIN)
        menu_item(2, "View All Candidates", THEME_ADMIN)
        menu_item(3, "Update Candidate", THEME_ADMIN)
        menu_item(4, "Delete Candidate", THEME_ADMIN)
        menu_item(5, "Search Candidates", THEME_ADMIN)

        subheader("Voting Station Management", THEME_ADMIN_ACCENT)
        menu_item(6, "Create Voting Station", THEME_ADMIN)
        menu_item(7, "View All Stations", THEME_ADMIN)
        menu_item(8, "Update Station", THEME_ADMIN)
        menu_item(9, "Delete Station", THEME_ADMIN)

        subheader("Polls & Positions", THEME_ADMIN_ACCENT)
        menu_item(10, "Create Position", THEME_ADMIN)
        menu_item(11, "View Positions", THEME_ADMIN)
        menu_item(12, "Update Position", THEME_ADMIN)
        menu_item(13, "Delete Position", THEME_ADMIN)
        menu_item(14, "Create Poll", THEME_ADMIN)
        menu_item(15, "View All Polls", THEME_ADMIN)
        menu_item(16, "Update Poll", THEME_ADMIN)
        menu_item(17, "Delete Poll", THEME_ADMIN)
        menu_item(18, "Open/Close Poll", THEME_ADMIN)
        menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)

        subheader("Voter Management", THEME_ADMIN_ACCENT)
        menu_item(20, "View All Voters", THEME_ADMIN)
        menu_item(21, "Verify Voter", THEME_ADMIN)
        menu_item(22, "Deactivate Voter", THEME_ADMIN)
        menu_item(23, "Search Voters", THEME_ADMIN)

        subheader("Admin Management", THEME_ADMIN_ACCENT)
        menu_item(24, "Create Admin Account", THEME_ADMIN)
        menu_item(25, "View Admins", THEME_ADMIN)
        menu_item(26, "Deactivate Admin", THEME_ADMIN)

        subheader("Results & Reports", THEME_ADMIN_ACCENT)
        menu_item(27, "View Poll Results", THEME_ADMIN)
        menu_item(28, "View Detailed Statistics", THEME_ADMIN)
        menu_item(29, "View Audit Log", THEME_ADMIN)
        menu_item(30, "Station-wise Results", THEME_ADMIN)

        subheader("System", THEME_ADMIN_ACCENT)
        menu_item(31, "Save Data", THEME_ADMIN)
        menu_item(32, "Logout", THEME_ADMIN)
        print()
        choice = prompt("Enter choice: ")

        if choice == "1": create_candidate()
        elif choice == "2": view_all_candidates()
        elif choice == "3": update_candidate()
        elif choice == "4": delete_candidate()
        elif choice == "5": search_candidates()
        elif choice == "6": create_voting_station()
        elif choice == "7": view_all_stations()
        elif choice == "8": update_station()
        elif choice == "9": delete_station()
        elif choice == "10": create_position()
        elif choice == "11": view_positions()
        elif choice == "12": update_position()
        elif choice == "13": delete_position()
        elif choice == "14": create_poll()
        elif choice == "15": view_all_polls()
        elif choice == "16": update_poll()
        elif choice == "17": delete_poll()
        elif choice == "18": open_close_poll()
        elif choice == "19": assign_candidates_to_poll()
        elif choice == "20": view_all_voters()
        elif choice == "21": verify_voter()
        elif choice == "22": deactivate_voter()
        elif choice == "23": search_voters()
        elif choice == "24": create_admin()
        elif choice == "25": view_admins()
        elif choice == "26": deactivate_admin()
        elif choice == "27": view_poll_results()
        elif choice == "28": view_detailed_statistics()
        elif choice == "29": view_audit_log()
        elif choice == "30": station_wise_results()
        elif choice == "31": save_data(); pause()
        elif choice == "32": log_action("LOGOUT", current_user["username"], "Admin logged out"); save_data(); break
        else: error("Invalid choice."); pause()


## candidate crud
def create_candidate():
    global candidate_id_counter
    clear_screen()
    header("CREATE NEW CANDIDATE", THEME_ADMIN)
    print()
    full_name = prompt("Full Name: ")
    if not full_name: error("Name cannot be empty."); pause(); return
    national_id = prompt("National ID: ")
    if not national_id: error("National ID cannot be empty."); pause(); return
    for cid, c in candidates.items():
        if c["national_id"] == national_id: error("A candidate with this National ID already exists."); pause(); return
    dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
    try:
        dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
        age = (datetime.datetime.now() - dob).days // 365
    except ValueError: error("Invalid date format."); pause(); return
    if age < MIN_CANDIDATE_AGE: error(f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}"); pause(); return
    if age > MAX_CANDIDATE_AGE: error(f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}"); pause(); return
    gender = prompt("Gender (M/F/Other): ").upper()
    subheader("Education Levels", THEME_ADMIN_ACCENT)
    for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
        print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
    try:
        edu_choice = int(prompt("Select education level: "))
        if edu_choice < 1 or edu_choice > len(REQUIRED_EDUCATION_LEVELS): error("Invalid choice."); pause(); return
        education = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
    except ValueError: error("Invalid input."); pause(); return
    party = prompt("Political Party/Affiliation: ")
    manifesto = prompt("Brief Manifesto/Bio: ")
    address = prompt("Address: ")
    phone = prompt("Phone: ")
    email = prompt("Email: ")
    criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()
    if criminal_record == "yes":
        error("Candidates with criminal records are not eligible.")
        log_action("CANDIDATE_REJECTED", current_user["username"], f"Candidate {full_name} rejected - criminal record")
        pause(); return
    years_experience = prompt("Years of Public Service/Political Experience: ")
    try: years_experience = int(years_experience)
    except ValueError: years_experience = 0
    candidates[candidate_id_counter] = {
        "id": candidate_id_counter, "full_name": full_name, "national_id": national_id,
        "date_of_birth": dob_str, "age": age, "gender": gender, "education": education,
        "party": party, "manifesto": manifesto, "address": address, "phone": phone,
        "email": email, "has_criminal_record": False, "years_experience": years_experience,
        "is_active": True, "is_approved": True,
        "created_at": str(datetime.datetime.now()), "created_by": current_user["username"]
    }
    log_action("CREATE_CANDIDATE", current_user["username"], f"Created candidate: {full_name} (ID: {candidate_id_counter})")
    print()
    success(f"Candidate '{full_name}' created successfully! ID: {candidate_id_counter}")
    candidate_id_counter += 1
    save_data(); pause()


def view_all_candidates():
    clear_screen()
    header("ALL CANDIDATES", THEME_ADMIN)
    if not candidates: print(); info("No candidates found."); pause(); return
    print()
    table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
    table_divider(85, THEME_ADMIN)
    for cid, c in candidates.items():
        status = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
        print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20} {status}")
    print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
    pause()


def update_candidate():
    clear_screen()
    header("UPDATE CANDIDATE", THEME_ADMIN)
    if not candidates: print(); info("No candidates found."); pause(); return
    print()
    for cid, c in candidates.items():
        print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
    try: cid = int(prompt("\nEnter Candidate ID to update: "))
    except ValueError: error("Invalid input."); pause(); return
    if cid not in candidates: error("Candidate not found."); pause(); return
    c = candidates[cid]
    print(f"\n  {BOLD}Updating: {c['full_name']}{RESET}")
    info("Press Enter to keep current value\n")
    new_name = prompt(f"Full Name [{c['full_name']}]: ")
    if new_name: c["full_name"] = new_name
    new_party = prompt(f"Party [{c['party']}]: ")
    if new_party: c["party"] = new_party
    new_manifesto = prompt(f"Manifesto [{c['manifesto'][:50]}...]: ")
    if new_manifesto: c["manifesto"] = new_manifesto
    new_phone = prompt(f"Phone [{c['phone']}]: ")
    if new_phone: c["phone"] = new_phone
    new_email = prompt(f"Email [{c['email']}]: ")
    if new_email: c["email"] = new_email
    new_address = prompt(f"Address [{c['address']}]: ")
    if new_address: c["address"] = new_address
    new_exp = prompt(f"Years Experience [{c['years_experience']}]: ")
    if new_exp:
        try: c["years_experience"] = int(new_exp)
        except ValueError: warning("Invalid number, keeping old value.")
    log_action("UPDATE_CANDIDATE", current_user["username"], f"Updated candidate: {c['full_name']} (ID: {cid})")
    print(); success(f"Candidate '{c['full_name']}' updated successfully!")
    save_data(); pause()


def delete_candidate():
    clear_screen()
    header("DELETE CANDIDATE", THEME_ADMIN)
    if not candidates: print(); info("No candidates found."); pause(); return
    print()
    for cid, c in candidates.items():
        status = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET} {status}")
    try: cid = int(prompt("\nEnter Candidate ID to delete: "))
    except ValueError: error("Invalid input."); pause(); return
    if cid not in candidates: error("Candidate not found."); pause(); return
    for pid, poll in polls.items():
        if poll["status"] == "open":
            for pos in poll.get("positions", []):
                if cid in pos.get("candidate_ids", []): error(f"Cannot delete - candidate is in active poll: {poll['title']}"); pause(); return
    confirm = prompt(f"Are you sure you want to delete '{candidates[cid]['full_name']}'? (yes/no): ").lower()
    if confirm == "yes":
        deleted_name = candidates[cid]["full_name"]
        candidates[cid]["is_active"] = False
        log_action("DELETE_CANDIDATE", current_user["username"], f"Deactivated candidate: {deleted_name} (ID: {cid})")
        print(); success(f"Candidate '{deleted_name}' has been deactivated.")
        save_data()
    else: info("Deletion cancelled.")
    pause()


def search_candidates():
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
        term = prompt("Enter name to search: ").lower()
        results = [c for c in candidates.values() if term in c["full_name"].lower()]
    elif choice == "2":
        term = prompt("Enter party name: ").lower()
        results = [c for c in candidates.values() if term in c["party"].lower()]
    elif choice == "3":
        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(prompt("Select: "))
            edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
            results = [c for c in candidates.values() if c["education"] == edu]
        except (ValueError, IndexError): error("Invalid choice."); pause(); return
    elif choice == "4":
        try:
            min_age = int(prompt("Min age: "))
            max_age = int(prompt("Max age: "))
            results = [c for c in candidates.values() if min_age <= c["age"] <= max_age]
        except ValueError: error("Invalid input."); pause(); return
    else: error("Invalid choice."); pause(); return
    if not results: print(); info("No candidates found matching your criteria.")
    else:
        print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
        table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", THEME_ADMIN)
        table_divider(75, THEME_ADMIN)
        for c in results:
            print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20}")
    pause()


### voting station crud 
def create_voting_station():
    global station_id_counter
    clear_screen()
    header("CREATE VOTING STATION", THEME_ADMIN)
    print()
    name = prompt("Station Name: ")
    if not name: error("Name cannot be empty."); pause(); return
    location = prompt("Location/Address: ")
    if not location: error("Location cannot be empty."); pause(); return
    region = prompt("Region/District: ")
    try:
        capacity = int(prompt("Voter Capacity: "))
        if capacity <= 0: error("Capacity must be positive."); pause(); return
    except ValueError: error("Invalid capacity."); pause(); return
    supervisor = prompt("Station Supervisor Name: ")
    contact = prompt("Contact Phone: ")
    opening_time = prompt("Opening Time (e.g. 08:00): ")
    closing_time = prompt("Closing Time (e.g. 17:00): ")
    voting_stations[station_id_counter] = {
        "id": station_id_counter, "name": name, "location": location, "region": region,
        "capacity": capacity, "registered_voters": 0, "supervisor": supervisor,
        "contact": contact, "opening_time": opening_time, "closing_time": closing_time,
        "is_active": True, "created_at": str(datetime.datetime.now()), "created_by": current_user["username"]
    }
    log_action("CREATE_STATION", current_user["username"], f"Created station: {name} (ID: {station_id_counter})")
    print(); success(f"Voting Station '{name}' created! ID: {station_id_counter}")
    station_id_counter += 1
    save_data(); pause()


def view_all_stations():
    clear_screen()
    header("ALL VOTING STATIONS", THEME_ADMIN)
    if not voting_stations: print(); info("No voting stations found."); pause(); return
    print()
    table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN)
    table_divider(96, THEME_ADMIN)
    for sid, s in voting_stations.items():
        reg_count = sum(1 for v in voters.values() if v["station_id"] == sid)
        status = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
        print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15} {s['capacity']:<8} {reg_count:<8} {status}")
    print(f"\n  {DIM}Total Stations: {len(voting_stations)}{RESET}")
    pause()


def update_station():
    clear_screen()
    header("UPDATE VOTING STATION", THEME_ADMIN)
    if not voting_stations: print(); info("No stations found."); pause(); return
    print()
    for sid, s in voting_stations.items():
        print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")
    try: sid = int(prompt("\nEnter Station ID to update: "))
    except ValueError: error("Invalid input."); pause(); return
    if sid not in voting_stations: error("Station not found."); pause(); return
    s = voting_stations[sid]
    print(f"\n  {BOLD}Updating: {s['name']}{RESET}")
    info("Press Enter to keep current value\n")
    new_name = prompt(f"Name [{s['name']}]: ")
    if new_name: s["name"] = new_name
    new_location = prompt(f"Location [{s['location']}]: ")
    if new_location: s["location"] = new_location
    new_region = prompt(f"Region [{s['region']}]: ")
    if new_region: s["region"] = new_region
    new_capacity = prompt(f"Capacity [{s['capacity']}]: ")
    if new_capacity:
        try: s["capacity"] = int(new_capacity)
        except ValueError: warning("Invalid number, keeping old value.")
    new_supervisor = prompt(f"Supervisor [{s['supervisor']}]: ")
    if new_supervisor: s["supervisor"] = new_supervisor
    new_contact = prompt(f"Contact [{s['contact']}]: ")
    if new_contact: s["contact"] = new_contact
    log_action("UPDATE_STATION", current_user["username"], f"Updated station: {s['name']} (ID: {sid})")
    print(); success(f"Station '{s['name']}' updated successfully!")
    save_data(); pause()


def delete_station():
    clear_screen()
    header("DELETE VOTING STATION", THEME_ADMIN)
    if not voting_stations: print(); info("No stations found."); pause(); return
    print()
    for sid, s in voting_stations.items():
        status = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET} {status}")
    try: sid = int(prompt("\nEnter Station ID to delete: "))
    except ValueError: error("Invalid input."); pause(); return
    if sid not in voting_stations: error("Station not found."); pause(); return
    voter_count = sum(1 for v in voters.values() if v["station_id"] == sid)
    if voter_count > 0:
        warning(f"{voter_count} voters are registered at this station.")
        if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes": info("Cancelled."); pause(); return
    if prompt(f"Confirm deactivation of '{voting_stations[sid]['name']}'? (yes/no): ").lower() == "yes":
        voting_stations[sid]["is_active"] = False
        log_action("DELETE_STATION", current_user["username"], f"Deactivated station: {voting_stations[sid]['name']}")
        print(); success(f"Station '{voting_stations[sid]['name']}' deactivated.")
        save_data()
    else: info("Cancelled.")
    pause()


### position crud
def create_position():
    global position_id_counter
    clear_screen()
    header("CREATE POSITION", THEME_ADMIN)
    print()
    title = prompt("Position Title (e.g. President, Governor, Senator): ")
    if not title: error("Title cannot be empty."); pause(); return
    description = prompt("Description: ")
    level = prompt("Level (National/Regional/Local): ")
    if level.lower() not in ["national", "regional", "local"]: error("Invalid level."); pause(); return
    try:
        max_winners = int(prompt("Number of winners/seats: "))
        if max_winners <= 0: error("Must be at least 1."); pause(); return
    except ValueError: error("Invalid number."); pause(); return
    min_cand_age = prompt(f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: ")
    min_cand_age = int(min_cand_age) if min_cand_age.isdigit() else MIN_CANDIDATE_AGE
    positions[position_id_counter] = {
        "id": position_id_counter, "title": title, "description": description,
        "level": level.capitalize(), "max_winners": max_winners, "min_candidate_age": min_cand_age,
        "is_active": True, "created_at": str(datetime.datetime.now()), "created_by": current_user["username"]
    }
    log_action("CREATE_POSITION", current_user["username"], f"Created position: {title} (ID: {position_id_counter})")
    print(); success(f"Position '{title}' created! ID: {position_id_counter}")
    position_id_counter += 1
    save_data(); pause()


def view_positions():
    clear_screen()
    header("ALL POSITIONS", THEME_ADMIN)
    if not positions: print(); info("No positions found."); pause(); return
    print()
    table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}", THEME_ADMIN)
    table_divider(70, THEME_ADMIN)
    for pid, p in positions.items():
        status = status_badge("Active", True) if p["is_active"] else status_badge("Inactive", False)
        print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8} {p['min_candidate_age']:<10} {status}")
    print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
    pause()


def update_position():
    clear_screen()
    header("UPDATE POSITION", THEME_ADMIN)
    if not positions: print(); info("No positions found."); pause(); return
    print()
    for pid, p in positions.items():
        print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
    try: pid = int(prompt("\nEnter Position ID to update: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in positions: error("Position not found."); pause(); return
    p = positions[pid]
    print(f"\n  {BOLD}Updating: {p['title']}{RESET}")
    info("Press Enter to keep current value\n")
    new_title = prompt(f"Title [{p['title']}]: ")
    if new_title: p["title"] = new_title
    new_desc = prompt(f"Description [{p['description'][:50]}]: ")
    if new_desc: p["description"] = new_desc
    new_level = prompt(f"Level [{p['level']}]: ")
    if new_level and new_level.lower() in ["national", "regional", "local"]: p["level"] = new_level.capitalize()
    new_seats = prompt(f"Seats [{p['max_winners']}]: ")
    if new_seats:
        try: p["max_winners"] = int(new_seats)
        except ValueError: warning("Keeping old value.")
    log_action("UPDATE_POSITION", current_user["username"], f"Updated position: {p['title']}")
    print(); success("Position updated!")
    save_data(); pause()


def delete_position():
    clear_screen()
    header("DELETE POSITION", THEME_ADMIN)
    if not positions: print(); info("No positions found."); pause(); return
    print()
    for pid, p in positions.items():
        print(f"  {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}){RESET}")
    try: pid = int(prompt("\nEnter Position ID to delete: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in positions: error("Position not found."); pause(); return
    for poll_id, poll in polls.items():
        for pp in poll.get("positions", []):
            if pp["position_id"] == pid and poll["status"] == "open": error(f"Cannot delete - in active poll: {poll['title']}"); pause(); return
    if prompt(f"Confirm deactivation of '{positions[pid]['title']}'? (yes/no): ").lower() == "yes":
        positions[pid]["is_active"] = False
        log_action("DELETE_POSITION", current_user["username"], f"Deactivated position: {positions[pid]['title']}")
        print(); success("Position deactivated.")
        save_data()
    pause()


### poll crud
def create_poll():
    global poll_id_counter
    clear_screen()
    header("CREATE POLL / ELECTION", THEME_ADMIN)
    print()
    title = prompt("Poll/Election Title: ")
    if not title: error("Title cannot be empty."); pause(); return
    description = prompt("Description: ")
    election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")
    start_date = prompt("Start Date (YYYY-MM-DD): ")
    end_date = prompt("End Date (YYYY-MM-DD): ")
    try:
        sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        if ed <= sd: error("End date must be after start date."); pause(); return
    except ValueError: error("Invalid date format."); pause(); return
    if not positions: error("No positions available. Create positions first."); pause(); return
    subheader("Available Positions", THEME_ADMIN_ACCENT)
    active_positions = {pid: p for pid, p in positions.items() if p["is_active"]}
    if not active_positions: error("No active positions."); pause(); return
    for pid, p in active_positions.items():
        print(f"    {THEME_ADMIN}{p['id']}.{RESET} {p['title']} {DIM}({p['level']}) - {p['max_winners']} seat(s){RESET}")
    try: selected_position_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
    except ValueError: error("Invalid input."); pause(); return
    poll_positions = []
    for spid in selected_position_ids:
        if spid not in active_positions: warning(f"Position ID {spid} not found or inactive. Skipping."); continue
        poll_positions.append({"position_id": spid, "position_title": positions[spid]["title"], "candidate_ids": [], "max_winners": positions[spid]["max_winners"]})
    if not poll_positions: error("No valid positions selected."); pause(); return
    if not voting_stations: error("No voting stations. Create stations first."); pause(); return
    subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
    active_stations = {sid: s for sid, s in voting_stations.items() if s["is_active"]}
    for sid, s in active_stations.items():
        print(f"    {THEME_ADMIN}{s['id']}.{RESET} {s['name']} {DIM}({s['location']}){RESET}")
    if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
        selected_station_ids = list(active_stations.keys())
    else:
        try: selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
        except ValueError: error("Invalid input."); pause(); return
    polls[poll_id_counter] = {
        "id": poll_id_counter, "title": title, "description": description,
        "election_type": election_type, "start_date": start_date, "end_date": end_date,
        "positions": poll_positions, "station_ids": selected_station_ids,
        "status": "draft", "total_votes_cast": 0,
        "created_at": str(datetime.datetime.now()), "created_by": current_user["username"]
    }
    log_action("CREATE_POLL", current_user["username"], f"Created poll: {title} (ID: {poll_id_counter})")
    print(); success(f"Poll '{title}' created! ID: {poll_id_counter}")
    warning("Status: DRAFT - Assign candidates and then open the poll.")
    poll_id_counter += 1
    save_data(); pause()


def view_all_polls():
    clear_screen()
    header("ALL POLLS / ELECTIONS", THEME_ADMIN)
    if not polls: print(); info("No polls found."); pause(); return
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
        print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
        for pos in poll["positions"]:
            cand_names = [candidates[ccid]["full_name"] for ccid in pos["candidate_ids"] if ccid in candidates]
            cand_display = ', '.join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
            print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
    print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
    pause()


def update_poll():
    clear_screen()
    header("UPDATE POLL", THEME_ADMIN)
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID to update: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    if poll["status"] == "open": error("Cannot update an open poll. Close it first."); pause(); return
    if poll["status"] == "closed" and poll["total_votes_cast"] > 0: error("Cannot update a poll with votes."); pause(); return
    print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
    info("Press Enter to keep current value\n")
    new_title = prompt(f"Title [{poll['title']}]: ")
    if new_title: poll["title"] = new_title
    new_desc = prompt(f"Description [{poll['description'][:50]}]: ")
    if new_desc: poll["description"] = new_desc
    new_type = prompt(f"Election Type [{poll['election_type']}]: ")
    if new_type: poll["election_type"] = new_type
    new_start = prompt(f"Start Date [{poll['start_date']}]: ")
    if new_start:
        try: datetime.datetime.strptime(new_start, "%Y-%m-%d"); poll["start_date"] = new_start
        except ValueError: warning("Invalid date, keeping old value.")
    new_end = prompt(f"End Date [{poll['end_date']}]: ")
    if new_end:
        try: datetime.datetime.strptime(new_end, "%Y-%m-%d"); poll["end_date"] = new_end
        except ValueError: warning("Invalid date, keeping old value.")
    log_action("UPDATE_POLL", current_user["username"], f"Updated poll: {poll['title']}")
    print(); success("Poll updated!")
    save_data(); pause()


def delete_poll():
    clear_screen()
    header("DELETE POLL", THEME_ADMIN)
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID to delete: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    if polls[pid]["status"] == "open": error("Cannot delete an open poll. Close it first."); pause(); return
    if polls[pid]["total_votes_cast"] > 0: warning(f"This poll has {polls[pid]['total_votes_cast']} votes recorded.")
    if prompt(f"Confirm deletion of '{polls[pid]['title']}'? (yes/no): ").lower() == "yes":
        deleted_title = polls[pid]["title"]
        del polls[pid]
        global votes
        votes = [v for v in votes if v["poll_id"] != pid]
        log_action("DELETE_POLL", current_user["username"], f"Deleted poll: {deleted_title}")
        print(); success(f"Poll '{deleted_title}' deleted.")
        save_data()
    pause()


def open_close_poll():
    clear_screen()
    header("OPEN / CLOSE POLL", THEME_ADMIN)
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    if poll["status"] == "draft":
        if not any(pos["candidate_ids"] for pos in poll["positions"]): error("Cannot open - no candidates assigned."); pause(); return
        if prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
            poll["status"] = "open"
            log_action("OPEN_POLL", current_user["username"], f"Opened poll: {poll['title']}")
            print(); success(f"Poll '{poll['title']}' is now OPEN for voting!")
            save_data()
    elif poll["status"] == "open":
        if prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
            poll["status"] = "closed"
            log_action("CLOSE_POLL", current_user["username"], f"Closed poll: {poll['title']}")
            print(); success(f"Poll '{poll['title']}' is now CLOSED.")
            save_data()
    elif poll["status"] == "closed":
        info("This poll is already closed.")
        if prompt("Reopen it? (yes/no): ").lower() == "yes":
            poll["status"] = "open"
            log_action("REOPEN_POLL", current_user["username"], f"Reopened poll: {poll['title']}")
            print(); success("Poll reopened!")
            save_data()
    pause()


def assign_candidates_to_poll():
    clear_screen()
    header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
    if not polls: print(); info("No polls found."); pause(); return
    if not candidates: print(); info("No candidates found."); pause(); return
    print()
    for pid, poll in polls.items():
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    if poll["status"] == "open": error("Cannot modify candidates of an open poll."); pause(); return
    for i, pos in enumerate(poll["positions"]):
        subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
        current_cands = [f"{ccid}: {candidates[ccid]['full_name']}" for ccid in pos["candidate_ids"] if ccid in candidates]
        if current_cands: print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
        else: info("No candidates assigned yet.")
        active_candidates = {cid: c for cid, c in candidates.items() if c["is_active"] and c["is_approved"]}
        pos_data = positions.get(pos["position_id"], {})
        min_age = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
        eligible = {cid: c for cid, c in active_candidates.items() if c["age"] >= min_age}
        if not eligible: info("No eligible candidates found."); continue
        subheader("Available Candidates", THEME_ADMIN)
        for cid, c in eligible.items():
            marker = f" {GREEN}[ASSIGNED]{RESET}" if cid in pos["candidate_ids"] else ""
            print(f"    {THEME_ADMIN}{c['id']}.{RESET} {c['full_name']} {DIM}({c['party']}) - Age: {c['age']}, Edu: {c['education']}{RESET}{marker}")
        if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
            try:
                new_cand_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                valid_ids = []
                for ncid in new_cand_ids:
                    if ncid in eligible: valid_ids.append(ncid)
                    else: warning(f"Candidate {ncid} not eligible. Skipping.")
                pos["candidate_ids"] = valid_ids
                success(f"{len(valid_ids)} candidate(s) assigned.")
            except ValueError: error("Invalid input. Skipping this position.")
    log_action("ASSIGN_CANDIDATES", current_user["username"], f"Updated candidates for poll: {poll['title']}")
    save_data(); pause()


### voter management
def view_all_voters():
    clear_screen()
    header("ALL REGISTERED VOTERS", THEME_ADMIN)
    if not voters: print(); info("No voters registered."); pause(); return
    print()
    table_header(f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}", THEME_ADMIN)
    table_divider(70, THEME_ADMIN)
    for vid, v in voters.items():
        verified = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
        active = status_badge("Yes", True) if v["is_active"] else status_badge("No", False)
        print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {v['station_id']:<6} {verified:<19} {active}")
    verified_count = sum(1 for v in voters.values() if v["is_verified"])
    unverified_count = sum(1 for v in voters.values() if not v["is_verified"])
    print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
    pause()


def verify_voter():
    clear_screen()
    header("VERIFY VOTER", THEME_ADMIN)
    unverified = {vid: v for vid, v in voters.items() if not v["is_verified"]}
    if not unverified: print(); info("No unverified voters."); pause(); return
    subheader("Unverified Voters", THEME_ADMIN_ACCENT)
    for vid, v in unverified.items():
        print(f"  {THEME_ADMIN}{v['id']}.{RESET} {v['full_name']} {DIM}│ NID: {v['national_id']} │ Card: {v['voter_card_number']}{RESET}")
    print()
    menu_item(1, "Verify a single voter", THEME_ADMIN)
    menu_item(2, "Verify all pending voters", THEME_ADMIN)
    choice = prompt("\nChoice: ")
    if choice == "1":
        try: vid = int(prompt("Enter Voter ID: "))
        except ValueError: error("Invalid input."); pause(); return
        if vid not in voters: error("Voter not found."); pause(); return
        if voters[vid]["is_verified"]: info("Already verified."); pause(); return
        voters[vid]["is_verified"] = True
        log_action("VERIFY_VOTER", current_user["username"], f"Verified voter: {voters[vid]['full_name']}")
        print(); success(f"Voter '{voters[vid]['full_name']}' verified!")
        save_data()
    elif choice == "2":
        count = 0
        for vid in unverified: voters[vid]["is_verified"] = True; count += 1
        log_action("VERIFY_ALL_VOTERS", current_user["username"], f"Verified {count} voters")
        print(); success(f"{count} voters verified!")
        save_data()
    pause()


def deactivate_voter():
    clear_screen()
    header("DEACTIVATE VOTER", THEME_ADMIN)
    if not voters: print(); info("No voters found."); pause(); return
    print()
    try: vid = int(prompt("Enter Voter ID to deactivate: "))
    except ValueError: error("Invalid input."); pause(); return
    if vid not in voters: error("Voter not found."); pause(); return
    if not voters[vid]["is_active"]: info("Already deactivated."); pause(); return
    if prompt(f"Deactivate '{voters[vid]['full_name']}'? (yes/no): ").lower() == "yes":
        voters[vid]["is_active"] = False
        log_action("DEACTIVATE_VOTER", current_user["username"], f"Deactivated voter: {voters[vid]['full_name']}")
        print(); success("Voter deactivated.")
        save_data()
    pause()


def search_voters():
    clear_screen()
    header("SEARCH VOTERS", THEME_ADMIN)
    subheader("Search by", THEME_ADMIN_ACCENT)
    menu_item(1, "Name", THEME_ADMIN); menu_item(2, "Voter Card Number", THEME_ADMIN)
    menu_item(3, "National ID", THEME_ADMIN); menu_item(4, "Station", THEME_ADMIN)
    choice = prompt("\nChoice: ")
    results = []
    if choice == "1": term = prompt("Name: ").lower(); results = [v for v in voters.values() if term in v["full_name"].lower()]
    elif choice == "2": term = prompt("Card Number: "); results = [v for v in voters.values() if term == v["voter_card_number"]]
    elif choice == "3": term = prompt("National ID: "); results = [v for v in voters.values() if term == v["national_id"]]
    elif choice == "4":
        try: sid = int(prompt("Station ID: ")); results = [v for v in voters.values() if v["station_id"] == sid]
        except ValueError: error("Invalid input."); pause(); return
    else: error("Invalid choice."); pause(); return
    if not results: print(); info("No voters found.")
    else:
        print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
        for v in results:
            verified = status_badge("Verified", True) if v['is_verified'] else status_badge("Unverified", False)
            print(f"  {THEME_ADMIN}ID:{RESET} {v['id']}  {DIM}│{RESET}  {v['full_name']}  {DIM}│  Card:{RESET} {v['voter_card_number']}  {DIM}│{RESET}  {verified}")
    pause()


### admin management
def create_admin():
    global admin_id_counter
    clear_screen()
    header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
    if current_user["role"] != "super_admin": print(); error("Only super admins can create admin accounts."); pause(); return
    print()
    username = prompt("Username: ")
    if not username: error("Username cannot be empty."); pause(); return
    for aid, a in admins.items():
        if a["username"] == username: error("Username already exists."); pause(); return
    full_name = prompt("Full Name: ")
    email = prompt("Email: ")
    password = masked_input("Password: ").strip()
    if len(password) < 6: error("Password must be at least 6 characters."); pause(); return
    subheader("Available Roles", THEME_ADMIN_ACCENT)
    menu_item(1, f"super_admin {DIM}─ Full access{RESET}", THEME_ADMIN)
    menu_item(2, f"election_officer {DIM}─ Manage polls and candidates{RESET}", THEME_ADMIN)
    menu_item(3, f"station_manager {DIM}─ Manage stations and verify voters{RESET}", THEME_ADMIN)
    menu_item(4, f"auditor {DIM}─ Read-only access{RESET}", THEME_ADMIN)
    role_choice = prompt("\nSelect role (1-4): ")
    role_map = {"1": "super_admin", "2": "election_officer", "3": "station_manager", "4": "auditor"}
    if role_choice not in role_map: error("Invalid role."); pause(); return
    role = role_map[role_choice]
    admins[admin_id_counter] = {
        "id": admin_id_counter, "username": username, "password": hash_password(password),
        "full_name": full_name, "email": email, "role": role,
        "created_at": str(datetime.datetime.now()), "is_active": True
    }
    log_action("CREATE_ADMIN", current_user["username"], f"Created admin: {username} (Role: {role})")
    print(); success(f"Admin '{username}' created with role: {role}")
    admin_id_counter += 1
    save_data(); pause()


def view_admins():
    clear_screen()
    header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
    print()
    table_header(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}", THEME_ADMIN)
    table_divider(78, THEME_ADMIN)
    for aid, a in admins.items():
        active = status_badge("Yes", True) if a["is_active"] else status_badge("No", False)
        print(f"  {a['id']:<5} {a['username']:<20} {a['full_name']:<25} {a['role']:<20} {active}")
    print(f"\n  {DIM}Total Admins: {len(admins)}{RESET}")
    pause()


def deactivate_admin():
    clear_screen()
    header("DEACTIVATE ADMIN", THEME_ADMIN)
    if current_user["role"] != "super_admin": print(); error("Only super admins can deactivate admins."); pause(); return
    print()
    for aid, a in admins.items():
        active = status_badge("Active", True) if a["is_active"] else status_badge("Inactive", False)
        print(f"  {THEME_ADMIN}{a['id']}.{RESET} {a['username']} {DIM}({a['role']}){RESET} {active}")
    try: aid = int(prompt("\nEnter Admin ID to deactivate: "))
    except ValueError: error("Invalid input."); pause(); return
    if aid not in admins: error("Admin not found."); pause(); return
    if aid == current_user["id"]: error("Cannot deactivate your own account."); pause(); return
    if prompt(f"Deactivate '{admins[aid]['username']}'? (yes/no): ").lower() == "yes":
        admins[aid]["is_active"] = False
        log_action("DEACTIVATE_ADMIN", current_user["username"], f"Deactivated admin: {admins[aid]['username']}")
        print(); success("Admin deactivated.")
        save_data()
    pause()


### voting process
def voter_dashboard():
    while True:
        clear_screen()
        header("VOTER DASHBOARD", THEME_VOTER)
        station_name = voting_stations.get(current_user["station_id"], {}).get("name", "Unknown")
        print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}")
        print(f"  {DIM}    Card: {current_user['voter_card_number']}  │  Station: {station_name}{RESET}")
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
        if choice == "1": view_open_polls_voter()
        elif choice == "2": cast_vote()
        elif choice == "3": view_voting_history()
        elif choice == "4": view_closed_poll_results_voter()
        elif choice == "5": view_voter_profile()
        elif choice == "6": change_voter_password()
        elif choice == "7": log_action("LOGOUT", current_user["voter_card_number"], "Voter logged out"); save_data(); break
        else: error("Invalid choice."); pause()


def view_open_polls_voter():
    clear_screen()
    header("OPEN POLLS", THEME_VOTER)
    open_polls = {pid: p for pid, p in polls.items() if p["status"] == "open"}
    if not open_polls: print(); info("No open polls at this time."); pause(); return
    for pid, poll in open_polls.items():
        already_voted = pid in current_user.get("has_voted_in", [])
        vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
        print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{vs}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
        for pos in poll["positions"]:
            print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
            for ccid in pos["candidate_ids"]:
                if ccid in candidates:
                    c = candidates[ccid]
                    print(f"      {DIM}•{RESET} {c['full_name']} {DIM}({c['party']}) │ Age: {c['age']} │ Edu: {c['education']}{RESET}")
    pause()


def cast_vote():
    clear_screen()
    header("CAST YOUR VOTE", THEME_VOTER)
    open_polls = {pid: p for pid, p in polls.items() if p["status"] == "open"}
    if not open_polls: print(); info("No open polls at this time."); pause(); return
    available_polls = {}
    for pid, poll in open_polls.items():
        if pid not in current_user.get("has_voted_in", []) and current_user["station_id"] in poll["station_ids"]:
            available_polls[pid] = poll
    if not available_polls: print(); info("No available polls to vote in."); pause(); return
    subheader("Available Polls", THEME_VOTER_ACCENT)
    for pid, poll in available_polls.items():
        print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")
    try: pid = int(prompt("\nSelect Poll ID to vote: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in available_polls: error("Invalid poll selection."); pause(); return
    poll = polls[pid]
    print()
    header(f"Voting: {poll['title']}", THEME_VOTER)
    info("Please select ONE candidate for each position.\n")
    my_votes = []
    for pos in poll["positions"]:
        subheader(pos['position_title'], THEME_VOTER_ACCENT)
        if not pos["candidate_ids"]: info("No candidates for this position."); continue
        for idx, ccid in enumerate(pos["candidate_ids"], 1):
            if ccid in candidates:
                c = candidates[ccid]
                print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
                print(f"       {DIM}Age: {c['age']} │ Edu: {c['education']} │ Exp: {c['years_experience']} yrs{RESET}")
                if c["manifesto"]: print(f"       {ITALIC}{DIM}{c['manifesto'][:80]}...{RESET}")
        print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")
        try: vote_choice = int(prompt(f"\nYour choice for {pos['position_title']}: "))
        except ValueError: warning("Invalid input. Skipping."); vote_choice = 0
        if vote_choice == 0:
            my_votes.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": None, "abstained": True})
        elif 1 <= vote_choice <= len(pos["candidate_ids"]):
            selected_cid = pos["candidate_ids"][vote_choice - 1]
            my_votes.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": selected_cid, "candidate_name": candidates[selected_cid]["full_name"], "abstained": False})
        else:
            warning("Invalid choice. Marking as abstain.")
            my_votes.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": None, "abstained": True})
    subheader("VOTE SUMMARY", BRIGHT_WHITE)
    for mv in my_votes:
        if mv["abstained"]: print(f"  {mv['position_title']}: {GRAY}ABSTAINED{RESET}")
        else: print(f"  {mv['position_title']}: {BRIGHT_GREEN}{BOLD}{mv['candidate_name']}{RESET}")
    print()
    if prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes": info("Vote cancelled."); pause(); return
    vote_timestamp = str(datetime.datetime.now())
    vote_hash = hashlib.sha256(f"{current_user['id']}{pid}{vote_timestamp}".encode()).hexdigest()[:16]
    for mv in my_votes:
        votes.append({"vote_id": vote_hash + str(mv["position_id"]), "poll_id": pid, "position_id": mv["position_id"], "candidate_id": mv["candidate_id"], "voter_id": current_user["id"], "station_id": current_user["station_id"], "timestamp": vote_timestamp, "abstained": mv["abstained"]})
    current_user["has_voted_in"].append(pid)
    for vid, v in voters.items():
        if v["id"] == current_user["id"]: v["has_voted_in"].append(pid); break
    polls[pid]["total_votes_cast"] += 1
    log_action("CAST_VOTE", current_user["voter_card_number"], f"Voted in poll: {poll['title']} (Hash: {vote_hash})")
    print()
    success("Your vote has been recorded successfully!")
    print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{vote_hash}{RESET}")
    print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
    save_data(); pause()


def view_voting_history():
    clear_screen()
    header("MY VOTING HISTORY", THEME_VOTER)
    voted_polls = current_user.get("has_voted_in", [])
    if not voted_polls: print(); info("You have not voted in any polls yet."); pause(); return
    print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
    for pid in voted_polls:
        if pid in polls:
            poll = polls[pid]
            sc = GREEN if poll['status'] == 'open' else RED
            print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
            for vr in [v for v in votes if v["poll_id"] == pid and v["voter_id"] == current_user["id"]]:
                pos_title = next((pos["position_title"] for pos in poll.get("positions", []) if pos["position_id"] == vr["position_id"]), "Unknown")
                if vr["abstained"]: print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                else: print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{candidates.get(vr['candidate_id'], {}).get('full_name', 'Unknown')}{RESET}")
            print()
    pause()


def view_closed_poll_results_voter():
    clear_screen()
    header("ELECTION RESULTS", THEME_VOTER)
    closed_polls = {pid: p for pid, p in polls.items() if p["status"] == "closed"}
    if not closed_polls: print(); info("No closed polls with results."); pause(); return
    for pid, poll in closed_polls.items():
        print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
        for pos in poll["positions"]:
            subheader(pos['position_title'], THEME_VOTER_ACCENT)
            vote_counts = {}
            abstain_count = 0
            for v in votes:
                if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                    if v["abstained"]: abstain_count += 1
                    else: vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
            total = sum(vote_counts.values()) + abstain_count
            for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                cand = candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                bar = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank <= pos["max_winners"] else ""
                print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
            if abstain_count > 0:
                print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total * 100) if total > 0 else 0:.1f}%){RESET}")
    pause()


def view_voter_profile():
    clear_screen()
    header("MY PROFILE", THEME_VOTER)
    v = current_user
    station_name = voting_stations.get(v["station_id"], {}).get("name", "Unknown")
    print()
    for label, value in [
        ("Name", v['full_name']), ("National ID", v['national_id']),
        ("Voter Card", f"{BRIGHT_YELLOW}{v['voter_card_number']}{RESET}"),
        ("Date of Birth", v['date_of_birth']), ("Age", v['age']), ("Gender", v['gender']),
        ("Address", v['address']), ("Phone", v['phone']), ("Email", v['email']),
        ("Station", station_name),
        ("Verified", status_badge('Yes', True) if v['is_verified'] else status_badge('No', False)),
        ("Registered", v['registered_at']), ("Polls Voted", len(v.get('has_voted_in', [])))
    ]:
        print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
    pause()


def change_voter_password():
    clear_screen()
    header("CHANGE PASSWORD", THEME_VOTER)
    print()
    old_pass = masked_input("Current Password: ").strip()
    if hash_password(old_pass) != current_user["password"]: error("Incorrect current password."); pause(); return
    new_pass = masked_input("New Password: ").strip()
    if len(new_pass) < 6: error("Password must be at least 6 characters."); pause(); return
    confirm_pass = masked_input("Confirm New Password: ").strip()
    if new_pass != confirm_pass: error("Passwords do not match."); pause(); return
    current_user["password"] = hash_password(new_pass)
    for vid, v in voters.items():
        if v["id"] == current_user["id"]: v["password"] = hash_password(new_pass); break
    log_action("CHANGE_PASSWORD", current_user["voter_card_number"], "Password changed")
    print(); success("Password changed successfully!")
    save_data(); pause()


### results and stats
def view_poll_results():
    clear_screen()
    header("POLL RESULTS", THEME_ADMIN)
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    print()
    header(f"RESULTS: {poll['title']}", THEME_ADMIN)
    sc = GREEN if poll['status'] == 'open' else RED
    print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll['total_votes_cast']}{RESET}")
    total_eligible = sum(1 for v in voters.values() if v["is_verified"] and v["is_active"] and v["station_id"] in poll["station_ids"])
    turnout = (poll['total_votes_cast'] / total_eligible * 100) if total_eligible > 0 else 0
    tc = GREEN if turnout > 50 else (YELLOW if turnout > 25 else RED)
    print(f"  {DIM}Eligible:{RESET} {total_eligible}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout:.1f}%{RESET}")
    for pos in poll["positions"]:
        subheader(f"{pos['position_title']} (Seats: {pos['max_winners']})", THEME_ADMIN_ACCENT)
        vote_counts = {}
        abstain_count = 0
        total_pos = 0
        for v in votes:
            if v["poll_id"] == pid and v["position_id"] == pos["position_id"]:
                total_pos += 1
                if v["abstained"]: abstain_count += 1
                else: vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
        for rank, (cid, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
            cand = candidates.get(cid, {})
            pct = (count / total_pos * 100) if total_pos > 0 else 0
            bl = int(pct / 2)
            bar = f"{THEME_ADMIN}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
            winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= pos["max_winners"] else ""
            print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
            print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
        if abstain_count > 0: print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total_pos * 100) if total_pos > 0 else 0:.1f}%){RESET}")
        if not vote_counts: info("    No votes recorded for this position.")
    pause()


def view_detailed_statistics():
    clear_screen()
    header("DETAILED STATISTICS", THEME_ADMIN)
    subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
    tc = len(candidates); ac = sum(1 for c in candidates.values() if c["is_active"])
    tv = len(voters); vv = sum(1 for v in voters.values() if v["is_verified"])
    av = sum(1 for v in voters.values() if v["is_active"])
    ts = len(voting_stations); ast = sum(1 for s in voting_stations.values() if s["is_active"])
    tp = len(polls)
    op = sum(1 for p in polls.values() if p["status"] == "open")
    cp = sum(1 for p in polls.values() if p["status"] == "closed")
    dp = sum(1 for p in polls.values() if p["status"] == "draft")
    print(f"  {THEME_ADMIN}Candidates:{RESET}  {tc} {DIM}(Active: {ac}){RESET}")
    print(f"  {THEME_ADMIN}Voters:{RESET}      {tv} {DIM}(Verified: {vv}, Active: {av}){RESET}")
    print(f"  {THEME_ADMIN}Stations:{RESET}    {ts} {DIM}(Active: {ast}){RESET}")
    print(f"  {THEME_ADMIN}Polls:{RESET}       {tp} {DIM}({GREEN}Open: {op}{RESET}{DIM}, {RED}Closed: {cp}{RESET}{DIM}, {YELLOW}Draft: {dp}{RESET}{DIM}){RESET}")
    print(f"  {THEME_ADMIN}Total Votes:{RESET} {len(votes)}")
    subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
    gender_counts = {}
    age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
    for v in voters.values():
        gender_counts[v.get("gender", "?")] = gender_counts.get(v.get("gender", "?"), 0) + 1
        age = v.get("age", 0)
        if age <= 25: age_groups["18-25"] += 1
        elif age <= 35: age_groups["26-35"] += 1
        elif age <= 45: age_groups["36-45"] += 1
        elif age <= 55: age_groups["46-55"] += 1
        elif age <= 65: age_groups["56-65"] += 1
        else: age_groups["65+"] += 1
    for g, count in gender_counts.items():
        pct = (count / tv * 100) if tv > 0 else 0
        print(f"    {g}: {count} ({pct:.1f}%)")
    print(f"  {BOLD}Age Distribution:{RESET}")
    for group, count in age_groups.items():
        pct = (count / tv * 100) if tv > 0 else 0
        print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")
    subheader("STATION LOAD", THEME_ADMIN_ACCENT)
    for sid, s in voting_stations.items():
        vc = sum(1 for v in voters.values() if v["station_id"] == sid)
        lp = (vc / s["capacity"] * 100) if s["capacity"] > 0 else 0
        lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
        st = f"{RED}{BOLD}OVERLOADED{RESET}" if lp > 100 else f"{GREEN}OK{RESET}"
        print(f"    {s['name']}: {vc}/{s['capacity']} {lc}({lp:.0f}%){RESET} {st}")
    subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
    party_counts = {}
    for c in candidates.values():
        if c["is_active"]: party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
    for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")
    subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
    edu_counts = {}
    for c in candidates.values():
        if c["is_active"]: edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1
    for edu, count in edu_counts.items():
        print(f"    {edu}: {BOLD}{count}{RESET}")
    pause()


def station_wise_results():
    clear_screen()
    header("STATION-WISE RESULTS", THEME_ADMIN)
    if not polls: print(); info("No polls found."); pause(); return
    print()
    for pid, poll in polls.items():
        sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
        print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
    try: pid = int(prompt("\nEnter Poll ID: "))
    except ValueError: error("Invalid input."); pause(); return
    if pid not in polls: error("Poll not found."); pause(); return
    poll = polls[pid]
    print()
    header(f"STATION RESULTS: {poll['title']}", THEME_ADMIN)
    for sid in poll["station_ids"]:
        if sid not in voting_stations: continue
        station = voting_stations[sid]
        subheader(f"{station['name']}  ({station['location']})", BRIGHT_WHITE)
        station_votes = [v for v in votes if v["poll_id"] == pid and v["station_id"] == sid]
        svc = len(set(v["voter_id"] for v in station_votes))
        ras = sum(1 for v in voters.values() if v["station_id"] == sid and v["is_verified"] and v["is_active"])
        st = (svc / ras * 100) if ras > 0 else 0
        tc = GREEN if st > 50 else (YELLOW if st > 25 else RED)
        print(f"  {DIM}Registered:{RESET} {ras}  {DIM}│  Voted:{RESET} {svc}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{st:.1f}%{RESET}")
        for pos in poll["positions"]:
            print(f"    {THEME_ADMIN_ACCENT}▸ {pos['position_title']}:{RESET}")
            pv = [v for v in station_votes if v["position_id"] == pos["position_id"]]
            vc = {}; ac = 0
            for v in pv:
                if v["abstained"]: ac += 1
                else: vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
            total = sum(vc.values()) + ac
            for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                cand = candidates.get(cid, {})
                pct = (count / total * 100) if total > 0 else 0
                print(f"      {cand.get('full_name', '?')} {DIM}({cand.get('party', '?')}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
            if ac > 0: print(f"      {GRAY}Abstained: {ac} ({(ac / total * 100) if total > 0 else 0:.1f}%){RESET}")
    pause()


def view_audit_log():
    clear_screen()
    header("AUDIT LOG", THEME_ADMIN)
    if not audit_log: print(); info("No audit records."); pause(); return
    print(f"\n  {DIM}Total Records: {len(audit_log)}{RESET}")
    subheader("Filter", THEME_ADMIN_ACCENT)
    menu_item(1, "Last 20 entries", THEME_ADMIN); menu_item(2, "All entries", THEME_ADMIN)
    menu_item(3, "Filter by action type", THEME_ADMIN); menu_item(4, "Filter by user", THEME_ADMIN)
    choice = prompt("\nChoice: ")
    entries = audit_log
    if choice == "1": entries = audit_log[-20:]
    elif choice == "3":
        action_types = list(set(e["action"] for e in audit_log))
        for i, at in enumerate(action_types, 1): print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
        try: at_choice = int(prompt("Select action type: ")); entries = [e for e in audit_log if e["action"] == action_types[at_choice - 1]]
        except (ValueError, IndexError): error("Invalid choice."); pause(); return
    elif choice == "4":
        uf = prompt("Enter username/card number: ")
        entries = [e for e in audit_log if uf.lower() in e["user"].lower()]
    print()
    table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
    table_divider(100, THEME_ADMIN)
    for entry in entries:
        ac = GREEN if "CREATE" in entry["action"] or entry["action"] == "LOGIN" else (RED if "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"] else (YELLOW if "UPDATE" in entry["action"] else RESET))
        print(f"  {DIM}{entry['timestamp'][:19]}{RESET}  {ac}{entry['action']:<25}{RESET} {entry['user']:<20} {DIM}{entry['details'][:50]}{RESET}")
    pause()


### main app
def main():
    global current_user, current_role
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")
    load_data()
    time.sleep(1)
    while True:
        clear_screen()
        logged_in = login()
        if logged_in:
            if current_role == "admin": admin_dashboard()
            elif current_role == "voter": voter_dashboard()
            current_user = None
            current_role = None


if __name__ == "__main__":
    main()