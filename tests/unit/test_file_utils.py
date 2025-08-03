#!/usr/bin/env python3
# File: tests/test_file_utils.py

import os
import shutil

# Add the src directory to the path
import sys
import tempfile
import unittest
from datetime import datetime

from src.utils.file_utils import (
    format_size,
    get_directory_size,
    get_file_type,
    scan_directory,
)

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestFileUtils(unittest.TestCase):
    """
    Test cases for the file_utils module.
    """

    def setUp(self):
        """Create a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()

        # Create some test files
        with open(os.path.join(self.temp_dir, 'test.txt'), 'w') as f:
            f.write('This is a test file.')

        with open(os.path.join(self.temp_dir, 'example.py'), 'w') as f:
            f.write('print("Hello, world!")')

        # Create a subdirectory
        os.mkdir(os.path.join(self.temp_dir, 'subdir'))
        with open(os.path.join(self.temp_dir, 'subdir', 'test2.txt'), 'w') as f:
            f.write('This is another test file.')

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_format_size(self):
        """Test the format_size function."""
        test_cases = [
            (0, "0 B"),
            (1023, "1023 B"),
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
            (1024 * 1024 * 1024 * 1.5, "1.5 GB")
        ]

        for size, expected in test_cases:
            self.assertEqual(format_size(size), expected)

    def test_get_file_type(self):
        """Test the get_file_type function."""
        test_cases = [
            (os.path.join(self.temp_dir, 'test.txt'), "TXT"),
            (os.path.join(self.temp_dir, 'example.py'), "PY")
        ]

        for path, expected in test_cases:
            self.assertEqual(get_file_type(path), expected)

    def test_scan_directory(self):
        """Test the scan_directory function."""
        # Test non-recursive scan
        files, total_size = scan_directory(self.temp_dir, recursive=False)
        # Should only find the two files in the root dir
        self.assertEqual(len(files), 2)

        # Test recursive scan
        files, total_size = scan_directory(self.temp_dir, recursive=True)
        self.assertEqual(len(files), 3)  # Should find all three files

        # Verify file information
        for file_info in files:
            self.assertIn('name', file_info)
            self.assertIn('path', file_info)
            self.assertIn('size', file_info)
            self.assertIn('modified', file_info)
            self.assertIn('type', file_info)

            # Check that dates are datetime objects
            self.assertIsInstance(file_info['modified'], datetime)

    def test_get_directory_size(self):
        """Test the get_directory_size function."""
        # Get the expected size by manually calculating
        expected_size = 0
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                expected_size += os.path.getsize(os.path.join(root, file))

        # Compare with the function result
        self.assertEqual(get_directory_size(self.temp_dir), expected_size)


if __name__ == '__main__':
    unittest.main()
