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
        """Load SVG icon definitions from resource files"""
        from pathlib import Path

        # Get the project root directory
        current_dir = Path(__file__).parent.parent.parent.parent
        icons_dir = current_dir / "resource" / "icons"

        self._svg_cache = {}

        # Load all SVG files from the icons directory
        if icons_dir.exists():
            for svg_file in icons_dir.glob("*.svg"):
                icon_name = svg_file.stem
                try:
                    with open(svg_file, encoding='utf-8') as f:
                        svg_content = f.read()
                        self._svg_cache[icon_name] = svg_content
                except Exception as e:
                    print(f"Warning: Could not load icon {icon_name}: {e}")

        # Add fallback icons if directory doesn't exist or is empty
        if not self._svg_cache:
            self._load_fallback_icons()

    def _load_fallback_icons(self):
        """Load fallback SVG icons if resource files are not available"""
        self._svg_cache = {
            "folder": """<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/></svg>""",
            "file": """<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2H6c-1.11 0-2 .89-2 2v16c0 1.11.89 2 2 2h12c1.11 0 2-.89 2-2V9l-7-7z"/><path d="M13 2v7h7" stroke="currentColor" stroke-width="2" fill="none"/></svg>""",
            "chart": """<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3v18h18"/><rect x="7" y="12" width="2" height="8"/><rect x="11" y="8" width="2" height="12"/><rect x="15" y="14" width="2" height="6"/><rect x="19" y="10" width="2" height="10"/></svg>""",
            "settings": """<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>""",
            "refresh": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12c0-4.97 4.03-9 9-9s9 4.03 9 9-4.03 9-9 9c-2.39 0-4.54-.96-6.07-2.49"/><path d="M3 18l3 0 0-3"/></svg>""",
            "search": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="21 21l-4.35-4.35"/></svg>""",
            "close": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m18 6-12 12"/><path d="m6 6 12 12"/></svg>""",
            "menu": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18"/><path d="M3 6h18"/><path d="M3 18h18"/></svg>""",
            "home": """<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22" fill="none" stroke="white" stroke-width="2"/></svg>"""
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
