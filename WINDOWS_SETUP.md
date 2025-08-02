# Setting Up File System Analyzer on Windows

This guide will help you install and run the File System Analyzer on a Windows machine.

## Prerequisites

1. **Python 3.8 or later**
   - Download the latest Python from [python.org](https://www.python.org/downloads/windows/)
   - During installation, check "Add Python to PATH"

## Installation

### Option 1: Direct Installation

1. Clone or download this repository
2. Open Command Prompt and navigate to the project directory
3. Install the required dependencies:

```
pip install PyQt6
```

4. Run the application by double-clicking `run.bat` or executing:

```
python -m src.main
```

### Option 2: Create a Virtual Environment (Recommended)

1. Clone or download this repository
2. Open Command Prompt and navigate to the project directory
3. Create a virtual environment:

```
python -m venv venv
```

4. Activate the virtual environment:

```
venv\Scripts\activate
```

5. Install the required dependencies:

```
pip install PyQt6
```

6. Run the application:

```
python -m src.main
```

## Troubleshooting

### PyQt6 Not Found

If you get an error about PyQt6 not being found, make sure you have installed it correctly:

```
pip install PyQt6
```

### Python Command Not Found

If the `python` command is not recognized, try using `py` instead:

```
py -m pip install PyQt6
py -m src.main
```

### Application Crashes on Start

- Make sure you have Python 3.8+
- Check that PyQt6 is properly installed
- Try running with verbose output:

```
python -m src.main --verbose
```

## Getting Help

If you encounter issues, please open an issue on the GitHub repository with:

- Your Windows version
- Your Python version (`python --version`)
- Full error message
