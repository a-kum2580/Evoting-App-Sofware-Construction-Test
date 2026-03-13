"""
StationScreens — Admin screens for voting station management.

Handles: create, view all, update, and delete voting stations.
Delegates all business logic to StationService.
"""

from e_voting.ui.console import (
    clear_screen, header, table_header, table_divider,
    prompt, error, success, warning, info, status_badge, pause,
    THEME_ADMIN, DIM, RESET, BOLD,
)


class StationScreens:
    """Admin UI screens for voting station CRUD."""

    def __init__(self, store, station_service):
        self._store = store
        self._stations = station_service

    def create(self):
        clear_screen()
        header("CREATE VOTING STATION", THEME_ADMIN)
        print()
        name = prompt("Station Name: ")
        if not name:
            error("Name cannot be empty."); pause(); return
        location = prompt("Location/Address: ")
        if not location:
            error("Location cannot be empty."); pause(); return
        region = prompt("Region/District: ")
        try:
            capacity = int(prompt("Voter Capacity: "))
            min_capacity = 1
            if capacity < min_capacity:
                error("Capacity must be positive."); pause(); return
        except ValueError:
            error("Invalid capacity."); pause(); return
        supervisor = prompt("Station Supervisor Name: ")
        contact = prompt("Contact Phone: ")
        opening_time = prompt("Opening Time (e.g. 08:00): ")
        closing_time = prompt("Closing Time (e.g. 17:00): ")

        station = self._stations.create(
            name, location, region, capacity, supervisor, contact,
            opening_time, closing_time,
            self._store.current_user.username
        )
        print()
        success(f"Voting Station '{name}' created! ID: {station.id}")
        pause()

    def view_all(self):
        clear_screen()
        header("ALL VOTING STATIONS", THEME_ADMIN)
        stations = self._stations.get_all()
        if not stations:
            print(); info("No voting stations found."); pause(); return
        print()
        col_id, col_name, col_loc, col_reg, col_cap, col_cnt, col_status = 5, 25, 25, 15, 8, 8, 10
        table_width = col_id + col_name + col_loc + col_reg + col_cap + col_cnt + col_status
        table_header(
            f"{'ID':<{col_id}} {'Name':<{col_name}} {'Location':<{col_loc}} {'Region':<{col_reg}} "
            f"{'Cap.':<{col_cap}} {'Reg.':<{col_cnt}} {'Status':<{col_status}}", THEME_ADMIN
        )
        table_divider(table_width, THEME_ADMIN)
        for sid, station in stations.items():
            reg_count = self._stations.get_registered_voter_count(sid)
            status = (status_badge("Active", True) if station.is_active
                      else status_badge("Inactive", False))
            print(f"  {station.id:<{col_id}} {station.name:<{col_name}} "
                  f"{station.location:<{col_loc}} {station.region:<{col_reg}} "
                  f"{station.capacity:<{col_cap}} {reg_count:<{col_cnt}} {status}")
        print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
        pause()

    def update(self):
        clear_screen()
        header("UPDATE VOTING STATION", THEME_ADMIN)
        stations = self._stations.get_all()
        if not stations:
            print(); info("No stations found."); pause(); return
        print()
        for station in stations.values():
            print(f"  {THEME_ADMIN}{station.id}.{RESET} {station.name} "
                  f"{DIM}- {station.location}{RESET}")
        try:
            sid = int(prompt("\nEnter Station ID to update: "))
        except ValueError:
            error("Invalid input."); pause(); return
        station = self._stations.get(sid)
        if not station:
            error("Station not found."); pause(); return

        print(f"\n  {BOLD}Updating: {station.name}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {}
        new_name = prompt(f"Name [{station.name}]: ")
        if new_name:
            updates["name"] = new_name
        new_location = prompt(f"Location [{station.location}]: ")
        if new_location:
            updates["location"] = new_location
        new_region = prompt(f"Region [{station.region}]: ")
        if new_region:
            updates["region"] = new_region
        new_capacity = prompt(f"Capacity [{station.capacity}]: ")
        if new_capacity:
            try:
                updates["capacity"] = int(new_capacity)
            except ValueError:
                warning("Invalid number, keeping old value.")
        new_supervisor = prompt(f"Supervisor [{station.supervisor}]: ")
        if new_supervisor:
            updates["supervisor"] = new_supervisor
        new_contact = prompt(f"Contact [{station.contact}]: ")
        if new_contact:
            updates["contact"] = new_contact

        self._stations.update(
            sid, updates, self._store.current_user.username
        )
        name = updates.get("name", station.name)
        print()
        success(f"Station '{name}' updated successfully!")
        pause()

   