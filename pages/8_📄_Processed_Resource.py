"""Processed Resources page - Display and view processed PDF files."""

import os
import base64
import json
import streamlit as st
from pathlib import Path
from typing import Dict


# File to store used/unused status
STATUS_FILE = Path(__file__).parent.parent / "data" / "processed_status.json"


def load_used_status() -> Dict[str, bool]:
    """Load used status from JSON file.

    Returns:
        Dictionary mapping PDF filenames to used status
    """
    if not STATUS_FILE.exists():
        # Create data directory if it doesn't exist
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {}

    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_used_status(status: Dict[str, bool]) -> None:
    """Save used status to JSON file.

    Args:
        status: Dictionary mapping PDF filenames to used status
    """
    try:
        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f, indent=2)
    except IOError as e:
        st.error(f"Error saving status: {str(e)}")


def get_pdf_files(processed_dir: str) -> list:
    """Get list of PDF files in the processed directory.

    Args:
        processed_dir: Path to the processed directory

    Returns:
        List of PDF filenames
    """
    if not os.path.exists(processed_dir):
        return []

    pdf_files = []
    for filename in os.listdir(processed_dir):
        if filename.lower().endswith('.pdf'):
            pdf_files.append(filename)

    return sorted(pdf_files)


def filter_pdf_files(pdf_files: list, search_term: str) -> list:
    """Filter PDF files by search term (case-insensitive).

    Args:
        pdf_files: List of PDF filenames
        search_term: Search term to filter by

    Returns:
        Filtered list of PDF filenames
    """
    if not search_term:
        return pdf_files

    search_term_lower = search_term.lower()
    return [pdf for pdf in pdf_files if search_term_lower in pdf.lower()]


def filter_by_status(
    pdf_files: list,
    used_status: Dict[str, bool],
    view_type: str
) -> list:
    """Filter PDF files by used/unused status.

    Args:
        pdf_files: List of PDF filenames
        used_status: Dictionary mapping PDFs to their used status
        view_type: "unused", "used", or "all"

    Returns:
        Filtered list of PDF filenames
    """
    if view_type == "all":
        return pdf_files
    elif view_type == "used":
        return [pdf for pdf in pdf_files if used_status.get(pdf, False)]
    else:  # unused (default)
        return [pdf for pdf in pdf_files if not used_status.get(pdf, False)]


def pdf_to_base64(pdf_path: str) -> str:
    """Convert PDF file to base64 string for embedding.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Base64 encoded string
    """
    with open(pdf_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def main():
    """Main processed resources page."""
    st.set_page_config(
        page_title="Processed Resources",
        page_icon="📄",
        layout="wide"
    )

    # Initialize session state
    if "processed_selected_pdf" not in st.session_state:
        st.session_state.processed_selected_pdf = None

    st.title("📄 Processed Resources")

    # Get the processed directory path
    script_dir = Path(__file__).parent.parent
    processed_dir = script_dir / "processed"

    # Load used status
    used_status = load_used_status()

    # Get list of PDF files
    all_pdf_files = get_pdf_files(str(processed_dir))

    if not all_pdf_files:
        st.warning("No processed PDF files found in the 'processed' folder.")
        st.info(
            "Place PDF files in the 'processed' folder to view them here.\n\n"
            f"Expected location: `{processed_dir}`"
        )
        return

    # Create two columns: left for controls, right for PDF viewer
    col_controls, col_viewer = st.columns([1, 3])

    with col_controls:
        # View filter section
        st.markdown("### 🔍 View & Filter")

        # View type selector (default to "unused")
        view_type = st.radio(
            "Show:",
            options=["unused", "used", "all"],
            format_func=lambda x: {
                "unused": "🆕 Unused Only",
                "used": "✅ Used Only",
                "all": "📄 All Resources"
            }.get(x, x),
            horizontal=False,
            label_visibility="collapsed",
            key="view_type_selector"
        )

        st.markdown("---")

        # Search section
        st.markdown("### 🔎 Search")
        search_term = st.text_input(
            "Filter by name:",
            placeholder="Type to filter...",
            key="pdf_search",
            label_visibility="collapsed"
        )

        # First filter by search term
        filtered_by_search = filter_pdf_files(all_pdf_files, search_term)

        # Then filter by status
        filtered_files = filter_by_status(filtered_by_search, used_status, view_type)

        # Show file count with breakdown
        unused_count = sum(1 for f in filtered_by_search if not used_status.get(f, False))
        used_count = sum(1 for f in filtered_by_search if used_status.get(f, False))
        st.caption(f"Unused: {unused_count} | Used: {used_count} | Total: {len(filtered_by_search)}")

        if not filtered_files:
            st.warning(f"No PDF files found for view: {view_type}")
            return

        st.markdown("---")

        # PDF list section
        st.markdown("### 📄 PDF Files")

        # List all filtered PDFs as buttons
        for pdf in filtered_files:
            is_used = used_status.get(pdf, False)
            is_selected = st.session_state.processed_selected_pdf == pdf

            # Determine button style based on selection and used status
            if is_selected:
                button_label = f"👁️ {pdf}"
                button_type = "primary"
            elif is_used:
                button_label = f"✅ {pdf}"
                button_type = "secondary"
            else:
                button_label = f"🆕 {pdf}"
                button_type = "secondary"

            if st.button(button_label, key=f"btn_{pdf}", use_container_width=True, type=button_type):
                st.session_state.processed_selected_pdf = pdf
                st.rerun()

    with col_viewer:
        # PDF Viewer section (always at top)
        if st.session_state.processed_selected_pdf:
            selected_pdf = st.session_state.processed_selected_pdf
            pdf_path = processed_dir / selected_pdf

            if pdf_path.exists():
                # Display PDF
                try:
                    # Read PDF for download
                    with open(pdf_path, 'rb') as f:
                        pdf_bytes = f.read()

                    # Get current used status
                    is_used = used_status.get(selected_pdf, False)

                    st.subheader(f"Viewing: {selected_pdf}")

                    # Toggle used/unused status
                    col_mark, col_download = st.columns([2, 1])

                    with col_mark:
                        if st.button(
                            f"✏️ Mark as {'Unused' if is_used else 'Used'}",
                            key=f"mark_{selected_pdf}",
                            use_container_width=True
                        ):
                            used_status[selected_pdf] = not is_used
                            save_used_status(used_status)
                            st.rerun()

                    with col_download:
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=selected_pdf,
                            mime="application/pdf",
                            key=f"download_{selected_pdf}",
                            use_container_width=True
                        )

                    # Display PDF using base64 embedding
                    pdf_base64 = pdf_to_base64(str(pdf_path))
                    st.markdown(
                        f"""
                        <embed
                            src="data:application/pdf;base64,{pdf_base64}"
                            width="100%"
                            height="750"
                            type="application/pdf"
                            style="border: 1px solid #ddd; border-radius: 8px;"
                        />
                        """,
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.error(f"Error loading PDF: {str(e)}")
                    st.info(
                        "Try downloading the PDF and opening it in your browser "
                        "or PDF viewer."
                    )
            else:
                st.error(f"File not found: {selected_pdf}")
        else:
            st.info(
                "👈 Select a PDF file from the list on the left to view it here."
            )
            # Show some helpful instructions
            st.markdown("""
            ### Instructions:
            1. Choose view type (Unused, Used, or All)
            2. Use the search box to filter PDFs by name
            3. Click on any PDF file to view it
            4. Mark PDFs as Used/Unused to track their status
            5. Download the PDF if needed
            """)


if __name__ == "__main__":
    main()
