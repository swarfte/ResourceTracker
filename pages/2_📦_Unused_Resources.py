"""Unused Resources page - Display, search, and move resources."""

import streamlit as st
import pandas as pd
from utils.session_manager import SessionManager
from utils.data_manager import DataManager


def main():
    """Display unused resources with search and selection."""
    st.title(f"📦 Unused Resources")

    # Initialize session state
    SessionManager.initialize()
    state = SessionManager.get_state()
    data_manager = SessionManager.get_data_manager()

    # Show total count
    total_unused = len(state.unused_resources)
    st.caption(f"Total: **{total_unused}** resources")

    # Check if there are any resources
    if not state.unused_resources:
        st.warning("⚠️ No unused resources found. Import files on the 📥 Resource Import page.")
        st.info("💡 Tip: Navigate to the home page to upload CSV or Excel files.")
        return

    # Get all unique tags
    all_tags = data_manager.get_all_tags(state.unused_resources)

    # Filter and search section
    st.divider()

    # Tag filter
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_tag = st.selectbox(
            "🏷️ Filter by Tag",
            options=["All"] + all_tags,
            help="Filter resources by import tag",
            index=0
        )

    # Search functionality
    with col2:
        search_query = st.text_input(
            "🔍 Search resources",
            placeholder="Search all columns...",
            label_visibility="visible"
        )

    # Apply filters
    filtered = state.unused_resources

    # Filter by tag first
    if selected_tag != "All":
        filtered = data_manager.filter_by_tag(selected_tag, filtered)

    # Then filter by search query
    if search_query:
        filtered = data_manager.search_resources(search_query, filtered)

    # Show filter results
    if selected_tag != "All" and search_query:
        st.info(f"📊 Found **{len(filtered)}** of **{total_unused}** resources (tag: '{selected_tag}', search: '{search_query}')")
    elif selected_tag != "All":
        st.info(f"📊 Found **{len(filtered)}** of **{total_unused}** resources with tag '{selected_tag}'")
    elif search_query:
        st.info(f"📊 Found **{len(filtered)}** of **{total_unused}** resources matching '{search_query}'")

    # Check if filters returned no results
    if not filtered:
        st.warning("⚠️ No resources found matching the filters")
        return

    # Convert to DataFrame for display
    df_data = [r.data for r in filtered]
    df = pd.DataFrame(df_data)

    # Add selection, ID, and Tag columns at the beginning
    df.insert(0, '☐️ Select', False)
    df.insert(1, '🆔 ID', [r.resource_id for r in filtered])
    df.insert(2, '🏷️ Tag', [r.tag for r in filtered])

    # Display editable table
    st.subheader("📋 Resource List")
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "☐️ Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select rows to move to used resources",
                width="small"
            ),
            "🆔 ID": st.column_config.TextColumn(
                "ID",
                help="Unique resource identifier",
                width="small",
                disabled=True
            ),
            "🏷️ Tag": st.column_config.TextColumn(
                "Tag",
                help="Import batch tag",
                width="small",
                disabled=True
            )
        },
        height=400
    )

    # Handle move to used
    selected_rows = edited_df[edited_df['☐️ Select'] == True]

    if len(selected_rows) > 0:
        st.divider()
        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(f"📌 **{len(selected_rows)}** row(s) selected")

        with col2:
            if st.button(f"📤 Move to Used", type="primary", use_container_width=True):
                # Get resource IDs to move
                selected_ids = selected_rows['🆔 ID'].tolist()

                # Move resources
                data_manager.move_to_used(selected_ids, state)
                data_manager.save_state(state)

                st.success(f"✅ Successfully moved **{len(selected_ids)}** resources to used!")
                st.rerun()


if __name__ == "__main__":
    main()
