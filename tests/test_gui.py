#!/usr/bin/env python3
# File: tests/test_gui.py

import os
import sys
import unittest

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from src.ui.directory_tree import DirectoryTreeView
from src.ui.file_table import FileTableView
from src.ui.main_window import MainWindow
from src.ui.visualization import FileTypeBar

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))


class MockMainWindow:
    """Mock main window for testing components in isolation."""

    def __init__(self):
        self.status_message = None

    def update_status(self, message):
        self.status_message = message


class TestGUIComponents(unittest.TestCase):
    """Test cases for the GUI components."""

    @classmethod
    def setUpClass(cls):
        """Set up the QApplication once for all tests."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_directory_tree(self):
        """Test the directory tree view."""
        tree = DirectoryTreeView()
        self.assertIsNotNone(tree.model)
        self.assertIsInstance(tree.model, QStandardItemModel)
        # Test that the home directory is in the tree
        self.assertGreater(tree.model.rowCount(), 0)

    def test_file_table(self):
        """Test the file table view."""
        table = FileTableView()
        self.assertIsNotNone(table.model)
        self.assertTrue(table.isSortingEnabled())

    def test_file_type_bar(self):
        """Test the file type visualization bar."""
        bar = FileTypeBar()

        # Test with empty data
        bar.update_data([])
        self.assertEqual(bar.data, {})

        # Test with some data
        test_files = [
            {
                "name": "test1.txt",
                "size": 1000,
                "type": "TXT",
                "modified": None,
                "path": None,
            },
            {
                "name": "test2.txt",
                "size": 2000,
                "type": "TXT",
                "modified": None,
                "path": None,
            },
            {
                "name": "test.exe",
                "size": 5000,
                "type": "EXE",
                "modified": None,
                "path": None,
            },
        ]
        bar.update_data(test_files)
        self.assertEqual(bar.data["TXT"], 3000)
        self.assertEqual(bar.data["EXE"], 5000)
        self.assertEqual(bar.total_size, 8000)


if __name__ == "__main__":
    unittest.main()
