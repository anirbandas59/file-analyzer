# File System Analyzer

A desktop application for visualizing and analyzing file system data, allowing users to easily understand disk usage and manage files more efficiently.

## Features

- Tree-based directory navigation
- Sortable file listing with details (name, size, date, type)
- Search and filter capabilities
- Visual representation of file sizes
- Responsive UI with resizable panels

## Requirements

- Python 3.8+
- PyQt6

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install PyQt6
```

## Running the Application

From the project root directory, run:

```bash
python -m src.main
```

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

## Future Features (Phase 2)

- Charts and graphical representations
- Duplicate file detection
- File type analysis
- Historical scanning and comparison
