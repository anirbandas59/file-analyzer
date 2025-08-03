#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Pytest plugins
pytest_plugins = ["pytestqt"]


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for pytest-qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setStyle("Fusion")  # Consistent styling across platforms
    yield app
    # App cleanup handled automatically


@pytest.fixture(autouse=True)
def setup_headless_environment():
    """Set up headless environment for all tests."""
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    yield


def pytest_configure(config):
    """Configure pytest for all tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "visual: mark test as visual regression test"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as GUI test"
    )
    config.addinivalue_line(
        "markers", "headless: mark test as headless test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Auto-mark tests based on directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "visual" in str(item.fspath):
            item.add_marker(pytest.mark.visual)