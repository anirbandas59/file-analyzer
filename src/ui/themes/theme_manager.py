#!/usr/bin/env python3
# File: src/ui/themes/theme_manager.py

"""
Modern Theme Manager using Design System

This module provides a comprehensive theme management system built on top of
the design system for consistent and maintainable theming.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from .chart_theming import chart_theme_manager
from .icon_manager import icon_manager

# Import new design system components
from .theme_provider import theme_provider


class ThemeManager(QObject):
    """
    Central theme manager for the File Analyzer application.

    This manager integrates with the new design system to provide:
    - Consistent theme switching
    - Chart theming integration
    - Icon management
    - Backward compatibility with existing code
    """

    # Signal emitted when theme changes
    theme_changed = pyqtSignal(str)  # theme_name

    def __init__(self):
        super().__init__()
        self._setup_connections()

    def _setup_connections(self):
        """Setup connections between different theme components"""
        # Forward theme changes from the theme provider
        theme_provider.theme_changed.connect(self.theme_changed.emit)

        # Auto-configure charts when theme changes
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def apply_theme(self, theme_name="light"):
        """
        Apply a theme to the application.

        Args:
            theme_name: Name of the theme to apply ("light" or "dark")
        """
        # Use the new theme provider
        theme_provider.set_theme(theme_name)
        theme_provider.apply_theme_to_app()

    def get_stylesheet(self, theme_name="light"):
        """
        Get the complete stylesheet for the specified theme.

        Args:
            theme_name: Name of the theme

        Returns:
            Complete CSS stylesheet as string
        """
        # Temporarily set theme to get stylesheet
        current_theme = theme_provider.current_theme
        theme_provider.set_theme(theme_name)
        stylesheet = theme_provider.generate_global_stylesheet()

        # Restore original theme if it was different
        if current_theme != theme_name:
            theme_provider.set_theme(current_theme)

        return stylesheet

    def get_color(self, color_name):
        """
        Get a color from the current theme.

        Args:
            color_name: Name of the color role or attribute

        Returns:
            QColor object
        """
        # Map old color names to new system
        color_mapping = {
            "PRIMARY": "primary",
            "BACKGROUND": "background",
            "PANEL_BACKGROUND": "surface",
            "BORDER": "border",
            "VERY_DARK_GRAY": "text_primary",
            "DARK_GRAY": "text_secondary",
            "MEDIUM_GRAY": "text_tertiary",
            "WHITE": "text_inverse",
        }

        mapped_name = color_mapping.get(color_name, color_name.lower())

        try:
            return theme_provider.get_color(mapped_name)
        except AttributeError:
            # Fallback to primary color if attribute doesn't exist
            return theme_provider.current_palette.primary

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = "dark" if theme_provider.current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def get_current_theme(self):
        """Get the current theme name."""
        return theme_provider.current_theme

    @property
    def current_theme(self):
        """Current theme name for backward compatibility"""
        return theme_provider.current_theme

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        # Configure chart theming
        chart_theme_manager.configure_matplotlib()

        # Clear icon cache
        icon_manager.clear_cache()

    # Convenience methods for accessing design system components
    def get_chart_colors(self):
        """Get chart colors for current theme"""
        return chart_theme_manager.get_chart_style_config()['colors']

    def get_icon(self, icon_name: str, size: int = 20):
        """Get a themed icon"""
        return icon_manager.get_icon(icon_name, size)

    def apply_chart_theme(self):
        """Apply theme to matplotlib charts"""
        chart_theme_manager.configure_matplotlib()


# Global theme manager instance - maintains backward compatibility
theme_manager = ThemeManager()
