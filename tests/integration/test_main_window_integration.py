#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.main_window import MainWindow
from src.utils.settings import SettingsManager


class TestMainWindowIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

        # Reset settings singleton
        SettingsManager._instance = None

        # Create test files
        self.test_files = []
        for i, ext in enumerate(['txt', 'py', 'log']):
            file_path = Path(self.temp_dir) / f"test{i}.{ext}"
            file_path.write_text(f"Test content {i}")
            self.test_files.append(file_path)

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        SettingsManager._instance = None

    @patch('src.utils.settings.Path.home')
    def test_main_window_initialization(self, mock_home):
        """Test main window initialization and basic setup."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Window should be created with proper title
        self.assertEqual(window.windowTitle(), "File System Analyzer")

        # Key components should exist
        self.assertIsNotNone(window.directory_tree)
        self.assertIsNotNone(window.file_table)
        self.assertIsNotNone(window.tab_widget)
        self.assertIsNotNone(window.browse_button)
        self.assertIsNotNone(window.scan_button)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_browse_button_functionality(self, mock_home):
        """Test browse button opens directory dialog."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Mock the file dialog to return our temp directory
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory', return_value=self.temp_dir):
            # Simulate button click
            QTest.mouseClick(window.browse_button, Qt.MouseButton.LeftButton)

            # Current scan path should be updated
            self.assertEqual(window.current_scan_path, self.temp_dir)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_scan_button_triggers_analysis(self, mock_home):
        """Test scan button triggers file analysis."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        window.current_scan_path = self.temp_dir

        # Mock the scan directory function
        with patch('src.ui.main_window.scan_directory') as mock_scan:
            mock_scan.return_value = ([], 0)  # Empty result

            # Simulate scan button click
            QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)

            # Scan function should have been called
            mock_scan.assert_called_once()

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_directory_tree_selection_updates_scan_path(self, mock_home):
        """Test directory tree selection updates scan path."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Set up directory tree with test directory
        window.directory_tree.set_root_directory(self.temp_dir)

        # Simulate directory selection (this would normally be done via tree interaction)
        window.on_directory_selected(self.temp_dir)

        self.assertEqual(window.current_scan_path, self.temp_dir)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_tab_switching_functionality(self, mock_home):
        """Test tab switching between different views."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Should have multiple tabs
        self.assertGreater(window.tab_widget.count(), 1)

        # Test switching to different tabs
        for i in range(window.tab_widget.count()):
            window.tab_widget.setCurrentIndex(i)
            self.assertEqual(window.tab_widget.currentIndex(), i)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_file_table_data_update(self, mock_home):
        """Test file table updates when data changes."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Create test file data
        test_data = [
            {'name': 'test1.txt', 'size': 100, 'type': 'TXT', 'modified': None, 'path': str(self.test_files[0])},
            {'name': 'test2.py', 'size': 200, 'type': 'PY', 'modified': None, 'path': str(self.test_files[1])}
        ]

        # Update file table
        window.file_table.update_data(test_data)

        # Table should reflect the new data
        self.assertGreater(window.file_table.model.rowCount(), 0)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_visualization_dashboard_integration(self, mock_home):
        """Test visualization dashboard integration."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Should have visualization components
        self.assertIsNotNone(window.visualization_dashboard)

        # Test data update to visualization
        test_data = [
            {'name': 'test1.txt', 'size': 100, 'type': 'TXT'},
            {'name': 'test2.py', 'size': 200, 'type': 'PY'}
        ]

        # This should not crash
        window.visualization_dashboard.update_data(test_data)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_management_dashboard_integration(self, mock_home):
        """Test management dashboard integration."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Should have management components
        self.assertIsNotNone(window.management_dashboard)

        # Test that management dashboard can be accessed
        self.assertTrue(hasattr(window.management_dashboard, 'update_data'))

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_theme_switching_integration(self, mock_home):
        """Test theme switching affects all components."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Test theme switching
        from src.ui.themes.theme_manager import theme_manager

        # Switch to dark theme
        theme_manager.apply_theme("dark")

        # Switch back to light theme
        theme_manager.apply_theme("light")

        # Should not crash and window should still be functional
        self.assertTrue(window.isEnabled())

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_settings_persistence_integration(self, mock_home):
        """Test settings persistence across window sessions."""
        mock_home.return_value = Path(self.temp_dir)

        # Create first window and modify settings
        window1 = MainWindow()
        window1.resize(1200, 800)

        # Simulate window close which should save settings
        window1.close()

        # Create second window - should restore previous geometry
        window2 = MainWindow()
        # Note: Actual geometry restoration depends on implementation

        window2.close()

    @patch('src.utils.settings.Path.home')
    def test_error_handling_integration(self, mock_home):
        """Test error handling in integrated components."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Test with invalid directory
        window.current_scan_path = "/nonexistent/directory"

        # Should handle errors gracefully
        with patch('src.ui.main_window.scan_directory', side_effect=OSError("Permission denied")):
            # This should not crash the application
            QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_recent_directories_integration(self, mock_home):
        """Test recent directories functionality."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Should have recent directories combo box
        self.assertIsNotNone(window.recent_dirs_combo)

        # Add a recent directory
        window.on_recent_directory_selected(self.temp_dir)

        window.close()


if __name__ == '__main__':
    unittest.main()

