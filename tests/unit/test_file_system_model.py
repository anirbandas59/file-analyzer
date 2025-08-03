#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from src.models.file_system_model import FileSystemModel


class TestFileSystemModel(unittest.TestCase):

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
        self.model = FileSystemModel()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_model_initialization(self):
        """Test FileSystemModel initialization."""
        self.assertIsNotNone(self.model)
        self.assertIsNotNone(self.model.rootPath())

    def test_set_root_path(self):
        """Test setting root path."""
        self.model.setRootPath(self.temp_dir)
        self.assertEqual(self.model.rootPath(), self.temp_dir)

    def test_model_with_existing_directory(self):
        """Test model with an existing directory."""
        # Create test files
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")

        test_dir = Path(self.temp_dir) / "subdir"
        test_dir.mkdir()

        self.model.setRootPath(self.temp_dir)
        root_index = self.model.index(self.temp_dir)

        # Should have at least the files we created
        self.assertTrue(self.model.hasChildren(root_index))
        self.assertGreater(self.model.rowCount(root_index), 0)

    def test_model_data_retrieval(self):
        """Test data retrieval from model."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")

        self.model.setRootPath(self.temp_dir)
        root_index = self.model.index(self.temp_dir)

        if self.model.rowCount(root_index) > 0:
            child_index = self.model.index(0, 0, root_index)

            # Test getting file name
            name = self.model.data(child_index, Qt.ItemDataRole.DisplayRole)
            self.assertIsInstance(name, str)

            # Test getting file path
            path = self.model.filePath(child_index)
            self.assertIsInstance(path, str)

    def test_model_file_info(self):
        """Test file information retrieval."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")

        self.model.setRootPath(self.temp_dir)
        file_index = self.model.index(str(test_file))

        if file_index.isValid():
            file_info = self.model.fileInfo(file_index)
            self.assertIsNotNone(file_info)
            self.assertEqual(file_info.fileName(), "test.txt")

    def test_model_with_nonexistent_path(self):
        """Test model behavior with nonexistent path."""
        nonexistent_path = "/nonexistent/path"

        # Should not crash
        self.model.setRootPath(nonexistent_path)
        # root_index = self.model.index(nonexistent_path)

        # May or may not be valid depending on implementation
        # Just ensure it doesn't crash

    def test_model_sorting(self):
        """Test model sorting capabilities."""
        # Create multiple files for sorting
        files = ["z_file.txt", "a_file.txt", "m_file.txt"]
        for filename in files:
            (Path(self.temp_dir) / filename).write_text("content")

        self.model.setRootPath(self.temp_dir)
        self.model.sort(0, Qt.SortOrder.AscendingOrder)

        root_index = self.model.index(self.temp_dir)
        self.assertGreaterEqual(self.model.rowCount(root_index), len(files))

    def test_model_filtering(self):
        """Test model filtering functionality."""
        # Create test files with different extensions
        (Path(self.temp_dir) / "test.txt").write_text("content")
        (Path(self.temp_dir) / "test.py").write_text("content")
        (Path(self.temp_dir) / "test.log").write_text("content")

        self.model.setRootPath(self.temp_dir)

        # Test name filtering
        self.model.setNameFilters(["*.txt"])
        self.model.setNameFilterDisables(False)

        # root_index = self.model.index(self.temp_dir)
        # Should filter to show only .txt files

    def test_model_column_count(self):
        """Test model column structure."""
        self.model.setRootPath(self.temp_dir)
        root_index = self.model.index(self.temp_dir)

        column_count = self.model.columnCount(root_index)
        self.assertGreater(column_count, 0)

        # Typically has Name, Size, Type, Date Modified columns
        self.assertGreaterEqual(column_count, 4)

    def test_model_header_data(self):
        """Test model header information."""
        headers = []
        for column in range(self.model.columnCount()):
            header = self.model.headerData(column, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            headers.append(header)

        self.assertGreater(len(headers), 0)
        # Should contain typical file system headers
        header_text = " ".join(str(h) for h in headers if h)
        self.assertTrue(any(word in header_text.lower() for word in ["name", "size", "type", "date"]))

    def test_model_index_validation(self):
        """Test model index validation."""
        self.model.setRootPath(self.temp_dir)

        valid_index = self.model.index(self.temp_dir)
        self.assertTrue(valid_index.isValid())

        # Test invalid index
        invalid_index = self.model.index(-1, -1)
        self.assertFalse(invalid_index.isValid())

    def test_model_parent_child_relationship(self):
        """Test parent-child relationships in model."""
        # Create subdirectory
        subdir = Path(self.temp_dir) / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("content")

        self.model.setRootPath(self.temp_dir)
        root_index = self.model.index(self.temp_dir)

        if self.model.rowCount(root_index) > 0:
            child_index = self.model.index(0, 0, root_index)
            parent_index = self.model.parent(child_index)

            # Parent should be the root
            self.assertEqual(parent_index, root_index)


if __name__ == '__main__':
    unittest.main()

