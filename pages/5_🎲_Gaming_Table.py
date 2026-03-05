"""Gaming Table page - Display and manage resources at gaming tables."""

from utils.location_page import render_location_page
from utils.data_manager import LOCATION_DISPLAY_NAMES


def main():
    """Main gaming table page."""
    render_location_page("gaming_table", LOCATION_DISPLAY_NAMES["gaming_table"])


if __name__ == "__main__":
    main()
