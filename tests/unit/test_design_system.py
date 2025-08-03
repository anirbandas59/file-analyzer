#!/usr/bin/env python3

import os
import sys
import unittest

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.themes.design_system import (
    LightThemePalette, DarkThemePalette, Typography, Spacing, BorderRadius,
    ComponentSpecs, IconSystem
)
from src.ui.themes.theme_provider import theme_provider
from src.ui.themes.icon_manager import icon_manager


class TestDesignSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_light_theme_palette(self):
        """Test light theme palette creation."""
        palette = LightThemePalette.get_palette()
        
        # Test that all required colors are present
        self.assertIsInstance(palette.primary, QColor)
        self.assertIsInstance(palette.background, QColor)
        self.assertIsInstance(palette.text_primary, QColor)
        
        # Test that colors are different
        self.assertNotEqual(palette.primary, palette.background)
        self.assertNotEqual(palette.text_primary, palette.background)

    def test_dark_theme_palette(self):
        """Test dark theme palette creation."""
        palette = DarkThemePalette.get_palette()
        
        # Test that all required colors are present
        self.assertIsInstance(palette.primary, QColor)
        self.assertIsInstance(palette.background, QColor)
        self.assertIsInstance(palette.text_primary, QColor)
        
        # Test that dark theme has darker background
        light_palette = LightThemePalette.get_palette()
        self.assertNotEqual(palette.background, light_palette.background)

    def test_typography_constants(self):
        """Test typography system constants."""
        # Test font sizes are reasonable
        self.assertGreater(Typography.FONT_LG, Typography.FONT_SM)
        self.assertGreater(Typography.FONT_XL, Typography.FONT_LG)
        
        # Test font weights
        self.assertGreater(Typography.WEIGHT_BOLD, Typography.WEIGHT_NORMAL)
        self.assertGreater(Typography.WEIGHT_MEDIUM, Typography.WEIGHT_NORMAL)
        
        # Test font families
        self.assertIsInstance(Typography.FONT_FAMILY_PRIMARY, str)
        self.assertIn("sans-serif", Typography.FONT_FAMILY_PRIMARY)

    def test_spacing_system(self):
        """Test spacing system consistency."""
        # Test spacing scale increases
        self.assertLess(Spacing.XS, Spacing.SM)
        self.assertLess(Spacing.SM, Spacing.MD)
        self.assertLess(Spacing.MD, Spacing.LG)
        
        # Test base unit
        self.assertEqual(Spacing.BASE, 8)
        self.assertEqual(Spacing.SM, Spacing.BASE)

    def test_border_radius_system(self):
        """Test border radius system."""
        # Test border radius increases
        self.assertLess(BorderRadius.SM, BorderRadius.MD)
        self.assertLess(BorderRadius.MD, BorderRadius.LG)
        
        # Test full radius is large
        self.assertGreater(BorderRadius.FULL, BorderRadius.XL)

    def test_component_specs(self):
        """Test component specifications."""
        button_specs = ComponentSpecs.get_button_specs()
        card_specs = ComponentSpecs.get_card_specs()
        input_specs = ComponentSpecs.get_input_specs()
        
        # Test button specs
        self.assertIn("primary", button_specs)
        self.assertIn("secondary", button_specs)
        self.assertIn("height", button_specs["primary"])
        
        # Test card specs
        self.assertIn("default", card_specs)
        self.assertIn("elevated", card_specs)
        
        # Test input specs
        self.assertIn("default", input_specs)
        self.assertIn("large", input_specs)

    def test_icon_system(self):
        """Test icon system constants."""
        # Test icon sizes
        self.assertLess(IconSystem.SIZE_SM, IconSystem.SIZE_MD)
        self.assertLess(IconSystem.SIZE_MD, IconSystem.SIZE_LG)
        
        # Test icon mappings
        self.assertIn("folder", IconSystem.ICONS)
        self.assertIn("file", IconSystem.ICONS)
        self.assertIn("light", IconSystem.ICONS["folder"])
        self.assertIn("dark", IconSystem.ICONS["folder"])


class TestThemeProvider(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Reset theme provider for each test."""
        theme_provider.set_theme("light")

    def test_theme_provider_initialization(self):
        """Test theme provider initialization."""
        self.assertEqual(theme_provider.current_theme, "light")
        self.assertIsNotNone(theme_provider.current_palette)

    def test_theme_switching(self):
        """Test theme switching functionality."""
        # Start with light theme
        self.assertEqual(theme_provider.current_theme, "light")
        
        # Switch to dark
        theme_provider.set_theme("dark")
        self.assertEqual(theme_provider.current_theme, "dark")
        
        # Switch back to light
        theme_provider.set_theme("light")
        self.assertEqual(theme_provider.current_theme, "light")

    def test_palette_access(self):
        """Test palette access through theme provider."""
        # Light theme
        theme_provider.set_theme("light")
        light_palette = theme_provider.current_palette
        
        # Dark theme
        theme_provider.set_theme("dark")
        dark_palette = theme_provider.current_palette
        
        # Palettes should be different
        self.assertNotEqual(light_palette.background, dark_palette.background)
        self.assertNotEqual(light_palette.text_primary, dark_palette.text_primary)

    def test_color_access(self):
        """Test color access by role."""
        primary = theme_provider.get_color("primary")
        background = theme_provider.get_color("background")
        
        self.assertIsInstance(primary, QColor)
        self.assertIsInstance(background, QColor)
        self.assertNotEqual(primary, background)

    def test_stylesheet_generation(self):
        """Test stylesheet generation."""
        stylesheet = theme_provider.generate_global_stylesheet()
        
        self.assertIsInstance(stylesheet, str)
        self.assertGreater(len(stylesheet), 0)
        
        # Should contain CSS elements
        self.assertIn("QMainWindow", stylesheet)
        self.assertIn("QPushButton", stylesheet)
        self.assertIn("color", stylesheet)

    def test_invalid_theme_handling(self):
        """Test handling of invalid theme names."""
        original_theme = theme_provider.current_theme
        
        # Try to set invalid theme
        theme_provider.set_theme("invalid_theme")
        
        # Should remain unchanged
        self.assertEqual(theme_provider.current_theme, original_theme)

    def test_theme_change_signals(self):
        """Test theme change signal emission."""
        signal_received = []
        
        def on_theme_changed(theme_name):
            signal_received.append(theme_name)
        
        theme_provider.theme_changed.connect(on_theme_changed)
        
        # Change theme
        theme_provider.set_theme("dark")
        
        # Signal should be emitted
        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0], "dark")


class TestIconManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_icon_manager_initialization(self):
        """Test icon manager initialization."""
        self.assertIsNotNone(icon_manager)
        
        # Should have available icons
        icons = icon_manager.get_available_icons()
        self.assertIsInstance(icons, list)
        self.assertGreater(len(icons), 0)

    def test_icon_creation(self):
        """Test icon creation."""
        icon = icon_manager.get_icon("folder", 24)
        self.assertIsNotNone(icon)
        
        # Test different sizes
        small_icon = icon_manager.get_icon("folder", 16)
        large_icon = icon_manager.get_icon("folder", 32)
        
        self.assertIsNotNone(small_icon)
        self.assertIsNotNone(large_icon)

    def test_icon_caching(self):
        """Test icon caching functionality."""
        # First call creates icon
        icon1 = icon_manager.get_icon("folder", 24)
        
        # Second call should return cached icon
        icon2 = icon_manager.get_icon("folder", 24)
        
        # Should be the same instance (cached)
        self.assertEqual(icon1, icon2)

    def test_cache_clearing(self):
        """Test cache clearing."""
        # Create an icon to populate cache
        icon_manager.get_icon("folder", 24)
        
        # Clear cache
        icon_manager.clear_cache()
        
        # Should not crash and should work normally
        new_icon = icon_manager.get_icon("folder", 24)
        self.assertIsNotNone(new_icon)

    def test_theme_aware_icons(self):
        """Test theme-aware icon coloring."""
        # Light theme
        theme_provider.set_theme("light")
        light_icon = icon_manager.get_icon("folder", 24)
        
        # Dark theme
        theme_provider.set_theme("dark")
        dark_icon = icon_manager.get_icon("folder", 24)
        
        # Icons should exist for both themes
        self.assertIsNotNone(light_icon)
        self.assertIsNotNone(dark_icon)

    def test_fallback_icons(self):
        """Test fallback icon creation for unknown icons."""
        # Request unknown icon
        unknown_icon = icon_manager.get_icon("unknown_icon_name", 24)
        
        # Should still return an icon (fallback)
        self.assertIsNotNone(unknown_icon)

    def test_custom_color_icons(self):
        """Test custom color icon creation."""
        custom_color = QColor(255, 0, 0)  # Red
        red_icon = icon_manager.get_icon("folder", 24, custom_color)
        
        self.assertIsNotNone(red_icon)


if __name__ == '__main__':
    unittest.main()