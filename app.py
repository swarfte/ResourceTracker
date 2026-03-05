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
                use_container_width=True,
                hide_index=True
            )

            if len(df) > 10:
                st.caption(f"Showing first 10 of {len(df)} rows")

            # Import button
            st.divider()
            if st.button(f"🚀 Import {len(df)} Resources as Unused", type="primary", use_container_width=True):
                # Import resources with tag
                data_manager.import_resources(df, state, tag=import_tag)
                data_manager.save_state(state)

                tag_source = "filename" if not tag.strip() else "custom tag"
                st.success(f"✅ Successfully imported **{len(df)}** resources as unused with tag '**{import_tag}**' ({tag_source})!")
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

        1. **Set a tag (optional)** - Enter a custom tag or leave empty to use the filename as the tag
        2. **Upload a file** - Click the button above to select a CSV or Excel file
        3. **Preview data** - Review the first 10 rows of your data
        4. **Import** - Click the import button to add all resources as "unused"
        5. **Manage** - Navigate to 📦 Unused Resources to categorize them

        ### 📄 File Requirements:
        - CSV files (UTF-8, GBK, or Latin1 encoding)
        - Excel files (.xls or .xlsx)
        - No specific column requirements - all columns are imported

        ### 🏷️ About Tags:
        - Tags help you organize resources by import batch
        - If you don't provide a tag, the **filename** will be used automatically
        - You can filter resources by tag on the Unused/Used pages
        - Example: File 'test-data.csv' → Tag 'test-data'
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
