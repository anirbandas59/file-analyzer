"""
Icon Manager for Cross-Platform Compatibility

This module provides a comprehensive icon system that works across all platforms,
including Linux where some fonts may not be available.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel

from .design_system import IconSystem
from .theme_provider import theme_provider


class IconManager:
    """Manages icons with cross-platform compatibility"""

    def __init__(self):
        self._icon_cache: dict[str, QIcon] = {}
        self._svg_cache: dict[str, str] = {}
        self._load_svg_icons()

    def _load_svg_icons(self):
        """Load SVG icon definitions"""
        # Define SVG icons as strings for better compatibility
        self._svg_cache = {
            "folder": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8l-2-2H2v2h4l2 2h12c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H8v2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
            """,
            "file": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                </svg>
            """,
            "chart": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21M16,8H18V15H16V8M12,2H14V15H12V2M8,13H10V15H8V13M4,15H6V15H4V15Z"/>
                </svg>
            """,
            "settings": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/>
                </svg>
            """,
            "refresh": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z"/>
                </svg>
            """,
            "search": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
                </svg>
            """,
            "arrow_up": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z"/>
                </svg>
            """,
            "arrow_down": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z"/>
                </svg>
            """,
            "close": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                </svg>
            """,
            "menu": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"/>
                </svg>
            """,
            "check": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/>
                </svg>
            """,
            "warning": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
                </svg>
            """,
            "info": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
                </svg>
            """,
            "error": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,2C17.53,2 22,6.47 22,12C22,17.53 17.53,22 12,22C6.47,22 2,17.53 2,12C2,6.47 6.47,2 12,2M15.59,7L12,10.59L8.41,7L7,8.41L10.59,12L7,15.59L8.41,17L12,13.41L15.59,17L17,15.59L13.41,12L17,8.41L15.59,7Z"/>
                </svg>
            """,
            "success": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,16.5L6.5,12L7.91,10.59L11,13.67L16.59,8.09L18,9.5L11,16.5Z"/>
                </svg>
            """,
            "home": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"/>
                </svg>
            """,
            "analytics": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16,11.78L20.24,4.45L21.97,5.45L16.74,14.5L10.23,10.75L5.46,19H22V21H2V3H4V17.54L9.5,8L16,11.78Z"/>
                </svg>
            """,
            "management": """
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,2A3,3 0 0,1 15,5V7H19A2,2 0 0,1 21,9V19A2,2 0 0,1 19,21H5A2,2 0 0,1 3,19V9A2,2 0 0,1 5,7H9V5A3,3 0 0,1 12,2M12,4A1,1 0 0,0 11,5V7H13V5A1,1 0 0,0 12,4Z"/>
                </svg>
            """
        }

    def get_icon(self, icon_name: str, size: int = IconSystem.SIZE_MD, color: QColor | None = None) -> QIcon:
        """Get a themed icon with specified size and color"""
        cache_key = f"{icon_name}_{size}_{color.name() if color else 'auto'}"

        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Use theme color if none specified
        if color is None:
            color = theme_provider.current_palette.text_primary

        # Create icon from SVG
        icon = self._create_svg_icon(icon_name, size, color)

        # Cache the icon
        self._icon_cache[cache_key] = icon
        return icon

    def _create_svg_icon(self, icon_name: str, size: int, color: QColor) -> QIcon:
        """Create an icon from SVG data"""
        svg_data = self._svg_cache.get(icon_name)
        if not svg_data:
            # Fallback to text-based icon
            return self._create_text_icon(icon_name, size, color)

        # Replace currentColor with actual color
        svg_data = svg_data.replace("currentColor", color.name())

        # Create pixmap from SVG
        pixmap = self._svg_to_pixmap(svg_data, size)
        return QIcon(pixmap)

    def _svg_to_pixmap(self, svg_data: str, size: int) -> QPixmap:
        """Convert SVG data to QPixmap"""
        try:
            from PyQt6.QtSvg import QSvgRenderer

            # Create SVG renderer
            renderer = QSvgRenderer()
            renderer.load(svg_data.encode())

            # Create pixmap
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            # Render SVG to pixmap
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return pixmap

        except (ImportError, Exception):
            # Fallback if SVG support is not available or any other error
            return self._create_fallback_pixmap(size)

    def _create_text_icon(self, icon_name: str, size: int, color: QColor) -> QIcon:
        """Create a text-based icon as fallback"""
        # Unicode fallbacks
        unicode_icons = {
            "folder": "📁",
            "file": "📄",
            "chart": "📊",
            "settings": "⚙",
            "refresh": "🔄",
            "search": "🔍",
            "arrow_up": "▲",
            "arrow_down": "▼",
            "close": "✕",
            "menu": "☰",
            "check": "✓",
            "warning": "⚠",
            "info": "i",
            "error": "✗",
            "success": "✓",
            "home": "🏠",
            "analytics": "📈",
            "management": "💼"
        }

        icon_text = unicode_icons.get(icon_name, "?")

        # Create pixmap with text
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set font
        font = QFont()
        font.setPointSize(max(8, size - 8))
        painter.setFont(font)
        painter.setPen(color)

        # Draw text centered
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, icon_text)
        painter.end()

        return QIcon(pixmap)

    def _create_fallback_pixmap(self, size: int) -> QPixmap:
        """Create a simple fallback pixmap"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(theme_provider.current_palette.text_secondary)
        painter.setBrush(theme_provider.current_palette.surface_variant)

        # Draw a simple rectangle
        rect = pixmap.rect().adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(rect, 3, 3)
        painter.end()

        return pixmap

    def clear_cache(self):
        """Clear the icon cache (useful when theme changes)"""
        self._icon_cache.clear()

    def get_available_icons(self) -> list:
        """Get list of available icon names"""
        return list(self._svg_cache.keys())


class IconWidget(QLabel):
    """A widget specifically for displaying themed icons"""

    def __init__(self, icon_name: str, size: int = IconSystem.SIZE_MD, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.icon_size = size
        self._icon_manager = icon_manager
        self._setup_widget()
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def _setup_widget(self):
        """Setup the icon widget"""
        self.setFixedSize(self.icon_size, self.icon_size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_icon()

    def _update_icon(self):
        """Update the icon based on current theme"""
        icon = self._icon_manager.get_icon(
            self.icon_name,
            self.icon_size,
            theme_provider.current_palette.text_primary
        )
        self.setPixmap(icon.pixmap(self.icon_size, self.icon_size))

    def set_color(self, color: QColor):
        """Set a custom color for the icon"""
        icon = self._icon_manager.get_icon(self.icon_name, self.icon_size, color)
        self.setPixmap(icon.pixmap(self.icon_size, self.icon_size))

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self._update_icon()


# Global icon manager instance
icon_manager = IconManager()

# Clear icon cache when theme changes
theme_provider.theme_changed.connect(lambda: icon_manager.clear_cache())
