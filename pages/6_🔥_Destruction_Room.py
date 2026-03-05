"""Destruction Room page - Display and manage resources in destruction room."""

from utils.location_page import render_location_page
from utils.data_manager import LOCATION_DISPLAY_NAMES


def main():
    """Main destruction room page."""
    render_location_page("destruction_room", LOCATION_DISPLAY_NAMES["destruction_room"])


if __name__ == "__main__":
    main()
