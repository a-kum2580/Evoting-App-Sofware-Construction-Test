"""
AdminMgmtScreens — Admin screens for admin account management.

Handles: create admin, view all admins, deactivate admin.
Only super_admin users can create or deactivate admin accounts.
Delegates all business logic to AdminService.
"""

from e_voting.constants import ADMIN_ROLES, MIN_PASSWORD_LENGTH
from e_voting.ui.console import (
    clear_screen, header, subheader, table_header, table_divider,
    menu_item, prompt, masked_input,
    error, success, info, status_badge, pause,
    THEME_ADMIN, THEME_ADMIN_ACCENT, DIM, RESET, BOLD,
)


class AdminMgmtScreens:
    """Admin UI screens for admin account management."""

    def __init__(self, store, admin_service, auth_service):
        self._store = store
        self._admins = admin_service
        self._auth = auth_service

    def create(self):
        clear_screen()
        header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
        if not self._store.current_user.is_super_admin():
            print()
            error("Only super admins can create admin accounts.")
            pause(); return
        print()
        username = prompt("Username: ")
        if not username:
            error("Username cannot be empty."); pause(); return
        if not self._admins.is_username_unique(username):
            error("Username already exists."); pause(); return
        full_name = prompt("Full Name: ")
        email = prompt("Email: ")
        password = masked_input("Password: ").strip()
        if len(password) < MIN_PASSWORD_LENGTH:
            error(f"Password must be at least "
                  f"{MIN_PASSWORD_LENGTH} characters.")
            pause(); return

        subheader("Available Roles", THEME_ADMIN_ACCENT)
        menu_item(1, f"super_admin {DIM}─ Full access{RESET}",
                  THEME_ADMIN)
        menu_item(2, f"election_officer {DIM}─ Manage polls and "
                     f"candidates{RESET}", THEME_ADMIN)
        menu_item(3, f"station_manager {DIM}─ Manage stations and "
                     f"verify voters{RESET}", THEME_ADMIN)
        menu_item(4, f"auditor {DIM}─ Read-only access{RESET}",
                  THEME_ADMIN)
        role_choice = prompt("\nSelect role (1-4): ")
        if role_choice not in ADMIN_ROLES:
            error("Invalid role."); pause(); return
        role = ADMIN_ROLES[role_choice]

        admin = self._admins.create(
            username, full_name, email,
            self._auth.hash_password(password), role,
            self._store.current_user.username
        )
        print()
        success(f"Admin '{username}' created with role: {role}")
        pause()

    def view_all(self):
        clear_screen()
        header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
        print()
        admins = self._admins.get_all()
        col_id, col_user, col_name, col_role, col_act = 5, 20, 25, 20, 8
        table_width = col_id + col_user + col_name + col_role + col_act
        table_header(
            f"{'ID':<{col_id}} {'Username':<{col_user}} {'Full Name':<{col_name}} "
            f"{'Role':<{col_role}} {'Active':<{col_act}}", THEME_ADMIN
        )
        table_divider(table_width, THEME_ADMIN)
        for admin in admins.values():
            active = (status_badge("Yes", True) if admin.is_active
                      else status_badge("No", False))
            print(f"  {admin.id:<{col_id}} {admin.username:<{col_user}} "
                  f"{admin.full_name:<{col_name}} {admin.role:<{col_role}} {active}")
        print(f"\n  {DIM}Total Admins: {len(admins)}{RESET}")
        pause()

    def deactivate(self):
        clear_screen()
        header("DEACTIVATE ADMIN", THEME_ADMIN)
        if not self._store.current_user.is_super_admin():
            print()
            error("Only super admins can deactivate admins.")
            pause(); return
        print()
        admins = self._admins.get_all()
        for admin in admins.values():
            active = (status_badge("Active", True) if admin.is_active
                      else status_badge("Inactive", False))
            print(f"  {THEME_ADMIN}{admin.id}.{RESET} {admin.username} "
                  f"{DIM}({admin.role}){RESET} {active}")
        try:
            aid = int(prompt("\nEnter Admin ID to deactivate: "))
        except ValueError:
            error("Invalid input."); pause(); return
        if aid not in admins:
            error("Admin not found."); pause(); return
        if aid == self._store.current_user.id:
            error("Cannot deactivate your own account.")
            pause(); return

        admin = admins[aid]
        if prompt(f"Deactivate '{admin.username}'? "
                  "(yes/no): ").lower() == "yes":
            self._admins.deactivate(
                aid, self._store.current_user.username
            )
            print()
            success("Admin deactivated.")
        pause()
