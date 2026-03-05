"""Gaming Pit page - Display and manage resources in gaming pit."""

from utils.location_page import render_location_page
from utils.data_manager import LOCATION_DISPLAY_NAMES


def main():
    """Main gaming pit page."""
    render_location_page("gaming_pit", LOCATION_DISPLAY_NAMES["gaming_pit"])


if __name__ == "__main__":
    main()
