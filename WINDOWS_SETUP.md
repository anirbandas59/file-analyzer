# Windows Setup Guide - FileAnalyzer

This guide provides detailed setup instructions specifically for Windows users, including system configuration and troubleshooting steps.

## 📋 Prerequisites

### System Requirements
- **Windows 10** (version 1903 or later) or **Windows 11**
- **4GB RAM** minimum (8GB recommended for large file analysis)
- **100MB** free disk space for application and dependencies
- **Administrator privileges** (for certain file operations)

### Python Installation
- **Python 3.12+** is required (tested with 3.12.11)
- Download from the official source: [python.org/downloads/windows](https://www.python.org/downloads/windows/)
- **PyQt6** and optional dependencies will be installed automatically

## 🚀 Quick Setup (Recommended)

### Step 1: Download FileAnalyzer
1. **Download** or **clone** this repository to your desired location
2. **Extract** the files if downloaded as ZIP
3. **Navigate** to the FileAnalyzer folder

### Step 2: Run the Application
1. **Double-click** `run.bat` in the project folder
2. **Wait** for the automatic setup process:
   - Python version verification
   - Virtual environment creation
   - Dependency installation
   - Application launch

> **Note**: The first run may take 2-3 minutes for setup. Subsequent runs will be much faster.

## 🔧 Manual Setup (Advanced Users)

### Step 1: Install Python
1. Download Python 3.12+ from [python.org](https://www.python.org/downloads/windows/)
2. **Important**: Check **"Add Python to PATH"** during installation
3. Select **"Install for all users"** if you have administrator rights
4. After installation, verify by opening Command Prompt and running:
   ```cmd
   python --version
   ```
   Should show Python 3.12.x or later

### Step 2: Setup FileAnalyzer
1. Open **Command Prompt** or **PowerShell**
2. Navigate to the FileAnalyzer directory:
   ```cmd
   cd C:\path\to\FileAnalyzer
   ```
3. Create a virtual environment:
   ```cmd
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
5. Install dependencies:
   ```cmd
   # Basic installation
   pip install -r requirements.txt
   
   # Or install with optional features (recommended)
   pip install -e ".[charts,svg,dev]"
   ```
6. Run the application:
   ```cmd
   python -m src.main
   ```

## ⚙️ System Configuration

### Enable Long Path Support (Recommended)

FileAnalyzer can analyze files with very long paths. To ensure compatibility:

#### Method 1: Registry Editor (Advanced)
1. Press **Win + R**, type `regedit`, press Enter
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Find or create `LongPathsEnabled` (DWORD)
4. Set value to `1`
5. **Restart** your computer

#### Method 2: Group Policy (Windows Pro/Enterprise)
1. Press **Win + R**, type `gpedit.msc`, press Enter
2. Navigate to: **Computer Configuration** → **Administrative Templates** → **System** → **Filesystem**
3. Find **"Enable Win32 long paths"**
4. Set to **Enabled**
5. **Restart** your computer

#### Method 3: PowerShell (Windows 10 1607+)
Run PowerShell as Administrator:
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Windows Defender Configuration

If Windows Defender is blocking the application:

1. Open **Windows Security** (Windows Defender)
2. Go to **Virus & threat protection**
3. Click **Manage settings** under "Virus & threat protection settings"
4. Add FileAnalyzer folder to **Exclusions**:
   - Click **Add or remove exclusions**
   - Click **Add an exclusion** → **Folder**
   - Select your FileAnalyzer directory

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### Issue: "Python is not recognized as an internal or external command"
**Solution:**
1. Reinstall Python 3.12+ with **"Add Python to PATH"** checked
2. Or manually add Python to PATH:
   - Right-click **This PC** → **Properties**
   - Click **Advanced system settings**
   - Click **Environment Variables**
   - Under **System variables**, find and select **Path**, click **Edit**
   - Click **New** and add: `C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\`
   - Also add: `C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\Scripts\`

#### Issue: "Access is denied" when running application
**Solutions:**
1. **Run as Administrator**: Right-click `run.bat` → **Run as administrator**
2. **Change folder permissions**:
   - Right-click FileAnalyzer folder → **Properties**
   - Go to **Security** tab → **Edit**
   - Select your user account → Check **Full control**

#### Issue: Application crashes on startup
**Solutions:**
1. **Update graphics drivers**
2. **Install Visual C++ Redistributables**:
   - Download from [Microsoft's website](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
3. **Run in compatibility mode**:
   - Right-click `run.bat` → **Properties**
   - Go to **Compatibility** tab
   - Check **Run this program in compatibility mode** → Select **Windows 8**

#### Issue: Slow performance during file scanning
**Solutions:**
1. **Exclude antivirus scanning**: Add FileAnalyzer to antivirus exclusions
2. **Close other applications** during analysis
3. **Increase virtual memory**:
   - **This PC** → **Properties** → **Advanced system settings**
   - **Performance** → **Settings** → **Advanced** → **Virtual memory**
   - **Change** → Uncheck **Automatically manage** → **Custom size**
   - Set **Initial size** and **Maximum size** to 2x your RAM (in MB)

#### Issue: "Module not found" errors
**Solutions:**
1. **Reinstall dependencies**:
   ```cmd
   venv\Scripts\activate
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   
   # Or install with optional features
   pip install -e ".[charts,svg,dev]"
   ```
2. **Clear pip cache**:
   ```cmd
   pip cache purge
   ```
3. **PyQt6 specific issues**:
   ```cmd
   pip install --upgrade PyQt6 PyQt6-Qt6
   ```

### Performance Optimization

#### For Large File Sets (>100,000 files)
1. **Increase available RAM**: Close other applications
2. **Use SSD storage**: Move FileAnalyzer to SSD if possible
3. **Exclude system directories**: Avoid scanning Windows, Program Files
4. **Analyze in batches**: Scan subdirectories separately

#### For Network Drives
1. **Copy files locally** for faster analysis
2. **Use smaller batch sizes**
3. **Ensure stable network connection**

## 🔒 Security Considerations

### Administrator Rights
FileAnalyzer may request administrator rights for:
- **Accessing protected system files**
- **Deleting certain files**
- **Modifying file permissions**

### File Safety
- All file operations include **confirmation dialogs**
- **No automatic deletions** without user consent
- **Backup recommendations** before major cleanup operations

### Data Privacy
- **No data collection**: FileAnalyzer doesn't send data externally
- **Local processing only**: All analysis happens on your computer
- **No network requirements**: Works completely offline

## 📞 Getting Help

### If you encounter issues:

1. **Check this guide** for common solutions
2. **Run Windows Update** to ensure system compatibility
3. **Update graphics and system drivers** (important for PyQt6)
4. **Try running as Administrator**
5. **Check test reports** in `documents/reports/` for known issues
6. **Run diagnostic tests**:
   ```cmd
   # Test PyQt6 installation
   python -c "import PyQt6.QtWidgets; print('PyQt6 OK')"
   
   # Test optional dependencies
   python -c "import matplotlib; print('Matplotlib OK')"
   python -c "import numpy; print('Numpy OK')"
   ```

### System Information for Bug Reports

If reporting issues, include:
- **Windows version**: Run `winver` in Command Prompt
- **Python version**: Run `python --version` (should be 3.12+)
- **PyQt6 version**: Run `python -c "import PyQt6.QtCore; print(PyQt6.QtCore.PYQT_VERSION_STR)"`
- **Error messages**: Copy exact error text
- **System specs**: RAM, storage type (HDD/SSD)
- **Test results**: Check `documents/reports/` for test failures

## 🚀 Advanced Usage

### Command Line Options
Run from Command Prompt for advanced options:
```cmd
# Run with verbose logging
python -m src.main --verbose

# Specify initial directory
python -m src.main --directory "C:\Users\Username\Documents"

# Run in debug mode
python -m src.main --debug

# Run tests (if dev dependencies installed)
pytest tests/ --tb=short

# Run visual regression tests
pytest tests/visual/ -m visual
```

### Custom Configuration
Create `config.ini` in the FileAnalyzer directory:
```ini
[Analysis]
default_large_file_threshold=100
default_age_threshold_days=365
max_concurrent_workers=4

[UI]
theme=dark
auto_save_results=true
confirm_deletions=true
enable_visual_regression_tests=false

[Development]
run_tests_on_startup=false
generate_test_reports=true
enable_coverage_reporting=false
```

---

**Need more help?** Check our [main README](README.md) or submit an issue on GitHub!
