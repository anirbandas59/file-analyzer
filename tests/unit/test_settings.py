#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.settings import SettingsManager


class TestSettingsManager(unittest.TestCase):

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = Path(self.temp_dir) / "settings.json"
        self.backup_file = Path(self.temp_dir) / "settings_backup.json"

        # Create fresh instance for each test
        SettingsManager._instance = None

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        SettingsManager._instance = None

    @patch('src.utils.settings.Path.home')
    def test_singleton_pattern(self, mock_home):
        """Test that SettingsManager follows singleton pattern."""
        mock_home.return_value = Path(self.temp_dir)

        settings1 = SettingsManager()
        settings2 = SettingsManager()

        self.assertIs(settings1, settings2)

    @patch('src.utils.settings.Path.home')
    def test_default_settings_initialization(self, mock_home):
        """Test that default settings are properly initialized."""
        mock_home.return_value = Path(self.temp_dir)

        settings = SettingsManager()

        # Test default values
        self.assertEqual(settings.get_theme(), "light")
        self.assertEqual(settings.get("version"), "1.0.0")
        self.assertTrue(isinstance(settings.get_last_directory(), str))

    @patch('src.utils.settings.Path.home')
    def test_get_and_set_theme(self, mock_home):
        """Test theme getter and setter."""
        mock_home.return_value = Path(self.temp_dir)

        settings = SettingsManager()

        # Test default theme
        self.assertEqual(settings.get_theme(), "light")

        # Test setting dark theme
        settings.set_theme("dark")
        self.assertEqual(settings.get_theme(), "dark")

        # Test invalid theme defaults to light
        settings.set_theme("invalid")
        self.assertEqual(settings.get_theme(), "light")

    @patch('src.utils.settings.Path.home')
    def test_recent_directories_management(self, mock_home):
        """Test recent directories functionality."""
        mock_home.return_value = Path(self.temp_dir)

        settings = SettingsManager()

        # Test initial empty list
        recent_dirs = settings.get_recent_directories()
        self.assertEqual(recent_dirs, [])

        # Test adding directories
        test_dir1 = "/path/to/dir1"
        test_dir2 = "/path/to/dir2"

        settings.add_recent_directory(test_dir1)
        self.assertEqual(settings.get_recent_directories(), [test_dir1])

        settings.add_recent_directory(test_dir2)
        self.assertEqual(settings.get_recent_directories(), [test_dir2, test_dir1])

        # Test duplicate handling
        settings.add_recent_directory(test_dir1)
        self.assertEqual(settings.get_recent_directories(), [test_dir1, test_dir2])

    @patch('src.utils.settings.Path.home')
    def test_window_geometry_persistence(self, mock_home):
        """Test window geometry settings."""
        mock_home.return_value = Path(self.temp_dir)

        settings = SettingsManager()

        # Test default geometry
        geometry = settings.get_window_geometry()
        expected_keys = ["width", "height", "x", "y", "maximized"]
        for key in expected_keys:
            self.assertIn(key, geometry)

        # Test setting geometry
        settings.set_window_geometry(1200, 800, 100, 50, True)
        geometry = settings.get_window_geometry()

        self.assertEqual(geometry["width"], 1200)
        self.assertEqual(geometry["height"], 800)
        self.assertEqual(geometry["x"], 100)
        self.assertEqual(geometry["y"], 50)
        self.assertTrue(geometry["maximized"])

    @patch('src.utils.settings.Path.home')
    def test_settings_persistence(self, mock_home):
        """Test that settings are properly saved and loaded."""
        mock_home.return_value = Path(self.temp_dir)

        # Create settings and modify some values
        settings1 = SettingsManager()
        settings1.set_theme("dark")
        settings1.add_recent_directory("/test/path")
        settings1.save()

        # Create new instance (simulating app restart)
        SettingsManager._instance = None
        settings2 = SettingsManager()

        # Verify values persisted
        self.assertEqual(settings2.get_theme(), "dark")
        self.assertEqual(settings2.get_recent_directories(), ["/test/path"])

    @patch('src.utils.settings.Path.home')
    @patch('builtins.open', side_effect=OSError("File not found"))
    def test_error_handling_file_not_found(self, mock_open_func, mock_home):
        """Test error handling when settings file doesn't exist."""
        mock_home.return_value = Path(self.temp_dir)

        # Should not raise exception and use defaults
        settings = SettingsManager()
        self.assertEqual(settings.get_theme(), "light")

    @patch('src.utils.settings.Path.home')
    def test_corrupted_settings_file_recovery(self, mock_home):
        """Test recovery from corrupted settings file."""
        mock_home.return_value = Path(self.temp_dir)

        # Create corrupted settings file
        corrupted_data = "{ invalid json"
        self.settings_file.write_text(corrupted_data)

        # Should recover using defaults
        settings = SettingsManager()
        self.assertEqual(settings.get_theme(), "light")

    @patch('src.utils.settings.Path.home')
    def test_backup_and_recovery(self, mock_home):
        """Test backup creation and recovery mechanisms."""
        mock_home.return_value = Path(self.temp_dir)

        settings = SettingsManager()
        settings.set_theme("dark")
        settings.save()

        # Verify backup was created
        self.assertTrue(self.backup_file.exists())

        # Corrupt main file
        self.settings_file.write_text("corrupted")

        # Create new instance - should recover from backup
        SettingsManager._instance = None
        settings2 = SettingsManager()
        self.assertEqual(settings2.get_theme(), "dark")


if __name__ == '__main__':
    unittest.main()

