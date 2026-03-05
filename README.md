# ResourceTracker

A personal tool for tracking and managing company application testing resources. Built with Python and Streamlit for rapid development and ease of use.

## Features

- **Import Files**: Upload CSV or Excel files (.csv, .xls, .xlsx)
- **Categorize Resources**: Mark resources as used or unused
- **Full-Text Search**: Search across all columns in your data
- **Auto-Save**: All changes automatically persist to local JSON file
- **Simple UI**: Clean interface with good UX for quick resource management

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd D:\Benjamin\ResourceTracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**:
   The application will automatically open at `http://localhost:8501`

## Usage

### 1. Import Resources (📥 Resource Import)

1. Navigate to the home page
2. Click "Browse files" to upload a CSV or Excel file
3. Preview the first 10 rows of your data
4. Click "Import" to add all resources as "unused"

### 2. Manage Unused Resources (📦 Unused Resources)

1. Navigate to "Unused Resources" in the sidebar
2. Use the search bar to filter resources
3. Select rows by checking the boxes
4. Click "Move to Used" to categorize selected resources

### 3. View Used Resources (✅ Used Resources)

1. Navigate to "Used Resources" in the sidebar
2. Use the search bar to filter resources
3. View all categorized resources (read-only)

## File Requirements

- **CSV Files**: Supports UTF-8, GBK, and Latin1 encodings
- **Excel Files**: Supports both .xls and .xlsx formats
- **No Column Requirements**: All columns are imported as-is
- **Automatic Encoding Detection**: Tries multiple encodings for CSV files

## Data Persistence

All data is automatically saved to `data/resources.json`:
- Changes are saved immediately after import or move operations
- Data persists across application restarts
- JSON format for easy inspection and backup
- Auto-creates the `data/` directory if it doesn't exist

## Project Structure

```
ResourceTracker/
├── app.py                          # Main entry point (Import page)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── pages/
│   ├── 2_📦_Unused_Resources.py   # Unused resources page
│   └── 3_✅_Used_Resources.py      # Used resources page
├── utils/
│   ├── __init__.py
│   ├── data_manager.py            # Data operations and persistence
│   ├── file_parser.py             # CSV/Excel parsing
│   └── session_manager.py         # Session state management
└── data/
    └── resources.json             # Auto-saved persistence file
```

## Technology Stack

- **Streamlit 1.40+**: Web framework for rapid UI development
- **Pandas 2.2+**: Data manipulation and analysis
- **OpenPyXL 3.1+**: Excel XLSX file support
- **XLRD 2.0+**: Excel XLS file support

## Tips

- Use the search bar to quickly find resources across all columns
- Select multiple rows at once to move them in bulk
- Your data is automatically saved - no manual save needed
- The application works offline once dependencies are installed
- Close the browser window to exit the application

## Troubleshooting

**File upload fails**:
- Check that the file format is CSV, XLS, or XLSX
- For CSV files, try saving with UTF-8 encoding
- Ensure the file is not corrupted

**Data not persisting**:
- Check that you have write permissions in the project directory
- Verify the `data/resources.json` file exists and is accessible

**Application won't start**:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Python 3.8+ is installed

## License

Apache License 2.0

## Author

Created for personal use in testing company applications.
