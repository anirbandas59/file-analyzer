# FileAnalyzer - Smart File Management

![FileAnalyzer](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive desktop application for smart file management, storage optimization, and automated cleanup recommendations. FileAnalyzer helps you reclaim disk space, organize files efficiently, and maintain a clean file system.

## ✨ Features

### 🔍 **Smart File Management Tools**

- **📊 Duplicate File Detection**
  - Content-based duplicate detection using SHA-256 hashing
  - Heuristic detection for fast preliminary analysis
  - Safe removal with confirmation dialogs
  - Batch operations with space savings calculation

- **📈 Large File Analysis** 
  - Configurable size thresholds (default: 100MB+)
  - Size categorization and cleanup recommendations
  - File type analysis and directory breakdown
  - Individual file actions (open location, delete)

- **📅 File Age Analysis & Archival**
  - Age-based file categorization (Recent, Active, Stale, Archive, Old)
  - Visual age distribution with color-coded categories
  - Priority archival recommendations
  - Bulk selection for archival candidates

### 🎨 **Modern User Interface**

- **Comprehensive Design System**: Material Design 3 inspired theme architecture
- **Runtime Theme Switching**: Seamless light/dark mode with instant updates
- **Cross-Platform Icons**: SVG-based icon system with fallbacks
- **Responsive Components**: Consistent spacing, typography, and styling
- **Background Processing**: Progress indicators and non-blocking operations
- **Interactive Charts**: Matplotlib integration with theme-aware styling

### 📊 **Advanced Visualization**

- **File System Tree View**: Real-time statistics with theming support
- **Interactive Charts**: Theme-aware matplotlib charts (pie, bar, treemap)
- **Size and Age Analysis**: Visual breakdowns with category filtering
- **Export Capabilities**: CSV, JSON formats with comprehensive data
- **Visual Regression Testing**: 61+ UI screenshots for quality assurance

## 🚀 Quick Start

### For Windows Users (Recommended)

1. **Download or clone** this repository
2. **Double-click** `run.bat` in the project folder
3. **Wait** for automatic setup (Python check, virtual environment, dependencies)
4. **Start analyzing** your files!

The `run.bat` script will automatically:
- Check for Python 3.10+ installation
- Create a virtual environment
- Install all required dependencies
- Launch the FileAnalyzer application

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/fileanalyzer/FileAnalyzer.git
cd FileAnalyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies (basic)
pip install -r requirements.txt

# Install with optional features (recommended)
pip install -e ".[charts,svg,dev]"

# Run the application
python -m src.main
```

## 📋 Prerequisites

- **Python 3.12+** - Download from [python.org](https://python.org/downloads/)
- **Windows 10/11** (primary support), macOS 10.14+, or Linux (WSL2 tested)
- **~100MB** disk space for installation and dependencies
- **Administrator rights** (for certain file operations)
- **Optional**: matplotlib and numpy for advanced charting (auto-installed)
- **Optional**: PyQt6-SVG for enhanced icon support (auto-installed)

## 🎯 How to Use

### 1. **File Scanning**
- Launch the application and navigate to the **Files** tab
- Click **"Browse"** to select a directory to analyze
- Wait for the scan to complete (progress bar will show status)

### 2. **Duplicate Detection**
- Go to **Management** tab → **Duplicate Finder**
- Click **"Start Analysis"** to find duplicate files
- Review detected duplicates with confidence levels
- Select files to remove and confirm deletion

### 3. **Large File Analysis**
- Go to **Management** tab → **Large File Analyzer** 
- Configure size threshold (default: 100MB)
- Start analysis to identify largest files
- Review cleanup recommendations and take action

### 4. **Age-Based Archival**
- Go to **Management** tab → **File Age Analyzer**
- Analyze files by modification date
- View age distribution and archival candidates
- Export lists for batch archival operations

### 5. **Export & Reports**
- Export analysis results in CSV or JSON format
- Generate cleanup reports for documentation
- Save recommendations for future reference

## 🛠️ Advanced Configuration

### Custom Thresholds
- **Large File Threshold**: Adjust from 1MB to 10GB
- **Age Categories**: Customize time periods for archival
- **Duplicate Confidence**: Configure heuristic vs content-based detection

### File Operations
- **Safe Mode**: Confirmation dialogs for all destructive operations
- **Batch Operations**: Select multiple files for bulk actions
- **Undo Support**: Recycle bin integration where available

## 📊 Analysis Capabilities

### File Statistics
- Total files and directories scanned
- Size distribution across categories
- Age distribution analysis
- File type breakdown

### Cleanup Recommendations
- **High Priority**: Large old files (>100MB, >1 year)
- **Medium Priority**: Duplicate files and stale data
- **Low Priority**: Small old files and temporary files

### Export Formats
- **CSV**: Tabular data for spreadsheet analysis
- **JSON**: Structured data for programmatic processing
- **Reports**: Human-readable cleanup summaries

## 🔧 Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.12+ is installed and in PATH
- Ensure PyQt6 dependencies are properly installed
- Run `run.bat` as Administrator if needed
- Check antivirus software isn't blocking execution

**Slow scanning:**
- Large directories (>100k files) may take time
- Network drives are slower than local storage
- Consider excluding system directories

**Permission errors:**
- Run as Administrator for system file access
- Some protected files cannot be analyzed
- Enable long path support on Windows (see WINDOWS_SETUP.md)

**Memory usage:**
- Large file sets may use significant RAM
- Consider analyzing subdirectories separately
- Close other applications during analysis

## 🤝 Contributing

We welcome contributions! Our project includes comprehensive testing infrastructure:

### Development Setup
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run linting
ruff check src/ tests/
ruff format src/ tests/

# Run test suite
pytest tests/ --cov=src

# Run visual regression tests
pytest tests/visual/ -m visual
```

### Code Quality Standards
- **56 tests** covering core functionality (94.6% pass rate)
- **Comprehensive linting** with ruff (481 issues resolved)
- **Type hints** throughout codebase
- **Visual regression testing** with 61+ reference screenshots
- **9% code coverage** with 100% on design system

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **UI Framework**: [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for cross-platform GUI
- **Charting**: [Matplotlib](https://matplotlib.org/) for data visualization
- **Testing**: [pytest](https://pytest.org/) with [pytest-qt](https://pytest-qt.readthedocs.io/)
- **Code Quality**: [ruff](https://docs.astral.sh/ruff/) for linting and formatting
- **Design Inspiration**: Material Design 3 principles
- **Community**: Open-source contributors and feedback

## 📞 Support

- **Documentation**: Check project documentation and test reports
- **Issues**: Report bugs with system information
- **Windows Setup**: See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed instructions
- **Test Reports**: Check `documents/reports/` for comprehensive test coverage
- **Visual Tests**: Reference screenshots in `tests/visual/screenshots/`

---

**Made with ❤️ for better file management**
