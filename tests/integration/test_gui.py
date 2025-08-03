#!/usr/bin/env python3
# File: tests/integration/test_gui.py

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.main_window import MainWindow
from src.ui.themes.theme_manager import theme_manager
from src.ui.themes.theme_provider import theme_provider
from src.utils.settings import SettingsManager


class TestGUIIntegration(unittest.TestCase):
    """Integration tests for GUI components."""

    @classmethod
    def setUpClass(cls):
        """Set up the QApplication once for all tests."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        SettingsManager._instance = None
        
        # Create test files
        test_files = [
            ("document.txt", "Sample text content"),
            ("script.py", "print('Hello, World!')"),
            ("data.json", '{"key": "value"}'),
        ]
        
        for filename, content in test_files:
            (Path(self.temp_dir) / filename).write_text(content)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        SettingsManager._instance = None

    @patch('src.utils.settings.Path.home')
    def test_main_window_initialization(self, mock_home):
        """Test main window initialization."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        self.assertIsNotNone(window)
        
        # Test that main components exist
        self.assertIsNotNone(window.tab_widget)
        self.assertIsNotNone(window.browse_button)
        self.assertIsNotNone(window.scan_button)

    @patch('src.utils.settings.Path.home')
    def test_theme_integration(self, mock_home):
        """Test theme integration with main window."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        
        # Test theme switching
        original_theme = theme_manager.current_theme
        
        # Apply dark theme
        theme_manager.apply_theme("dark")
        self.assertEqual(theme_provider.current_theme, "dark")
        
        # Apply light theme
        theme_manager.apply_theme("light")
        self.assertEqual(theme_provider.current_theme, "light")
        
        # Restore original theme
        theme_manager.apply_theme(original_theme)

    @patch('src.utils.settings.Path.home')
    def test_tab_widget_functionality(self, mock_home):
        """Test tab widget functionality."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        tab_widget = window.tab_widget
        
        # Should have at least Files, Charts, and Management tabs
        self.assertGreaterEqual(tab_widget.count(), 3)
        
        # Test tab switching
        for i in range(tab_widget.count()):
            tab_widget.setCurrentIndex(i)
            self.assertEqual(tab_widget.currentIndex(), i)

    @patch('src.utils.settings.Path.home')
    def test_directory_scanning_integration(self, mock_home):
        """Test directory scanning integration."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        
        # Set scan path
        window.current_scan_path = self.temp_dir
        
        # Should not crash when scanning
        try:
            # Simulate scan button click
            window.on_scan_clicked()
        except Exception as e:
            self.fail(f"Scanning should not crash: {e}")

    @patch('src.utils.settings.Path.home')
    def test_theme_provider_integration(self, mock_home):
        """Test new theme provider integration."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        
        # Test that theme provider is accessible
        self.assertIsNotNone(theme_provider.current_palette)
        
        # Test theme switching affects UI
        original_theme = theme_provider.current_theme
        
        theme_provider.set_theme("dark")
        self.assertEqual(theme_provider.current_theme, "dark")
        
        theme_provider.set_theme("light")
        self.assertEqual(theme_provider.current_theme, "light")
        
        # Restore
        theme_provider.set_theme(original_theme)

    @patch('src.utils.settings.Path.home')
    def test_new_design_system_components(self, mock_home):
        """Test new design system components integration."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        
        # Test that we can create themed components
        from src.ui.components.themed.themed_widgets import ThemedButton, ThemedCard
        
        button = ThemedButton("Test Button")
        self.assertIsNotNone(button)
        
        card = ThemedCard()
        self.assertIsNotNone(card)

    @patch('src.utils.settings.Path.home')
    def test_icon_system_integration(self, mock_home):
        """Test icon system integration."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        
        # Test icon manager accessibility
        from src.ui.themes.icon_manager import icon_manager
        
        # Should be able to get icons
        folder_icon = icon_manager.get_icon("folder", 24)
        self.assertIsNotNone(folder_icon)
        
        file_icon = icon_manager.get_icon("file", 24)
        self.assertIsNotNone(file_icon)

    def test_settings_persistence_integration(self):
        """Test settings persistence integration."""
        # Test that settings manager works with new theme system
        from src.utils.settings import settings
        
        # Should be able to get/set theme settings
        original_theme = settings.get("theme.current", "light")
        
        # Set new theme
        settings.set("theme.current", "dark")
        self.assertEqual(settings.get("theme.current"), "dark")
        
        # Restore
        settings.set("theme.current", original_theme)

    @patch('src.utils.settings.Path.home')
    def test_chart_theming_integration(self, mock_home):
        """Test chart theming integration."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        
        # Test chart theme manager
        from src.ui.themes.chart_theming import chart_theme_manager
        
        # Should be able to configure without errors
        chart_theme_manager.configure_matplotlib()
        
        # Should be able to get chart style config
        config = chart_theme_manager.get_chart_style_config()
        self.assertIsInstance(config, dict)
        self.assertIn('colors', config)

    @patch('src.utils.settings.Path.home')
    def test_visual_regression_components(self, mock_home):
        """Test components used in visual regression tests."""
        mock_home.return_value = Path(self.temp_dir)
        
        window = MainWindow()
        
        # Test that main window can be shown (for visual tests)
        try:
            window.show()
            window.hide()  # Hide immediately to avoid display issues in CI
        except Exception as e:
            self.fail(f"Window show/hide should not crash: {e}")
        
        # Test tab switching for visual tests
        tab_widget = window.tab_widget
        for i in range(tab_widget.count()):
            try:
                tab_widget.setCurrentIndex(i)
            except Exception as e:
                self.fail(f"Tab switching should not crash: {e}")


class TestThemeSystemIntegration(unittest.TestCase):
    """Integration tests specifically for the theme system."""

    @classmethod
    def setUpClass(cls):
        """Set up the QApplication once for all tests."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_theme_provider_stylesheet_generation(self):
        """Test theme provider stylesheet generation."""
        # Test both themes
        for theme_name in ["light", "dark"]:
            theme_provider.set_theme(theme_name)
            stylesheet = theme_provider.generate_global_stylesheet()
            
            self.assertIsInstance(stylesheet, str)
            self.assertGreater(len(stylesheet), 0)
            
            # Should contain expected CSS elements
            expected_elements = [
                "QMainWindow", "QPushButton", "QLabel", "color", "background-color"
            ]
            
            for element in expected_elements:
                self.assertIn(element, stylesheet)

    def test_theme_manager_backward_compatibility(self):
        """Test theme manager backward compatibility."""
        # Test old interface still works
        self.assertEqual(theme_manager.get_current_theme(), theme_provider.current_theme)
        
        # Test old color access
        primary = theme_manager.get_color("PRIMARY")
        self.assertIsNotNone(primary)
        
        # Test toggle functionality
        original_theme = theme_manager.current_theme
        theme_manager.toggle_theme()
        self.assertNotEqual(theme_manager.current_theme, original_theme)
        theme_manager.toggle_theme()
        self.assertEqual(theme_manager.current_theme, original_theme)

    def test_design_system_consistency(self):
        """Test design system consistency across themes."""
        light_palette = theme_provider._palettes["light"]
        dark_palette = theme_provider._palettes["dark"]
        
        # Test that palettes have all required attributes
        required_attrs = [
            "primary", "background", "text_primary", "chart_primary",
            "border", "surface", "success", "warning", "error"
        ]
        
        for attr in required_attrs:
            self.assertTrue(hasattr(light_palette, attr))
            self.assertTrue(hasattr(dark_palette, attr))

    def test_chart_theme_integration(self):
        """Test chart theme integration with theme provider."""
        from src.ui.themes.chart_theming import chart_theme_manager
        
        # Test that chart theming responds to theme changes
        original_theme = theme_provider.current_theme
        
        # Switch themes and test chart config updates
        for theme_name in ["light", "dark"]:
            theme_provider.set_theme(theme_name)
            config = chart_theme_manager.get_chart_style_config()
            
            self.assertIsInstance(config, dict)
            self.assertIn('colors', config)
            self.assertGreater(len(config['colors']), 0)
        
        # Restore original theme
        theme_provider.set_theme(original_theme)


if __name__ == '__main__':
    unittest.main()