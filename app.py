"""ResourceTracker - Main application entry point and import page."""

import streamlit as st
from utils.session_manager import SessionManager
from utils.data_manager import DataManager, LOCATION_DISPLAY_NAMES
from utils.file_parser import FileParser


def main():
    """Main import page functionality."""
    st.title("📥 Resource Import")
    st.write("Upload CSV or Excel files to import resources into the warehouse.")

    # Initialize session state
    SessionManager.initialize()
    state = SessionManager.get_state()
    data_manager = SessionManager.get_data_manager()

    # Tag input field
    st.subheader("🏷️ Tag Configuration")
    tag = st.text_input(
        "Import Tag (Optional)",
        placeholder="Enter a custom tag (e.g., 'batch-1', 'test-data', '2024-03-05')",
        help="This tag will be applied to all resources. If left empty, the filename will be used as the tag.",
        value=""
    )

    st.divider()

    # File upload UI
    uploaded_file = st.file_uploader(
        "Upload Resource File",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, XLS, XLSX",
        label_visibility="visible"
    )

    if uploaded_file:
        # Extract filename without extension as default tag
        filename = uploaded_file.name
        filename_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename

        # Use custom tag if provided, otherwise use filename
        import_tag = tag if tag.strip() else filename_without_ext

        st.info(f"📁 File selected: **{filename}**")
        st.info(f"🏷️ Tag: **{import_tag}** {'(using filename)' if not tag.strip() else '(custom tag)'}")

        # Parse the file
        df = FileParser.parse_file(uploaded_file)

        if df is not None:
            st.success(f"✅ File loaded successfully: **{len(df)}** rows detected")

            # Show preview (first 10 rows)
            st.subheader("📊 Data Preview")
            st.dataframe(
                df.head(10),
                width='stretch',
                hide_index=True
            )

            if len(df) > 10:
                st.caption(f"Showing first 10 of {len(df)} rows")

            # Import button
            st.divider()
            if st.button(f"🚀 Import {len(df)} Resources to Warehouse", type="primary", use_container_width=True):
                # Import resources with tag
                data_manager.import_resources(df, state, tag=import_tag)
                data_manager.save_state(state)

                tag_source = "filename" if not tag.strip() else "custom tag"
                st.success(f"✅ Successfully imported **{len(df)}** resources to **Warehouse** with tag '**{import_tag}**' ({tag_source})!")
                st.balloons()

                # Show summary
                total_count = data_manager.get_total_count(state)
                warehouse_count = len(state.resources["warehouse"])
                st.info(f"📦 Total resources: **{total_count}** | Warehouse: **{warehouse_count}**")

        else:
            st.error("❌ Failed to parse file. Please check the file format and try again.")
            st.help("Supported formats: CSV (UTF-8, GBK encoding), Excel (.xls, .xlsx)")

    else:
        # Show empty state
        st.markdown("""
        ### 📋 How to use:

        1. **Set a tag (optional)** - Enter a custom tag or leave empty to use the filename as the tag
        2. **Upload a file** - Click the button above to select a CSV or Excel file
        3. **Preview data** - Review the first 10 rows of your data
        4. **Import** - Click the import button to add all resources to the **Warehouse**
        5. **Manage** - Navigate to different locations to move resources around

        ### 📄 File Requirements:
        - CSV files (UTF-8, GBK, or Latin1 encoding)
        - Excel files (.xls or .xlsx)
        - No specific column requirements - all columns are imported

        ### 🏷️ About Tags:
        - Tags help you organize resources by import batch
        - If you don't provide a tag, the **filename** will be used automatically
        - You can filter resources by tag on any location page
        - Example: File 'test-data.csv' → Tag 'test-data'

        ### 📍 About Locations:
        - **Warehouse**: Default location for all imported resources
        - Move resources to other locations as they progress through your workflow
        - Each location page shows resources currently at that location
        """)

        # Show current stats if there's data
        total_count = data_manager.get_total_count(state)
        if total_count > 0:
            st.divider()
            st.subheader("📊 Current Statistics")

            # Get location counts
            location_counts = data_manager.get_location_counts(state)

            # Display metrics for all 6 locations
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(LOCATION_DISPLAY_NAMES["warehouse"], location_counts["warehouse"])
            with col2:
                st.metric(LOCATION_DISPLAY_NAMES["card_room"], location_counts["card_room"])
            with col3:
                st.metric(LOCATION_DISPLAY_NAMES["gaming_pit"], location_counts["gaming_pit"])

            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric(LOCATION_DISPLAY_NAMES["gaming_table"], location_counts["gaming_table"])
            with col5:
                st.metric(LOCATION_DISPLAY_NAMES["destruction_room"], location_counts["destruction_room"])
            with col6:
                st.metric(LOCATION_DISPLAY_NAMES["surveillance"], location_counts["surveillance"])

            st.caption(f"**Total Resources:** {total_count}")


if __name__ == "__main__":
    main()
