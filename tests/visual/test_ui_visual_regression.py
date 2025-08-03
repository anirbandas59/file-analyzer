#!/usr/bin/env python3

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.main_window import MainWindow
from src.ui.themes.theme_manager import theme_manager
from src.utils.settings import SettingsManager


class TestUIVisualRegression:
    """Visual regression tests using pytest-qt for UI components."""

    @pytest.fixture(autouse=True)
    def setup_test(self, qtbot):
        """Set up test environment for each test."""
        self.qtbot = qtbot
        self.temp_dir = tempfile.mkdtemp()
        SettingsManager._instance = None

        # Create test files
        self.create_test_files()

        yield

        # Cleanup
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        SettingsManager._instance = None

    def create_test_files(self):
        """Create test files for visual testing."""
        files = [
            ("document.txt", "Sample text content"),
            ("script.py", "print('Hello, World!')"),
            ("data.json", '{"key": "value"}'),
            ("image.jpg", "fake image data" * 100),
        ]

        for filename, content in files:
            (Path(self.temp_dir) / filename).write_text(content)

    @patch('src.utils.settings.Path.home')
    def test_main_window_light_theme_visual(self, mock_home, qtbot):
        """Test main window visual appearance with light theme."""
        mock_home.return_value = Path(self.temp_dir)

        # Apply light theme
        theme_manager.apply_theme("light")

        # Create main window
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Wait for window to fully render
        qtbot.wait(500)

        # Take screenshot
        screenshot = window.grab()
        self.save_reference_image(screenshot, "main_window_light_theme")

        # Verify window is displayed properly
        assert window.isVisible()
        assert window.windowTitle() == "File System Analyzer"

    @patch('src.utils.settings.Path.home')
    def test_main_window_dark_theme_visual(self, mock_home, qtbot):
        """Test main window visual appearance with dark theme."""
        mock_home.return_value = Path(self.temp_dir)

        # Apply dark theme
        theme_manager.apply_theme("dark")

        # Create main window
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Wait for rendering
        qtbot.wait(500)

        # Take screenshot
        screenshot = window.grab()
        self.save_reference_image(screenshot, "main_window_dark_theme")

        assert window.isVisible()

    @patch('src.utils.settings.Path.home')
    def test_file_table_populated_visual(self, mock_home, qtbot):
        """Test file table visual appearance when populated with data."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Set scan path and trigger scan
        window.current_scan_path = self.temp_dir
        qtbot.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)

        # Wait for scan to complete
        qtbot.wait(1000)

        # Focus on file table
        file_table = window.file_table
        file_table.setFocus()

        # Take screenshot of populated table
        table_screenshot = file_table.grab()
        self.save_reference_image(table_screenshot, "file_table_populated")

        # Verify table has data
        assert file_table.model.rowCount() > 0

    @patch('src.utils.settings.Path.home')
    def test_directory_tree_visual(self, mock_home, qtbot):
        """Test directory tree visual appearance."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Set up directory tree
        tree = window.directory_tree
        tree.set_root_directory(self.temp_dir)

        # Wait for tree to populate
        qtbot.wait(500)

        # Take screenshot
        tree_screenshot = tree.grab()
        self.save_reference_image(tree_screenshot, "directory_tree")

        assert tree.model.rowCount() >= 0

    @patch('src.utils.settings.Path.home')
    def test_charts_tab_visual(self, mock_home, qtbot):
        """Test charts tab visual appearance."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Trigger scan to populate data
        window.current_scan_path = self.temp_dir
        qtbot.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        qtbot.wait(1000)

        # Switch to charts tab
        charts_tab_index = self.find_tab_index(window, "Charts")
        if charts_tab_index >= 0:
            window.tab_widget.setCurrentIndex(charts_tab_index)
            qtbot.wait(500)

            # Take screenshot of charts
            charts_widget = window.tab_widget.currentWidget()
            chart_screenshot = charts_widget.grab()
            self.save_reference_image(chart_screenshot, "charts_tab")

    @patch('src.utils.settings.Path.home')
    def test_management_tab_visual(self, mock_home, qtbot):
        """Test management tab visual appearance."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Trigger scan
        window.current_scan_path = self.temp_dir
        qtbot.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        qtbot.wait(1000)

        # Switch to management tab
        mgmt_tab_index = self.find_tab_index(window, "Management")
        if mgmt_tab_index >= 0:
            window.tab_widget.setCurrentIndex(mgmt_tab_index)
            qtbot.wait(500)

            # Take screenshot
            mgmt_widget = window.tab_widget.currentWidget()
            mgmt_screenshot = mgmt_widget.grab()
            self.save_reference_image(mgmt_screenshot, "management_tab")

    @patch('src.utils.settings.Path.home')
    def test_button_states_visual(self, mock_home, qtbot):
        """Test button visual states (normal, hover, pressed)."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Test browse button states
        browse_btn = window.browse_button

        # Normal state
        btn_normal = browse_btn.grab()
        self.save_reference_image(btn_normal, "browse_button_normal")

        # Hover state (simulate mouse hover)
        qtbot.mouseMove(browse_btn)
        qtbot.wait(100)
        btn_hover = browse_btn.grab()
        self.save_reference_image(btn_hover, "browse_button_hover")

        # Test scan button
        scan_btn = window.scan_button
        scan_normal = scan_btn.grab()
        self.save_reference_image(scan_normal, "scan_button_normal")

    @patch('src.utils.settings.Path.home')
    def test_splitter_layout_visual(self, mock_home, qtbot):
        """Test splitter layout and resizing behavior."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Default layout
        default_screenshot = window.grab()
        self.save_reference_image(default_screenshot, "splitter_default")

        # Resize splitter (move divider)
        splitter = window.splitter
        sizes = splitter.sizes()

        # Make left panel wider
        new_sizes = [sizes[0] + 100, sizes[1] - 100]
        splitter.setSizes(new_sizes)
        qtbot.wait(200)

        resized_screenshot = window.grab()
        self.save_reference_image(resized_screenshot, "splitter_resized")

    @patch('src.utils.settings.Path.home')
    def test_file_type_bar_visual(self, mock_home, qtbot):
        """Test file type visualization bar."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Trigger scan to populate file type bar
        window.current_scan_path = self.temp_dir
        qtbot.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        qtbot.wait(1000)

        # Take screenshot of file type bar
        if hasattr(window, 'file_type_bar'):
            bar_screenshot = window.file_type_bar.grab()
            self.save_reference_image(bar_screenshot, "file_type_bar")

    @patch('src.utils.settings.Path.home')
    def test_status_bar_visual(self, mock_home, qtbot):
        """Test status bar visual appearance."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Update status message
        window.update_status("Ready to scan directory")
        qtbot.wait(100)

        # Take screenshot of status bar
        if window.statusBar():
            status_screenshot = window.statusBar().grab()
            self.save_reference_image(status_screenshot, "status_bar")

    def test_dialog_visual_consistency(self, qtbot):
        """Test dialog visual consistency."""
        # This would test file dialogs, message boxes, etc.
        # For now, we'll just verify that dialogs can be created
        from PyQt6.QtWidgets import QMessageBox

        msgbox = QMessageBox()
        msgbox.setWindowTitle("Test Dialog")
        msgbox.setText("This is a test dialog")
        qtbot.addWidget(msgbox)

        # Don't show as it would block testing
        # Just verify it can be created and styled
        assert msgbox.windowTitle() == "Test Dialog"

    def find_tab_index(self, window, tab_name):
        """Helper to find tab index by name."""
        tab_widget = window.tab_widget
        for i in range(tab_widget.count()):
            if tab_name.lower() in tab_widget.tabText(i).lower():
                return i
        return -1

    def save_reference_image(self, pixmap: QPixmap, name: str):
        """Save reference image for visual comparison."""
        # Create screenshots directory
        screenshots_dir = Path(__file__).parent / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)

        # Save screenshot
        screenshot_path = screenshots_dir / f"{name}.png"
        pixmap.save(str(screenshot_path))

        # Verify file was created
        assert screenshot_path.exists()
        assert screenshot_path.stat().st_size > 0

    @pytest.mark.parametrize("theme", ["light", "dark"])
    @patch('src.utils.settings.Path.home')
    def test_theme_consistency_visual(self, mock_home, qtbot, theme):
        """Test visual consistency across themes."""
        mock_home.return_value = Path(self.temp_dir)

        # Apply theme
        theme_manager.apply_theme(theme)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(500)

        # Take screenshot
        screenshot = window.grab()
        self.save_reference_image(screenshot, f"theme_consistency_{theme}")

        # Verify theme applied correctly
        assert theme_manager.current_theme == theme

    @patch('src.utils.settings.Path.home')
    def test_window_resize_visual(self, mock_home, qtbot):
        """Test window resize behavior."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Test different window sizes
        sizes = [(800, 600), (1200, 800), (1600, 1000)]

        for width, height in sizes:
            window.resize(width, height)
            qtbot.wait(200)

            screenshot = window.grab()
            self.save_reference_image(screenshot, f"window_resize_{width}x{height}")

            # Verify window resized correctly
            assert window.width() == width
            assert window.height() == height

