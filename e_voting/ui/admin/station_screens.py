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

   