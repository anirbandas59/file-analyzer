# File System Analyzer

A desktop application for smart file management, disk analysis, and cleanup. Visualize, analyze, and organize your files with ease.

## Features

- **Large File Analyzer**: Identify and manage large files taking up disk space.
- **File Age Analyzer**: Find old or rarely accessed files for potential cleanup.
- **Duplicate Finder**: Detect and remove duplicate files to free up storage.
- Tree-based directory navigation
- Sortable file listing with details (name, size, date, type)
- Search and filter capabilities
- Visual representation of file sizes
- Responsive UI with resizable panels

## Prerequisites

- Python 3.10+
- Windows 10/11 recommended

## How to Run

### Quick Start (Recommended)

1. [Install Python 3.10+](https://www.python.org/downloads/windows/) (ensure "Add Python to PATH" is checked)
2. Download or clone this repository
3. Double-click `run.bat` to launch the app

### Manual Start

1. Create a virtual environment (optional but recommended):
   ```bat
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bat
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bat
   python -m src.main
   ```

## Export, Cleanup, and Archival Recommendations

- Export file lists and analysis results for reporting or further action
- Get recommendations for archiving or deleting old/large/duplicate files
- One-click cleanup actions (admin rights may be required for some operations)

## Screenshots

<!-- Add screenshots here -->

## Project Structure

```
FileAnalyzer/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── directory_tree.py
│   │   └── file_table.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── file_system_model.py
│   └── utils/
│       ├── __init__.py
│       └── file_utils.py
├── resources/
│   └── icons/
└── tests/
    ├── __init__.py
    └── test_file_utils.py
```

## Usage

1. Launch the application
2. Navigate through the directory tree in the left panel
3. Click on a directory to view its contents in the file table
4. Use the search box to filter files by name or type
5. Click on column headers to sort the file list
6. Use the "Scan" button to perform a deep scan of the selected directory

## Future Features

- Charts and graphical representations
- File type analysis
- Historical scanning and comparison
