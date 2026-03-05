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

    # Search functionality
    st.divider()
    search_query = st.text_input(
        "🔍 Search resources",
        placeholder="Search all columns...",
        label_visibility="collapsed"
    )

    # Filter resources based on search
    if search_query:
        filtered = data_manager.search_resources(search_query, state.used_resources)
        st.info(f"📊 Found **{len(filtered)}** of **{total_used}** resources matching '{search_query}'")
    else:
        filtered = state.used_resources

    # Check if search returned no results
    if not filtered:
        st.warning(f"⚠️ No resources found matching '{search_query}'")
        return

    # Convert to DataFrame for display
    df_data = [r.data for r in filtered]

    # Add metadata columns
    df = pd.DataFrame(df_data)
    df.insert(0, '🆔 ID', [r.resource_id for r in filtered])
    df.insert(1, '📅 Imported', [r.import_date.split('T')[0] for r in filtered])

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
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Total Used", value=len(state.used_resources))

    with col2:
        st.metric(label="Showing", value=len(filtered))

    with col3:
        if state.used_resources:
            latest_date = max(r.import_date for r in state.used_resources).split('T')[0]
            st.metric(label="Latest Import", value=latest_date)


if __name__ == "__main__":
    main()
