"""Card Room page - Display and manage resources in card room."""

from utils.location_page import render_location_page
from utils.data_manager import LOCATION_DISPLAY_NAMES


def main():
    """Main card room page."""
    render_location_page("card_room", LOCATION_DISPLAY_NAMES["card_room"])


if __name__ == "__main__":
    main()
