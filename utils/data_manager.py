"""Data models and persistence management for ResourceTracker."""

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

# Define all available locations
LOCATIONS = [
    "warehouse",
    "card_room",
    "gaming_pit",
    "gaming_table",
    "destruction_room",
    "surveillance"
]

LOCATION_DISPLAY_NAMES = {
    "warehouse": "📦 Warehouse",
    "card_room": "🃏 Card Room",
    "gaming_pit": "🎰 Gaming Pit",
    "gaming_table": "🎲 Gaming Table",
    "destruction_room": "🔥 Destruction Room",
    "surveillance": "📹 Surveillance"
}


@dataclass
class ResourceItem:
    """Represents a single resource row with metadata."""
    data: Dict[str, Any]  # Original row data from CSV/Excel
    location: str = "warehouse"  # Current location of the resource
    status: str = "unused"  # Status: "unused" or "used"
    import_date: str = field(default_factory=lambda: datetime.now().isoformat())
    resource_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tag: str = "unknown"  # Tag for categorizing resources by import batch

    def to_dict(self) -> dict:
        """Convert ResourceItem to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ApplicationState:
    """Main application state for persistence."""
    resources: Dict[str, List[ResourceItem]] = field(default_factory=dict)  # location -> resources
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Initialize all locations with empty lists."""
        if not self.resources:
            self.resources = {loc: [] for loc in LOCATIONS}

    def to_dict(self) -> dict:
        """Convert ApplicationState to dictionary for JSON serialization."""
        return {
            'resources': {
                loc: [r.to_dict() for r in resources]
                for loc, resources in self.resources.items()
            },
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

            # Check if using new format (resources dict) or old format (unused/used)
            if 'resources' in data:
                # New format
                for loc, items in data['resources'].items():
                    if loc in LOCATIONS:
                        # Handle missing status field for backward compatibility
                        resources = []
                        for item in items:
                            if 'status' not in item:
                                item['status'] = 'unused'  # Default status for old data
                            resources.append(ResourceItem(**item))
                        state.resources[loc] = resources
            else:
                # Old format - migrate unused_resources to warehouse, used_resources to surveillance
                unused = [ResourceItem(**item) for item in data.get('unused_resources', [])]
                used = [ResourceItem(**item) for item in data.get('used_resources', [])]

                # Migrate old data to new locations
                for resource in unused:
                    resource.location = "warehouse"
                    resource.status = "unused"  # Set status for migrated resources
                    state.resources["warehouse"].append(resource)

                for resource in used:
                    resource.location = "surveillance"
                    resource.status = "used"  # Set status for migrated resources
                    state.resources["surveillance"].append(resource)

            state.last_updated = data.get('last_updated', datetime.now().isoformat())

            return state
        except Exception as e:
            # Return empty state if file is corrupted
            return ApplicationState()

    def import_resources(self, df: pd.DataFrame, state: ApplicationState, tag: str = "unknown"):
        """Import DataFrame as resources in warehouse.

        Args:
            df: DataFrame to import
            state: Application state to update
            tag: Tag to apply to all imported resources (default: "unknown")
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
                location="warehouse",  # Store in warehouse by default
                status="unused",  # Default status for new imports
                tag=tag
            )
            state.resources["warehouse"].append(resource)

    def move_resources(self, resource_ids: List[str], state: ApplicationState, target_location: str):
        """Move resources from current location to target location.

        Args:
            resource_ids: List of resource IDs to move
            state: Application state to update
            target_location: Target location to move resources to
        """
        if target_location not in LOCATIONS:
            raise ValueError(f"Invalid target location: {target_location}")

        # Find and move resources from all locations
        for current_location in LOCATIONS:
            resources_to_move = []
            remaining_resources = []

            for resource in state.resources[current_location]:
                if resource.resource_id in resource_ids:
                    resource.location = target_location
                    resources_to_move.append(resource)
                else:
                    remaining_resources.append(resource)

            # Update current location
            state.resources[current_location] = remaining_resources

            # Add to target location
            if resources_to_move:
                state.resources[target_location].extend(resources_to_move)

    def mark_as_used(self, resource_ids: List[str], state: ApplicationState):
        """Mark resources as used (keeps them in current location).

        Args:
            resource_ids: List of resource IDs to mark as used
            state: Application state to update
        """
        # Find and update status in all locations
        for location in LOCATIONS:
            for resource in state.resources[location]:
                if resource.resource_id in resource_ids:
                    resource.status = "used"

    def mark_as_unused(self, resource_ids: List[str], state: ApplicationState):
        """Mark resources as unused (keeps them in current location).

        Args:
            resource_ids: List of resource IDs to mark as unused
            state: Application state to update
        """
        # Find and update status in all locations
        for location in LOCATIONS:
            for resource in state.resources[location]:
                if resource.resource_id in resource_ids:
                    resource.status = "unused"

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

    @staticmethod
    def get_all_tags(resources: List[ResourceItem]) -> List[str]:
        """Get all unique tags from a list of resources.

        Args:
            resources: List of resources to extract tags from

        Returns:
            Sorted list of unique tags
        """
        tags = set(resource.tag for resource in resources)
        return sorted(list(tags))

    @staticmethod
    def filter_by_tag(tag: str, resources: List[ResourceItem]) -> List[ResourceItem]:
        """Filter resources by tag.

        Args:
            tag: Tag to filter by (use "all" for no filtering)
            resources: List of resources to filter

        Returns:
            Filtered list of resources
        """
        if not tag or tag.lower() == "all":
            return resources

        return [r for r in resources if r.tag == tag]

    @staticmethod
    def filter_by_status(status: str, resources: List[ResourceItem]) -> List[ResourceItem]:
        """Filter resources by status.

        Args:
            status: Status to filter by ("unused", "used", or "all" for no filtering)
            resources: List of resources to filter

        Returns:
            Filtered list of resources
        """
        if not status or status.lower() == "all":
            return resources

        return [r for r in resources if r.status == status.lower()]

    @staticmethod
    def get_total_count(state: ApplicationState) -> int:
        """Get total count of all resources across all locations.

        Args:
            state: Application state

        Returns:
            Total count of resources
        """
        return sum(len(resources) for resources in state.resources.values())

    @staticmethod
    def get_location_counts(state: ApplicationState) -> Dict[str, int]:
        """Get count of resources for each location.

        Args:
            state: Application state

        Returns:
            Dictionary mapping location to count
        """
        return {loc: len(resources) for loc, resources in state.resources.items()}
