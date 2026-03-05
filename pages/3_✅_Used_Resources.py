"""Used Resources page - Read-only view of categorized resources."""

import streamlit as st
import pandas as pd
from utils.session_manager import SessionManager
from utils.data_manager import DataManager


def main():
    """Display used resources with search (read-only)."""
    st.title("✅ Used Resources")

    # Initialize session state
    SessionManager.initialize()
    state = SessionManager.get_state()
    data_manager = SessionManager.get_data_manager()

    # Show total count
    total_used = len(state.used_resources)
    st.caption(f"Total: **{total_used}** resources")

    # Check if there are any used resources
    if not state.used_resources:
        st.warning("⚠️ No used resources found. Move resources from 📦 Unused Resources page.")
        st.info("💡 Tip: Navigate to the Unused Resources page to select and move resources.")
        return

    # Get all unique tags
    all_tags = data_manager.get_all_tags(state.used_resources)

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
    filtered = state.used_resources

    # Filter by tag first
    if selected_tag != "All":
        filtered = data_manager.filter_by_tag(selected_tag, filtered)

    # Then filter by search query
    if search_query:
        filtered = data_manager.search_resources(search_query, filtered)

    # Show filter results
    if selected_tag != "All" and search_query:
        st.info(f"📊 Found **{len(filtered)}** of **{total_used}** resources (tag: '{selected_tag}', search: '{search_query}')")
    elif selected_tag != "All":
        st.info(f"📊 Found **{len(filtered)}** of **{total_used}** resources with tag '{selected_tag}'")
    elif search_query:
        st.info(f"📊 Found **{len(filtered)}** of **{total_used}** resources matching '{search_query}'")

    # Check if filters returned no results
    if not filtered:
        st.warning("⚠️ No resources found matching the filters")
        return

    # Convert to DataFrame for display
    df_data = [r.data for r in filtered]

    # Add metadata columns
    df = pd.DataFrame(df_data)
    df.insert(0, '🆔 ID', [r.resource_id for r in filtered])
    df.insert(1, '🏷️ Tag', [r.tag for r in filtered])
    df.insert(2, '📅 Imported', [r.import_date.split('T')[0] for r in filtered])

    # Display read-only table
    st.subheader("📋 Resource List")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # Show summary
    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Used", value=len(state.used_resources))

    with col2:
        st.metric(label="Showing", value=len(filtered))

    with col3:
        if selected_tag != "All":
            tag_count = len(data_manager.filter_by_tag(selected_tag, state.used_resources))
            st.metric(label=f"Tag: {selected_tag}", value=tag_count)
        else:
            st.metric(label="Tags", value=len(all_tags))

    with col4:
        if state.used_resources:
            latest_date = max(r.import_date for r in state.used_resources).split('T')[0]
            st.metric(label="Latest Import", value=latest_date)


if __name__ == "__main__":
    main()
