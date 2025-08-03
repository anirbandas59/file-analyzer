#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from src.models.file_system_model import FileSystemTableModel


class TestFileSystemTableModel(unittest.TestCase):

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
        self.model = FileSystemTableModel()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_model_initialization(self):
        """Test FileSystemTableModel initialization."""
        self.assertIsNotNone(self.model)
        self.assertEqual(self.model.rowCount(), 0)
        self.assertEqual(self.model.columnCount(), 4)

    def test_update_data(self):
        """Test updating model data."""
        from datetime import datetime
        test_data = [
            {"name": "test.txt", "size": 1024, "modified": datetime.now(), "type": "Text File"},
            {"name": "test.py", "size": 2048, "modified": datetime.now(), "type": "Python File"}
        ]
        self.model.update_data(test_data)
        self.assertEqual(self.model.rowCount(), 2)

    def test_model_data_access(self):
        """Test accessing model data."""
        from datetime import datetime
        from PyQt6.QtCore import QModelIndex
        
        test_data = [
            {"name": "test.txt", "size": 1024, "modified": datetime.now(), "type": "Text File"}
        ]
        self.model.update_data(test_data)
        
        index = self.model.index(0, 0)
        name = self.model.data(index)
        self.assertEqual(name, "test.txt")
        
        size_index = self.model.index(0, 1)
        size = self.model.data(size_index)
        self.assertIn("KB", size)  # Size should be formatted

    def test_model_sorting(self):
        """Test model sorting functionality."""
        from datetime import datetime
        
        test_data = [
            {"name": "z_file.txt", "size": 1024, "modified": datetime.now(), "type": "Text File"},
            {"name": "a_file.txt", "size": 2048, "modified": datetime.now(), "type": "Text File"}
        ]
        self.model.update_data(test_data)
        
        # Sort by name ascending
        self.model.sort(0, Qt.SortOrder.AscendingOrder)
        
        first_name = self.model.data(self.model.index(0, 0))
        self.assertEqual(first_name, "a_file.txt")

    def test_model_filtering(self):
        """Test model filtering functionality."""
        from datetime import datetime
        
        test_data = [
            {"name": "test.txt", "size": 1024, "modified": datetime.now(), "type": "Text File"},
            {"name": "script.py", "size": 2048, "modified": datetime.now(), "type": "Python File"}
        ]
        self.model.update_data(test_data)
        self.assertEqual(self.model.rowCount(), 2)
        
        # Test filtering (this would need to be implemented in the model)
        # For now just test that original data is preserved
        self.assertEqual(len(self.model.original_files), 2)

    def test_model_header_data(self):
        """Test model header data."""
        from PyQt6.QtCore import Qt
        
        headers = []
        for i in range(self.model.columnCount()):
            header = self.model.headerData(i, Qt.Orientation.Horizontal)
            headers.append(header)
        
        expected_headers = ["Name", "Size", "Modified", "Type"]
        self.assertEqual(headers, expected_headers)

    def test_empty_model(self):
        """Test model with no data."""
        self.assertEqual(self.model.rowCount(), 0)
        
        # Should return QVariant for invalid indices
        invalid_index = self.model.index(0, 0)
        data = self.model.data(invalid_index)
        from PyQt6.QtCore import QVariant
        self.assertEqual(data, QVariant())







if __name__ == '__main__':
    unittest.main()

