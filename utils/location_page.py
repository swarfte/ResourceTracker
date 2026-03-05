"""Shared location page rendering logic."""

import streamlit as st
import pandas as pd
from utils.session_manager import SessionManager
from utils.data_manager import DataManager, LOCATIONS, LOCATION_DISPLAY_NAMES


def render_location_page(location_key: str, location_display: str):
    """Render a location page with the given location.

    Args:
        location_key: Internal location key (e.g., "warehouse")
        location_display: Display name with emoji (e.g., "📦 Warehouse")
    """
    st.title(location_display)

    # Initialize session state
    SessionManager.initialize()
    state = SessionManager.get_state()
    data_manager = SessionManager.get_data_manager()

    # Get resources for this location
    location_resources = state.resources[location_key]
    total_in_location = len(location_resources)

    # Show total count
    st.caption(f"Total: **{total_in_location}** resources")

    # Check if there are any resources
    if not location_resources:
        st.warning(f"⚠️ No resources in {location_display}.")
        if location_key == "warehouse":
            st.info("💡 Tip: Import files on the 📥 Resource Import page to add resources to the warehouse.")
        else:
            st.info(f"💡 Tip: Move resources from other locations to {location_display}.")
        return

    # Get all unique tags
    all_tags = data_manager.get_all_tags(location_resources)

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
    filtered = location_resources

    # Filter by tag first
    if selected_tag != "All":
        filtered = data_manager.filter_by_tag(selected_tag, filtered)

    # Then filter by search query
    if search_query:
        filtered = data_manager.search_resources(search_query, filtered)

    # Show filter results
    if selected_tag != "All" and search_query:
        st.info(f"📊 Found **{len(filtered)}** of **{total_in_location}** resources (tag: '{selected_tag}', search: '{search_query}')")
    elif selected_tag != "All":
        st.info(f"📊 Found **{len(filtered)}** of **{total_in_location}** resources with tag '{selected_tag}'")
    elif search_query:
        st.info(f"📊 Found **{len(filtered)}** of **{total_in_location}** resources matching '{search_query}'")

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
        width='stretch',
        hide_index=True,
        column_config={
            "☐️ Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select rows to move to another location",
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

    # Handle move to another location
    selected_rows = edited_df[edited_df['☐️ Select'] == True]

    if len(selected_rows) > 0:
        st.divider()
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.info(f"📌 **{len(selected_rows)}** row(s) selected")

        with col2:
            # Get other locations for the dropdown
            other_locations = [(k, v) for k, v in LOCATION_DISPLAY_NAMES.items() if k != location_key]
            target_location = st.selectbox(
                "Move to:",
                options=[k for k, v in other_locations],
                format_func=lambda x: LOCATION_DISPLAY_NAMES[x],
                help="Select target location"
            )

        with col3:
            if st.button("📤 Move", type="primary", use_container_width=True):
                # Get resource IDs to move
                selected_ids = selected_rows['🆔 ID'].tolist()

                # Move resources
                data_manager.move_resources(selected_ids, state, target_location)
                data_manager.save_state(state)

                st.success(f"✅ Successfully moved **{len(selected_ids)}** resources to **{LOCATION_DISPLAY_NAMES[target_location]}**!")
                st.rerun()
