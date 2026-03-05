"""Warehouse page - Display and manage resources in warehouse."""

from utils.location_page import render_location_page
from utils.data_manager import LOCATION_DISPLAY_NAMES


def main():
    """Main warehouse page."""
    render_location_page("warehouse", LOCATION_DISPLAY_NAMES["warehouse"])


if __name__ == "__main__":
    main()
