# Setting Up File System Analyzer on Windows

This guide will help you install and run the File System Analyzer on a Windows machine.

## Prerequisites

1. **Python 3.10 or later**
   - Download the latest Python from [python.org](https://www.python.org/downloads/windows/)
   - During installation, check "Add Python to PATH"

## Optional: Enable Long Path Support

To work with very long file paths, enable long path support:
1. Open Group Policy Editor (`gpedit.msc`)
2. Go to `Local Computer Policy > Computer Configuration > Administrative Templates > System > Filesystem`
3. Enable "Enable Win32 long paths"

## Installation & Running

### Quick Start (Recommended)

1. Clone or download this repository
2. Double-click `run.bat` in the project folder
   - This will check Python, set up a virtual environment, install dependencies, and launch the app

### Manual Setup

1. Open Command Prompt and navigate to the project directory
2. (Optional) Create a virtual environment:
   ```bat
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bat
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bat
   python -m src.main
   ```

## Admin Rights

Some file operations (deleting, moving, or modifying protected files) may require administrator rights. If you encounter permission errors, try running the app as an administrator.

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

- Make sure you have Python 3.10+
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
