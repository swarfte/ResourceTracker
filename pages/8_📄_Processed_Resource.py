"""Processed Resources page - Display and view processed PDF files."""

import os
import base64
import streamlit as st
from pathlib import Path


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

    # Initialize session state for selected PDF
    if "processed_selected_pdf" not in st.session_state:
        st.session_state.processed_selected_pdf = None

    st.title("📄 Processed Resources")

    # Get the processed directory path
    script_dir = Path(__file__).parent.parent
    processed_dir = script_dir / "processed"

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
        # Search section
        st.markdown("### 🔍 Search")
        search_term = st.text_input(
            "Filter by name:",
            placeholder="Type to filter...",
            key="pdf_search",
            label_visibility="collapsed"
        )

        # Filter files
        filtered_files = filter_pdf_files(all_pdf_files, search_term)

        # Show file count
        st.metric(
            "Results",
            f"{len(filtered_files)}/{len(all_pdf_files)}"
        )

        if not filtered_files:
            st.warning("No PDF files match your search criteria.")
            return

        st.markdown("---")

        # PDF list section
        st.markdown("### 📄 PDF Files")

        # List all filtered PDFs as buttons
        for pdf in filtered_files:
            # Highlight the selected PDF
            if st.session_state.processed_selected_pdf == pdf:
                st.button(
                    f"✅ {pdf}",
                    key=f"btn_{pdf}",
                    use_container_width=True,
                    type="primary"
                )
            else:
                if st.button(f"📄 {pdf}", key=f"btn_{pdf}", use_container_width=True):
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

                    st.subheader(f"Viewing: {selected_pdf}")

                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=selected_pdf,
                        mime="application/pdf",
                        key=f"download_{selected_pdf}"
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
            1. Use the search box to filter PDFs by name
            2. Click on any PDF file to view it
            3. The PDF will be displayed here
            4. Download the PDF if needed
            """)


if __name__ == "__main__":
    main()
