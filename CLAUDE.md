# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application opens at `http://localhost:8501`

## Project Overview

ResourceTracker is a personal tool for tracking company resources across 6 physical locations. Users import CSV/Excel files, tag resources by import batch, and move resources through locations as they progress through a workflow.

Additionally, it provides a **Processed Resources** page for viewing and tracking processed PDF files with used/unused status management.

## Architecture

### 6-Location System

Resources are tracked through these locations:
1. **warehouse** (📦) - Default location for all imports
2. **card_room** (🃏) - Card room processing
3. **gaming_pit** (🎰) - Gaming pit area
4. **gaming_table** (🎲) - Gaming tables
5. **destruction_room** (🔥) - Marked for destruction
6. **surveillance** (📹) - Under monitoring

All imports go to **warehouse** by default. Resources can be moved between any locations.

### Data Model

**Core Data Classes** (`utils/data_manager.py`):
```python
@dataclass
class ResourceItem:
    data: Dict[str, Any]      # Original CSV/Excel row data
    location: str             # Current location (one of 6)
    import_date: str          # ISO timestamp
    resource_id: str          # Unique UUID
    tag: str                  # Import batch tag (default: filename)

@dataclass
class ApplicationState:
    resources: Dict[str, List[ResourceItem]]  # location -> list
    last_updated: str
```

**Key Constants**:
- `LOCATIONS` - List of all 6 location keys
- `LOCATION_DISPLAY_NAMES` - Maps location key to display name with emoji

### Data Persistence

- **Resource Storage**: `data/resources.json` (auto-created)
- **Processed Status**: `data/processed_status.json` - Tracks used/unused status for PDF files
- **Auto-save**: After every import, move, or status change operation
- **Backward compatible**: Old "unused/used" format auto-migrates (unused→warehouse, used→surveillance)
- **Type sanitization**: Pandas/NumPy types converted to JSON-compatible types (NaN→None, timestamps→ISO strings)

### Page Organization

**Import Page** (`app.py`):
- File upload with tag input (tag defaults to filename if empty)
- Data preview (first 10 rows)
- Import to warehouse

**Location Pages** (`pages/*.py`):
- Each location page uses `render_location_page()` from `utils/location_page.py`
- All location pages are ~14 lines of code (just call the template)
- Template provides: tag filter, search, select all/clear, resource table, move functionality

**Processed Resources Page** (`pages/8_📄_Processed_Resource.py`):
- Displays PDF files from `processed/` folder
- Search/filter by file name (case-insensitive)
- Used/Unused status tracking with persistent storage
- View filter: Unused Only (default), Used Only, or All Resources
- Click to view PDF in embedded viewer
- Mark as Used/Unused button to toggle status
- Download button for each PDF
- Status persisted in `data/processed_status.json`

**Template Pattern** (`utils/location_page.py`):
The `render_location_page(location_key, location_display)` function:
1. Displays resources for the given location
2. Provides tag filtering and full-text search
3. Shows Select All/Clear buttons
4. Displays editable table with checkboxes
5. Shows move controls when rows are selected
6. Handles move operation with auto-save

### Key Implementation Details

**Widget Keys**: All Streamlit widgets use unique keys with `location_key` to avoid conflicts:
```python
key=f"select_all_{location_key}"
key=f"move_to_{location_key}"
```

**Select All Logic**:
- Uses `st.session_state.select_all` to track state
- When checked: sets all filtered rows to selected
- When unchecked: clears all selections
- Calls `st.rerun()` after state change to update data_editor

**Resource Movement** (`DataManager.move_resources()`):
- Takes list of resource IDs and target location
- Searches ALL locations for the resources
- Updates resource location field
- Removes from source location, adds to target location
- Atomic operation (single save_state call)

**Tag System**:
- Default: Filename without extension
- Filter by tag on any location page
- Tags are preserved when resources move between locations

**Processed Resources Status Tracking**:
- Uses `data/processed_status.json` to persist used/unused status
- `st.session_state.processed_selected_pdf` tracks currently selected PDF
- Status toggled via "Mark as Used/Unused" button
- JSON format: `{"filename.pdf": true/false}`
- Auto-creates `data/` directory if it doesn't exist

### Important Files

**Core Business Logic**:
- `utils/data_manager.py` - DataManager class with all CRUD operations
  - `import_resources(df, state, tag)` - Import DataFrame to warehouse
  - `move_resources(ids, state, target_location)` - Move between locations
  - `search_resources(query, resources)` - Full-text search
  - `get_all_tags(resources)` - Extract unique tags
  - `filter_by_tag(tag, resources)` - Filter by tag
  - `get_total_count(state)` / `get_location_counts(state)` - Statistics

**Session Management**:
- `utils/session_manager.py` - Singleton pattern for Streamlit session state
  - `SessionManager.initialize()` - Called on every page load
  - `SessionManager.get_state()` - Get ApplicationState
  - `SessionManager.get_data_manager()` - Get DataManager instance

**UI Templates**:
- `utils/location_page.py` - `render_location_page()` function used by all location pages

**File Parsing**:
- `utils/file_parser.py` - `FileParser.parse_file()` handles CSV (UTF-8/GBK/Latin1) and Excel (XLS/XLSX)

### Data Migration Note

Old data format (`unused_resources`/`used_resources`) automatically migrates on first load:
- Old `unused_resources` → `warehouse` location
- Old `used_resources` → `surveillance` location
- Migration happens once, then saves in new format

### Directory Structure

```
ResourceTracker/
├── app.py                          # Main entry point (Import page)
├── requirements.txt                  # Python dependencies
├── CLAUDE.md                       # Project documentation for Claude Code
├── README.md                        # User documentation
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── pages/
│   ├── 2_📦_Warehouse.py          # Warehouse location page
│   ├── 3_🃏_Card_Room.py          # Card room location page
│   ├── 4_🎰_Gaming_Pit.py         # Gaming pit location page
│   ├── 5_🎲_Gaming_Table.py       # Gaming table location page
│   ├── 6_🔥_Destruction_Room.py   # Destruction room location page
│   ├── 7_📹_Surveillance.py       # Surveillance location page
│   └── 8_📄_Processed_Resource.py # Processed resources page
├── utils/
│   ├── __init__.py
│   ├── data_manager.py              # Data operations and persistence
│   ├── file_parser.py               # CSV/Excel parsing
│   └── session_manager.py           # Session state management
├── data/
│   ├── resources.json               # Auto-saved resource persistence
│   └── processed_status.json        # Processed PDF used/unused status
└── processed/                     # Folder for processed PDF files
    └── *.pdf                      # PDF files to view and track
```
