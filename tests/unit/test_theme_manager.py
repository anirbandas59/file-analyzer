#!/usr/bin/env python3

import os
import sys
import unittest
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.themes.theme_manager import ThemeManager, theme_manager
from src.ui.themes.theme_provider import theme_provider


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
        # Safely create theme manager without triggering signals
        with patch.object(theme_provider, 'apply_theme_to_app'):
            self.theme_manager = ThemeManager()
            # Reset to light theme for consistent testing
            theme_provider._current_theme = "light"

    def test_initialization(self):
        """Test ThemeManager initialization."""
        self.assertEqual(self.theme_manager.current_theme, "light")
        self.assertIsNotNone(theme_provider.current_palette)

    def test_apply_light_theme(self):
        """Test applying light theme."""
        self.theme_manager.apply_theme("light")
        self.assertEqual(self.theme_manager.current_theme, "light")
        self.assertEqual(theme_provider.current_theme, "light")

    def test_apply_dark_theme(self):
        """Test applying dark theme."""
        self.theme_manager.apply_theme("dark")
        self.assertEqual(self.theme_manager.current_theme, "dark")
        self.assertEqual(theme_provider.current_theme, "dark")

    def test_apply_invalid_theme_no_crash(self):
        """Test that invalid theme names don't crash."""
        original_theme = self.theme_manager.current_theme
        self.theme_manager.apply_theme("invalid_theme")
        # Should remain unchanged for invalid themes
        self.assertEqual(self.theme_manager.current_theme, original_theme)

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

        # Should contain common CSS elements from new design system
        common_elements = ["QMainWindow", "QWidget", "color", "background-color", "QPushButton", "QLabel"]

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

    def test_new_design_system_integration(self):
        """Test integration with new design system."""
        # Test color access
        color = self.theme_manager.get_color("PRIMARY")
        self.assertIsNotNone(color)
        
        # Test chart colors
        chart_colors = self.theme_manager.get_chart_colors()
        self.assertIsInstance(chart_colors, list)
        self.assertGreater(len(chart_colors), 0)
        
        # Test icon access
        icon = self.theme_manager.get_icon("folder", 24)
        self.assertIsNotNone(icon)

    def test_theme_provider_compatibility(self):
        """Test compatibility with new theme provider."""
        # Test that theme manager uses theme provider
        self.theme_manager.apply_theme("dark")
        self.assertEqual(theme_provider.current_theme, "dark")
        
        # Test palette access
        palette = theme_provider.current_palette
        self.assertIsNotNone(palette.primary)
        self.assertIsNotNone(palette.background)
        self.assertIsNotNone(palette.text_primary)

    def test_chart_theme_integration(self):
        """Test chart theming integration."""
        # Should be able to apply chart theme without errors
        self.theme_manager.apply_chart_theme()
        
        # Test switching themes updates chart theming
        self.theme_manager.apply_theme("dark")
        self.theme_manager.apply_theme("light")

    def test_toggle_theme(self):
        """Test theme toggling functionality."""
        original_theme = self.theme_manager.current_theme
        
        self.theme_manager.toggle_theme()
        new_theme = self.theme_manager.current_theme
        
        # Should have switched
        self.assertNotEqual(original_theme, new_theme)
        
        # Toggle back
        self.theme_manager.toggle_theme()
        final_theme = self.theme_manager.current_theme
        
        # Should be back to original
        self.assertEqual(original_theme, final_theme)

    def test_backward_compatibility(self):
        """Test backward compatibility with old theme manager interface."""
        # Old methods should still work
        self.assertIsNotNone(self.theme_manager.get_current_theme())
        
        # Color mapping should work
        primary = self.theme_manager.get_color("PRIMARY")
        background = self.theme_manager.get_color("BACKGROUND")
        
        self.assertIsNotNone(primary)
        self.assertIsNotNone(background)


if __name__ == '__main__':
    unittest.main()