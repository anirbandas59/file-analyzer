# File Analyzer Test Suite

This comprehensive test suite covers unit tests, integration tests, and visual regression tests for the File Analyzer application.

## Test Structure

```
tests/
├── README.md                          # This file
├── __init__.py                        # Test package initialization
├── unit/                              # Unit tests for individual components
│   ├── test_file_utils.py            # File utility functions tests
│   ├── test_settings.py              # Settings manager tests
│   ├── test_logger.py                # Logger functionality tests
│   ├── test_theme_manager.py         # Theme management tests
│   └── test_file_system_model.py     # File system model tests
├── integration/                       # Integration tests for component interactions
│   ├── test_gui.py                   # GUI component integration tests
│   ├── test_main_window_integration.py  # Main window integration tests
│   └── test_file_analysis_workflow.py   # End-to-end workflow tests
└── visual/                            # Visual regression tests
    ├── conftest.py                   # Visual test configuration
    ├── test_ui_visual_regression.py  # UI visual regression tests
    └── screenshots/                  # Reference screenshots (generated)
```

## Prerequisites

Ensure you have installed all test dependencies:

```bash
# Install test dependencies using uv
uv sync --group dev

# Or install manually if using pip
pip install pytest pytest-qt pytest-xvfb pytest-cov pytest-mock pytest-asyncio pytest-timeout
```

## Running Tests

### Run All Tests

```bash
# Run complete test suite
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Run Specific Test Categories

#### Unit Tests Only
```bash
pytest tests/unit/ -v
```

#### Integration Tests Only
```bash
pytest tests/integration/ -v
```

#### Visual Tests Only
```bash
pytest tests/visual/ -v
```

### Headless Testing (CI/CD)

For running GUI tests in headless environments:

```bash
# Using pytest-xvfb for headless GUI testing
pytest tests/ --xvfb-width=1920 --xvfb-height=1080

# Or set environment variable
export QT_QPA_PLATFORM=offscreen
pytest tests/
```

### Parallel Testing

Run tests in parallel for faster execution:

```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run tests in parallel
pytest -n auto tests/
```

## Test Configuration

### pytest.ini Configuration

Create a `pytest.ini` file in the project root:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
markers =
    unit: Unit tests
    integration: Integration tests
    visual: Visual regression tests
    slow: Slow running tests
    gui: Tests requiring GUI components
qt_api = pyqt6
```

### Environment Variables

Set these environment variables for consistent testing:

```bash
export QT_QPA_PLATFORM=offscreen  # For headless testing
export PYTEST_CURRENT_TEST=1      # Indicate test environment
```

## Test Categories Explained

### 1. Unit Tests (`tests/unit/`)

Test individual components in isolation:

- **test_file_utils.py**: Tests file scanning, size formatting, type detection
- **test_settings.py**: Tests settings persistence, backup/recovery, singleton pattern
- **test_logger.py**: Tests logging functionality, rotation, error handling
- **test_theme_manager.py**: Tests theme switching, stylesheet generation
- **test_file_system_model.py**: Tests Qt file system model integration

**Run unit tests:**
```bash
pytest tests/unit/ -m unit
```

### 2. Integration Tests (`tests/integration/`)

Test component interactions and workflows:

- **test_gui.py**: Basic GUI component interactions
- **test_main_window_integration.py**: Main window component integration
- **test_file_analysis_workflow.py**: End-to-end file analysis workflows

**Run integration tests:**
```bash
pytest tests/integration/ -m integration
```

### 3. Visual Regression Tests (`tests/visual/`)

Test UI appearance and visual consistency:

- **test_ui_visual_regression.py**: Screenshots and visual comparisons
- Uses pytest-qt for GUI automation
- Generates reference screenshots for comparison
- Tests theme consistency, layout responsiveness

**Run visual tests:**
```bash
pytest tests/visual/ -m visual
```

## Coverage Reports

Generate detailed coverage reports:

```bash
# HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Terminal coverage report
pytest --cov=src --cov-report=term-missing

# XML coverage report (for CI/CD)
pytest --cov=src --cov-report=xml
```

## Debugging Tests

### Running Single Tests

```bash
# Run specific test file
pytest tests/unit/test_settings.py -v

# Run specific test method
pytest tests/unit/test_settings.py::TestSettingsManager::test_theme_persistence -v

# Run with debugging
pytest tests/unit/test_settings.py::TestSettingsManager::test_theme_persistence -v -s --pdb
```

### Visual Test Debugging

```bash
# Run visual tests with GUI visible (not headless)
unset QT_QPA_PLATFORM
pytest tests/visual/test_ui_visual_regression.py::TestUIVisualRegression::test_main_window_light_theme_visual -v -s
```

### Test Output and Logging

```bash
# Show all output (including print statements)
pytest tests/ -s

# Show only failed tests output
pytest tests/ --tb=short

# Verbose output with test names
pytest tests/ -v
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv sync --group dev
    
    - name: Run tests
      run: |
        export QT_QPA_PLATFORM=offscreen
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Performance Testing

### Test Execution Times

Monitor test execution times:

```bash
# Show slowest tests
pytest --durations=10

# Show all test durations
pytest --durations=0
```

### Memory Usage Testing

```bash
# Install memory profiler
pip install pytest-memray

# Run with memory profiling
pytest --memray tests/
```

## Mock and Fixture Guidelines

### Common Fixtures Used

- `qtbot`: pytest-qt fixture for GUI testing
- `temp_dir`: Temporary directory for file operations
- `mock_home`: Mock user home directory
- `qapp`: QApplication instance for GUI tests

### Mock Patterns

```python
# Mock file system operations
@patch('src.utils.file_utils.scan_directory')
def test_scan_function(mock_scan):
    mock_scan.return_value = ([], 0)
    # Test code here

# Mock Qt dialogs
@patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory')
def test_file_dialog(mock_dialog):
    mock_dialog.return_value = "/test/path"
    # Test code here
```

## Troubleshooting

### Common Issues

1. **Qt Application Already Exists**
   ```bash
   # Solution: Use QApplication.instance() in tests
   app = QApplication.instance() or QApplication([])
   ```

2. **X11/Display Issues on Linux**
   ```bash
   # Solution: Use xvfb for headless testing
   export QT_QPA_PLATFORM=offscreen
   # or
   pytest --xvfb-width=1920 --xvfb-height=1080
   ```

3. **File Permission Errors**
   ```bash
   # Solution: Use temporary directories
   import tempfile
   temp_dir = tempfile.mkdtemp()
   ```

4. **Tests Hanging**
   ```bash
   # Solution: Use timeouts
   pytest --timeout=60 tests/
   ```

### Test Data Cleanup

Tests automatically clean up temporary files and reset singletons. If manual cleanup is needed:

```python
def tearDown(self):
    # Reset singletons
    SettingsManager._instance = None
    Logger._instance = None
    
    # Cleanup temporary files
    import shutil
    shutil.rmtree(self.temp_dir, ignore_errors=True)
```

## Contributing to Tests

### Adding New Tests

1. **Unit Tests**: Add to `tests/unit/` for new utility functions or models
2. **Integration Tests**: Add to `tests/integration/` for component interactions
3. **Visual Tests**: Add to `tests/visual/` for UI changes

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names: `test_theme_switching_updates_all_components`

### Test Documentation

Each test should include:
```python
def test_feature_description(self):
    """Test that feature works correctly under specific conditions."""
    # Arrange: Set up test data
    # Act: Perform the action being tested
    # Assert: Verify the expected outcome
```

## Performance Benchmarks

Expected test execution times:
- Unit tests: < 30 seconds total
- Integration tests: < 2 minutes total  
- Visual tests: < 5 minutes total
- Full suite: < 10 minutes total

Run performance tests:
```bash
pytest --benchmark-only tests/
```