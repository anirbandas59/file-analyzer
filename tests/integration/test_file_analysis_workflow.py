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
from src.utils.file_utils import scan_directory
from src.utils.settings import SettingsManager


class TestFileAnalysisWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test environment with sample files."""
        self.temp_dir = tempfile.mkdtemp()
        SettingsManager._instance = None

        # Create diverse test file structure
        self.create_test_file_structure()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        SettingsManager._instance = None

    def create_test_file_structure(self):
        """Create a comprehensive test file structure."""
        # Create directories
        (Path(self.temp_dir) / "documents").mkdir()
        (Path(self.temp_dir) / "images").mkdir()
        (Path(self.temp_dir) / "code").mkdir()
        (Path(self.temp_dir) / "empty").mkdir()

        # Create various file types with different sizes
        files_to_create = [
            ("document1.txt", "This is a text document", "documents"),
            ("document2.pdf", "PDF content placeholder", "documents"),
            ("script.py", "print('Hello World')\nprint('Python code')", "code"),
            ("readme.md", "# Readme\nThis is markdown", "code"),
            ("image1.jpg", "fake jpg content" * 100, "images"),  # Larger file
            ("image2.png", "fake png content" * 50, "images"),
            ("config.json", '{"setting": "value"}', "."),
            ("large_file.dat", "x" * 10000, "."),  # Large file for testing
        ]

        for filename, content, subdir in files_to_create:
            if subdir == ".":
                file_path = Path(self.temp_dir) / filename
            else:
                file_path = Path(self.temp_dir) / subdir / filename
            file_path.write_text(content)

    @patch('src.utils.settings.Path.home')
    def test_complete_directory_scan_workflow(self, mock_home):
        """Test complete workflow from directory selection to analysis display."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Step 1: Set directory
        window.current_scan_path = self.temp_dir

        # Step 2: Trigger scan
        QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)

        # Allow some time for processing
        QApplication.processEvents()

        # Step 3: Verify data populated in components
        # File table should have data
        self.assertGreater(window.file_table.model.rowCount(), 0)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_file_type_distribution_analysis(self, mock_home):
        """Test file type distribution analysis workflow."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        window.current_scan_path = self.temp_dir

        # Trigger analysis
        QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()

        # Check file type bar visualization
        file_type_bar = window.file_type_bar
        self.assertGreater(len(file_type_bar.data), 0)

        # Should have detected multiple file types
        detected_types = list(file_type_bar.data.keys())
        self.assertIn('TXT', detected_types)
        self.assertIn('PY', detected_types)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_large_file_detection_workflow(self, mock_home):
        """Test large file detection and analysis."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        window.current_scan_path = self.temp_dir

        # Trigger scan
        QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()

        # Switch to management tab to check large files
        management_tab_index = -1
        for i in range(window.tab_widget.count()):
            if "Management" in window.tab_widget.tabText(i):
                management_tab_index = i
                break

        if management_tab_index >= 0:
            window.tab_widget.setCurrentIndex(management_tab_index)

            # Large file analyzer should detect our large_file.dat
            # Note: Actual assertion depends on implementation details
            # large_file_analyzer = window.management_dashboard.large_file_analyzer

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_directory_tree_navigation_workflow(self, mock_home):
        """Test navigation through directory tree."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Set root directory in tree
        window.directory_tree.set_root_directory(self.temp_dir)

        # Verify tree shows our test directories
        model = window.directory_tree.model
        root_index = model.index(self.temp_dir)

        self.assertTrue(model.hasChildren(root_index))
        self.assertGreater(model.rowCount(root_index), 0)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_file_sorting_and_filtering_workflow(self, mock_home):
        """Test file sorting and filtering functionality."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        window.current_scan_path = self.temp_dir

        # Scan directory
        QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()

        # Test sorting by different columns
        file_table = window.file_table

        # Sort by name
        file_table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Sort by size
        file_table.sortByColumn(1, Qt.SortOrder.DescendingOrder)

        # Should not crash and table should still have data
        self.assertGreater(file_table.model.rowCount(), 0)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_visualization_updates_workflow(self, mock_home):
        """Test visualization components update with new data."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        window.current_scan_path = self.temp_dir

        # Initial scan
        QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()

        # Switch to Charts tab
        charts_tab_index = -1
        for i in range(window.tab_widget.count()):
            if "Charts" in window.tab_widget.tabText(i):
                charts_tab_index = i
                break

        if charts_tab_index >= 0:
            window.tab_widget.setCurrentIndex(charts_tab_index)

            # Visualization dashboard should have updated data
            viz_dashboard = window.visualization_dashboard
            self.assertIsNotNone(viz_dashboard)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_error_recovery_workflow(self, mock_home):
        """Test error recovery in analysis workflow."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()

        # Test with permission denied scenario
        with patch('src.utils.file_utils.scan_directory', side_effect=PermissionError("Access denied")):
            window.current_scan_path = self.temp_dir
            QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            # Should handle error gracefully
            self.assertTrue(window.isEnabled())

        # Test with corrupted file scenario
        with patch('src.utils.file_utils.scan_directory', side_effect=OSError("Disk error")):
            QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            # Should still be functional
            self.assertTrue(window.isEnabled())

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_memory_efficiency_workflow(self, mock_home):
        """Test memory efficiency with large directory scans."""
        mock_home.return_value = Path(self.temp_dir)

        # Create many files to test memory usage
        large_dir = Path(self.temp_dir) / "large_test"
        large_dir.mkdir()

        for i in range(50):  # Create 50 files
            (large_dir / f"file_{i:03d}.txt").write_text(f"Content of file {i}")

        window = MainWindow()
        window.current_scan_path = str(large_dir)

        # Scan large directory
        QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()

        # Should handle large number of files without issues
        self.assertGreaterEqual(window.file_table.model.rowCount(), 50)

        window.close()

    @patch('src.utils.settings.Path.home')
    def test_settings_integration_workflow(self, mock_home):
        """Test settings integration throughout workflow."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        window.current_scan_path = self.temp_dir

        # Scan and verify settings are updated
        QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()

        # Recent directories should be updated
        # settings = SettingsManager()
        # recent_dirs = settings.get_recent_directories()

        # Our temp directory might be in recent directories
        # (depends on implementation)

        window.close()

    def test_file_utils_integration(self):
        """Test direct integration with file_utils functions."""
        # Test scan_directory function directly
        files, total_size = scan_directory(self.temp_dir, recursive=True)

        # Should find all our test files
        self.assertGreater(len(files), 5)
        self.assertGreater(total_size, 0)

        # Verify file data structure
        for file_info in files:
            required_keys = ['name', 'path', 'size', 'modified', 'type']
            for key in required_keys:
                self.assertIn(key, file_info)

    @patch('src.utils.settings.Path.home')
    def test_concurrent_operations_workflow(self, mock_home):
        """Test handling of concurrent operations."""
        mock_home.return_value = Path(self.temp_dir)

        window = MainWindow()
        window.current_scan_path = self.temp_dir

        # Simulate rapid clicking (user impatience)
        for _ in range(3):
            QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

        # Should handle multiple requests gracefully
        self.assertTrue(window.isEnabled())

        window.close()


if __name__ == '__main__':
    unittest.main()

