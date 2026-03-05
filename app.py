"""ResourceTracker - Main application entry point and import page."""

import streamlit as st
from utils.session_manager import SessionManager
from utils.data_manager import DataManager
from utils.file_parser import FileParser


def main():
    """Main import page functionality."""
    st.title("📥 Resource Import")
    st.write("Upload CSV or Excel files to import resources as 'unused'.")

    # Initialize session state
    SessionManager.initialize()
    state = SessionManager.get_state()
    data_manager = SessionManager.get_data_manager()

    # File upload UI
    uploaded_file = st.file_uploader(
        "Upload Resource File",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, XLS, XLSX",
        label_visibility="visible"
    )

    if uploaded_file:
        st.info(f"📁 File selected: **{uploaded_file.name}**")

        # Parse the file
        df = FileParser.parse_file(uploaded_file)

        if df is not None:
            st.success(f"✅ File loaded successfully: **{len(df)}** rows detected")

            # Show preview (first 10 rows)
            st.subheader("📊 Data Preview")
            st.dataframe(
                df.head(10),
                use_container_width=True,
                hide_index=True
            )

            if len(df) > 10:
                st.caption(f"Showing first 10 of {len(df)} rows")

            # Import button
            st.divider()
            if st.button(f"🚀 Import {len(df)} Resources as Unused", type="primary", use_container_width=True):
                # Import resources
                data_manager.import_resources(df, state)
                data_manager.save_state(state)

                st.success(f"✅ Successfully imported **{len(df)}** resources as unused!")
                st.balloons()

                # Show summary
                st.info(f"📦 Total unused resources: **{len(state.unused_resources)}**")

        else:
            st.error("❌ Failed to parse file. Please check the file format and try again.")
            st.help("Supported formats: CSV (UTF-8, GBK encoding), Excel (.xls, .xlsx)")

    else:
        # Show empty state
        st.markdown("""
        ### 📋 How to use:

        1. **Upload a file** - Click the button above to select a CSV or Excel file
        2. **Preview data** - Review the first 10 rows of your data
        3. **Import** - Click the import button to add all resources as "unused"
        4. **Manage** - Navigate to 📦 Unused Resources to categorize them

        ### 📄 File Requirements:
        - CSV files (UTF-8, GBK, or Latin1 encoding)
        - Excel files (.xls or .xlsx)
        - No specific column requirements - all columns are imported
        """)

        # Show current stats if there's data
        if state.unused_resources or state.used_resources:
            st.divider()
            st.subheader("📊 Current Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="📦 Unused Resources", value=len(state.unused_resources))
            with col2:
                st.metric(label="✅ Used Resources", value=len(state.used_resources))


if __name__ == "__main__":
    main()
