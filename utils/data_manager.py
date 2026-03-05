"""Data models and persistence management for ResourceTracker."""

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


@dataclass
class ResourceItem:
    """Represents a single resource row with metadata."""
    data: Dict[str, Any]  # Original row data from CSV/Excel
    status: str = "unused"  # "unused" or "used"
    import_date: str = field(default_factory=lambda: datetime.now().isoformat())
    resource_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """Convert ResourceItem to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ApplicationState:
    """Main application state for persistence."""
    unused_resources: List[ResourceItem] = field(default_factory=list)
    used_resources: List[ResourceItem] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert ApplicationState to dictionary for JSON serialization."""
        return {
            'unused_resources': [r.to_dict() for r in self.unused_resources],
            'used_resources': [r.to_dict() for r in self.used_resources],
            'last_updated': self.last_updated
        }


class DataManager:
    """Manage resource data operations and persistence."""

    def __init__(self, data_path: str = "data/resources.json"):
        """Initialize DataManager with data file path."""
        self.data_path = data_path
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

    @staticmethod
    def _sanitize_value(value: Any) -> Any:
        """Convert pandas/NumPy types to JSON-serializable types.

        Args:
            value: Value to sanitize

        Returns:
            JSON-serializable value
        """
        # Handle NaN values
        if pd.isna(value):
            return None

        # Handle numpy types
        if isinstance(value, np.integer):
            return int(value)
        elif isinstance(value, np.floating):
            return float(value)
        elif isinstance(value, np.ndarray):
            return value.tolist()
        elif isinstance(value, (np.bool_, bool)):
            return bool(value)

        # Handle datetime objects
        if isinstance(value, (pd.Timestamp, datetime)):
            return value.isoformat()

        return value

    def save_state(self, state: ApplicationState):
        """Save application state to JSON file."""
        state.last_updated = datetime.now().isoformat()

        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)

    def load_state(self) -> ApplicationState:
        """Load application state from JSON file."""
        if not os.path.exists(self.data_path):
            return ApplicationState()

        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            state = ApplicationState()

            # Reconstruct ResourceItem objects
            state.unused_resources = [
                ResourceItem(**item) for item in data.get('unused_resources', [])
            ]
            state.used_resources = [
                ResourceItem(**item) for item in data.get('used_resources', [])
            ]
            state.last_updated = data.get('last_updated', datetime.now().isoformat())

            return state
        except Exception as e:
            # Return empty state if file is corrupted
            return ApplicationState()

    def import_resources(self, df: pd.DataFrame, state: ApplicationState):
        """Import DataFrame as unused resources.

        Args:
            df: DataFrame to import
            state: Application state to update
        """
        # Convert DataFrame rows to ResourceItem objects
        for _, row in df.iterrows():
            # Sanitize all values to be JSON-serializable
            sanitized_data = {
                key: self._sanitize_value(value)
                for key, value in row.to_dict().items()
            }
            resource = ResourceItem(
                data=sanitized_data,
                status="unused"
            )
            state.unused_resources.append(resource)

    def move_to_used(self, resource_ids: List[str], state: ApplicationState):
        """Move resources from unused to used.

        Args:
            resource_ids: List of resource IDs to move
            state: Application state to update
        """
        # Find and move resources
        resources_to_move = []
        remaining_unused = []

        for resource in state.unused_resources:
            if resource.resource_id in resource_ids:
                resource.status = "used"
                resources_to_move.append(resource)
            else:
                remaining_unused.append(resource)

        # Update state
        state.unused_resources = remaining_unused
        state.used_resources.extend(resources_to_move)

    def search_resources(self, query: str, resources: List[ResourceItem]) -> List[ResourceItem]:
        """Full-text search across all columns.

        Args:
            query: Search query string
            resources: List of resources to search

        Returns:
            Filtered list of resources matching query
        """
        if not query:
            return resources

        query_lower = query.lower()
        results = []

        for resource in resources:
            # Search all values in the data dictionary
            for value in resource.data.values():
                if query_lower in str(value).lower():
                    results.append(resource)
                    break  # Don't add same resource twice

        return results
