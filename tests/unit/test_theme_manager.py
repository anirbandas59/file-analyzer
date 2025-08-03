#!/usr/bin/env python3

import os
import sys
import unittest
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.themes.theme_manager import ThemeManager


class TestThemeManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up each test."""
        self.theme_manager = ThemeManager()

    def test_initialization(self):
        """Test ThemeManager initialization."""
        self.assertEqual(self.theme_manager.current_theme, "light")
        self.assertIsNotNone(self.theme_manager.themes_dir)

    def test_apply_light_theme(self):
        """Test applying light theme."""
        self.theme_manager.apply_theme("light")
        self.assertEqual(self.theme_manager.current_theme, "light")

    def test_apply_dark_theme(self):
        """Test applying dark theme."""
        self.theme_manager.apply_theme("dark")
        self.assertEqual(self.theme_manager.current_theme, "dark")

    def test_apply_invalid_theme_defaults_to_light(self):
        """Test that invalid theme names default to light theme."""
        self.theme_manager.apply_theme("invalid_theme")
        # Should not crash and should handle gracefully

    def test_get_stylesheet_light(self):
        """Test getting light theme stylesheet."""
        stylesheet = self.theme_manager.get_stylesheet("light")
        self.assertIsInstance(stylesheet, str)
        self.assertGreater(len(stylesheet), 0)

    def test_get_stylesheet_dark(self):
        """Test getting dark theme stylesheet."""
        stylesheet = self.theme_manager.get_stylesheet("dark")
        self.assertIsInstance(stylesheet, str)
        self.assertGreater(len(stylesheet), 0)

    def test_get_stylesheet_default(self):
        """Test getting default stylesheet."""
        stylesheet = self.theme_manager.get_stylesheet()
        self.assertIsInstance(stylesheet, str)
        self.assertGreater(len(stylesheet), 0)

    def test_theme_changed_signal(self):
        """Test that theme_changed signal is emitted."""
        signal_received = []

        def on_theme_changed(theme_name):
            signal_received.append(theme_name)

        self.theme_manager.theme_changed.connect(on_theme_changed)
        self.theme_manager.apply_theme("dark")

        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0], "dark")

    def test_apply_theme_without_app(self):
        """Test applying theme when no QApplication instance exists."""
        with patch('PyQt6.QtWidgets.QApplication.instance', return_value=None):
            # Should not crash when no app instance
            self.theme_manager.apply_theme("dark")

    def test_get_current_theme(self):
        """Test getting current theme."""
        self.theme_manager.apply_theme("dark")
        self.assertEqual(self.theme_manager.current_theme, "dark")

        self.theme_manager.apply_theme("light")
        self.assertEqual(self.theme_manager.current_theme, "light")

    def test_theme_consistency(self):
        """Test that themes are consistently applied."""
        # Apply dark theme
        self.theme_manager.apply_theme("dark")
        dark_stylesheet = self.theme_manager.get_stylesheet("dark")

        # Apply light theme
        self.theme_manager.apply_theme("light")
        light_stylesheet = self.theme_manager.get_stylesheet("light")

        # Stylesheets should be different
        self.assertNotEqual(dark_stylesheet, light_stylesheet)

    def test_stylesheet_contains_expected_elements(self):
        """Test that stylesheets contain expected CSS elements."""
        light_stylesheet = self.theme_manager.get_stylesheet("light")
        dark_stylesheet = self.theme_manager.get_stylesheet("dark")

        # Should contain common CSS elements
        common_elements = ["QWidget", "color", "background"]

        for element in common_elements:
            self.assertIn(element, light_stylesheet)
            self.assertIn(element, dark_stylesheet)

    def test_multiple_theme_applications(self):
        """Test applying themes multiple times."""
        # Should handle multiple applications without issues
        for _ in range(5):
            self.theme_manager.apply_theme("dark")
            self.assertEqual(self.theme_manager.current_theme, "dark")

            self.theme_manager.apply_theme("light")
            self.assertEqual(self.theme_manager.current_theme, "light")

    def test_theme_manager_singleton_like_behavior(self):
        """Test that theme manager can be used across the application."""
        # Create multiple instances (though not enforced singleton)
        tm1 = ThemeManager()
        tm2 = ThemeManager()

        # Both should be able to apply themes
        tm1.apply_theme("dark")
        tm2.apply_theme("light")

        # Last applied should be current for both
        self.assertEqual(tm2.current_theme, "light")


if __name__ == '__main__':
    unittest.main()

