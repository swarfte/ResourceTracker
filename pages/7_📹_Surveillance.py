"""Surveillance page - Display and manage resources in surveillance."""

from utils.location_page import render_location_page
from utils.data_manager import LOCATION_DISPLAY_NAMES


def main():
    """Main surveillance page."""
    render_location_page("surveillance", LOCATION_DISPLAY_NAMES["surveillance"])


if __name__ == "__main__":
    main()
