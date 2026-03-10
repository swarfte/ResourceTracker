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

    # Tag, Status, and Search filters
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        selected_tag = st.selectbox(
            "🏷️ Tag",
            options=["All"] + all_tags,
            help="Filter resources by import tag",
            index=0
        )

    with col2:
        selected_status = st.selectbox(
            "✅ Status",
            options=["All", "Unused", "Used"],
            help="Filter resources by usage status",
            index=1
        )

    # Search functionality
    with col3:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Search all columns...",
            label_visibility="visible"
        )
        strict_mode = st.checkbox(
            "🎯 Strict mode",
            value=True,
            help="When enabled, only exact matches are returned. When disabled, partial matches are included.",
            key=f"strict_mode_{location_key}"
        )

    # Apply filters
    filtered = location_resources

    # Filter by tag first
    if selected_tag != "All":
        filtered = data_manager.filter_by_tag(selected_tag, filtered)

    # Then filter by status
    if selected_status != "All":
        filtered = data_manager.filter_by_status(selected_status, filtered)

    # Then filter by search query
    if search_query:
        filtered = data_manager.search_resources(search_query, filtered, strict=strict_mode)

    # Show filter results
    filter_info_parts = []
    if selected_tag != "All":
        filter_info_parts.append(f"tag: '{selected_tag}'")
    if selected_status != "All":
        filter_info_parts.append(f"status: '{selected_status}'")
    if search_query:
        mode_text = " (strict)" if strict_mode else ""
        filter_info_parts.append(f"search: '{search_query}'{mode_text}")

    if filter_info_parts:
        filter_text = ", ".join(filter_info_parts)
        st.info(f"📊 Found **{len(filtered)}** of **{total_in_location}** resources ({filter_text})")

    # Check if filters returned no results
    if not filtered:
        st.warning("⚠️ No resources found matching the filters")
        return

    # Convert to DataFrame for display
    df_data = [r.data for r in filtered]
    df = pd.DataFrame(df_data)

    # Add ID, Tag, and Status columns at the beginning
    df.insert(0, '🆔 ID', [r.resource_id for r in filtered])
    df.insert(1, '🏷️ Tag', [r.tag for r in filtered])
    df.insert(2, '✅ Status', [r.status.capitalize() if r.status else "Unused" for r in filtered])

    # Add Select column first (at position 0)
    df.insert(0, '☐️ Select', False)

    # Initialize session state for this location's select_all functionality
    select_all_storage_key = f'_select_all_state_{location_key}'
    if select_all_storage_key not in st.session_state:
        st.session_state[select_all_storage_key] = False

    # Counter for editor versions - increments when select_all is clicked
    editor_version_key = f'_editor_version_{location_key}'
    if editor_version_key not in st.session_state:
        st.session_state[editor_version_key] = 0

    # Select All checkbox and action buttons
    st.subheader("📋 Resource List")
    col1, col2, col3 = st.columns([2, 1, 4])

    with col1:
        # Use session state value for checkbox
        select_all = st.checkbox(
            "☑️ Select All",
            value=st.session_state[select_all_storage_key],
            help="Select all filtered resources",
            key=f"select_all_{location_key}"  # Unique key for each location page
        )

    with col2:
        # Clear selection button
        if st.button("🗑️ Clear", help="Clear all selections", key=f"clear_{location_key}"):
            st.session_state[select_all_storage_key] = False
            st.session_state[editor_version_key] = 0  # Reset to base version
            st.rerun()
            return  # Stop execution - don't render old state

    # Detect if select_all checkbox changed
    if select_all != st.session_state[select_all_storage_key]:
        st.session_state[select_all_storage_key] = select_all
        # Clear all versioned editor states to force fresh render
        for key in list(st.session_state.keys()):
            if key.startswith(f'editor_{location_key}'):
                del st.session_state[key]
        st.rerun()  # Rerun to apply the change
        return  # Stop execution - don't render old state

    # Use static editor key - version tracking removed for simplicity
    editor_key = f'editor_{location_key}'

    # Update df based on select_all state (for display purposes)
    df.loc[:, '☐️ Select'] = st.session_state[select_all_storage_key]

    # Display editable table with key for state persistence
    edited_df = st.data_editor(
        df,
        width='stretch',
        hide_index=True,
        key=editor_key,
        column_config={
            "☐️ Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select rows to move to another location or change status",
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
            ),
            "✅ Status": st.column_config.TextColumn(
                "Status",
                help="Resource usage status",
                width="small",
                disabled=True
            )
        },
        height=400
    )

    # Get the current selections from the widget's session state (most up-to-date)
    if editor_key in st.session_state and isinstance(st.session_state[editor_key], pd.DataFrame) and '☐️ Select' in st.session_state[editor_key].columns:
        widget_df = st.session_state[editor_key]
        selected_rows = widget_df[widget_df['☐️ Select'] == True]
    else:
        selected_rows = edited_df[edited_df['☐️ Select'] == True]

    if len(selected_rows) > 0:
        st.divider()

        # Check status of selected rows
        selected_statuses = selected_rows['✅ Status'].tolist()
        has_unused = 'Unused' in selected_statuses
        has_used = 'Used' in selected_statuses

        # Action buttons section
        col1, col2, col3, col4 = st.columns([2, 2, 1.5, 2])

        with col1:
            st.info(f"📌 **{len(selected_rows)}** row(s) selected")

        with col2:
            # Get other locations for the dropdown
            other_locations = [(k, v) for k, v in LOCATION_DISPLAY_NAMES.items() if k != location_key]
            target_location = st.selectbox(
                label="Move to:",
                options=[k for k, v in other_locations],
                format_func=lambda x: LOCATION_DISPLAY_NAMES[x],
                help="Select target location",
                key=f"move_to_{location_key}"
            )

        with col3:
            # Move button
            if st.button("📤 Move", type="primary", use_container_width=True, key=f"move_btn_{location_key}"):
                # Get resource IDs to move
                selected_ids = selected_rows['🆔 ID'].tolist()

                try:
                    # Move resources
                    data_manager.move_resources(selected_ids, state, target_location)
                    data_manager.save_state(state)

                    # Clear selections after move
                    st.session_state[select_all_storage_key] = False
                    # Clear the editor's checkbox selections
                    if editor_key in st.session_state and isinstance(st.session_state[editor_key], pd.DataFrame) and '☐️ Select' in st.session_state[editor_key].columns:
                        st.session_state[editor_key]['☐️ Select'] = False

                    st.success(f"✅ Successfully moved **{len(selected_ids)}** resources to **{LOCATION_DISPLAY_NAMES[target_location]}**!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error moving resources: {str(e)}")
                    st.exception(e)

        with col4:
            # Status change buttons
            if has_unused and has_used:
                # Mixed selection - show both options
                col4a, col4b = st.columns(2)
                with col4a:
                    mark_used_btn = st.button("✅ Mark Used", help="Mark selected as used (keeps location)", key=f"mark_used_{location_key}")
                with col4b:
                    mark_unused_btn = st.button("⬜ Mark Unused", help="Mark selected as unused (keeps location)", key=f"mark_unused_{location_key}")
            elif has_unused:
                # All unused - only show Mark Used
                mark_used_btn = st.button("✅ Mark Used", help="Mark selected as used (keeps location)", key=f"mark_used_{location_key}")
                mark_unused_btn = None
            else:
                # All used - only show Mark Unused
                mark_used_btn = None
                mark_unused_btn = st.button("⬜ Mark Unused", help="Mark selected as unused (keeps location)", key=f"mark_unused_{location_key}")

        # Handle Mark as Used button click
        if mark_used_btn and has_unused:
            selected_ids = selected_rows['🆔 ID'].tolist()
            try:
                data_manager.mark_as_used(selected_ids, state)
                data_manager.save_state(state)

                # Clear selections after status change
                st.session_state[select_all_storage_key] = False
                # Clear the editor's checkbox selections
                if editor_key in st.session_state and isinstance(st.session_state[editor_key], pd.DataFrame) and '☐️ Select' in st.session_state[editor_key].columns:
                    st.session_state[editor_key]['☐️ Select'] = False

                st.success(f"✅ Successfully marked **{len(selected_ids)}** resources as **Used**!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error marking as used: {str(e)}")
                st.exception(e)

        # Handle Mark as Unused button click
        if mark_unused_btn and has_used:
            selected_ids = selected_rows['🆔 ID'].tolist()
            try:
                data_manager.mark_as_unused(selected_ids, state)
                data_manager.save_state(state)

                # Clear selections after status change
                st.session_state[select_all_storage_key] = False
                # Clear the editor's checkbox selections
                if editor_key in st.session_state and isinstance(st.session_state[editor_key], pd.DataFrame) and '☐️ Select' in st.session_state[editor_key].columns:
                    st.session_state[editor_key]['☐️ Select'] = False

                st.success(f"✅ Successfully marked **{len(selected_ids)}** resources as **Unused**!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error marking as unused: {str(e)}")
                st.exception(e)

    else:
        # Show hint when no rows selected
        st.caption("💡 Select resources using the checkboxes or 'Select All' to move them or change their status")
