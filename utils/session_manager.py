"""Session state management for ResourceTracker."""

import streamlit as st
from utils.data_manager import DataManager, ApplicationState


class SessionManager:
    """Initialize and manage Streamlit session state."""

    STATE_KEY = "app_state"
    DATA_MANAGER_KEY = "data_manager"

    @staticmethod
    def initialize():
        """Initialize all session state variables."""
        if SessionManager.STATE_KEY not in st.session_state:
            dm = DataManager()
            state = dm.load_state()
            st.session_state[SessionManager.STATE_KEY] = state
            st.session_state[SessionManager.DATA_MANAGER_KEY] = dm

    @staticmethod
    def get_state() -> ApplicationState:
        """Get current application state from session."""
        return st.session_state[SessionManager.STATE_KEY]

    @staticmethod
    def get_data_manager() -> DataManager:
        """Get data manager instance."""
        return st.session_state[SessionManager.DATA_MANAGER_KEY]

    @staticmethod
    def save_state():
        """Save current state to disk."""
        dm = SessionManager.get_data_manager()
        state = SessionManager.get_state()
        dm.save_state(state)
