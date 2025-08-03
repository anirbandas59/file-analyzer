"""
Themed Widget Components

This module provides theme-aware widget components that automatically
follow the design system and update when themes change.
"""


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...themes.design_system import IconSystem, Spacing
from ...themes.theme_provider import theme_provider


class ThemedButton(QPushButton):
    """Theme-aware button component"""

    def __init__(self, text: str = "", variant: str = "primary", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.setProperty("class", variant)
        self._setup_button()
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def _setup_button(self):
        """Setup button styling"""
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self.style().unpolish(self)
        self.style().polish(self)


class ThemedLabel(QLabel):
    """Theme-aware label component"""

    def __init__(self, text: str = "", variant: str = "body", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.setProperty("class", variant)
        self._setup_label()
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def _setup_label(self):
        """Setup label styling"""
        self.setWordWrap(True)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self.style().unpolish(self)
        self.style().polish(self)


class ThemedCard(QFrame):
    """Theme-aware card component"""

    def __init__(self, variant: str = "card", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.setProperty("class", variant)
        self._setup_card()
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def _setup_card(self):
        """Setup card styling"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self.style().unpolish(self)
        self.style().polish(self)


class ThemedInput(QLineEdit):
    """Theme-aware input component"""

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self._setup_input()
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def _setup_input(self):
        """Setup input styling"""
        pass

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self.style().unpolish(self)
        self.style().polish(self)


class ThemedIcon(QLabel):
    """Theme-aware icon component"""

    def __init__(self, icon_name: str, size: int = IconSystem.SIZE_MD, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.icon_size = size
        self._setup_icon()
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def _setup_icon(self):
        """Setup icon styling"""
        self._update_icon()
        self.setFixedSize(self.icon_size, self.icon_size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _update_icon(self):
        """Update icon based on current theme"""
        theme_name = theme_provider.current_theme
        icon_data = IconSystem.ICONS.get(self.icon_name, {})
        icon_text = icon_data.get(theme_name, icon_data.get("unicode", "?"))

        self.setText(icon_text)
        font = QFont()
        font.setPointSize(self.icon_size - 4)
        self.setFont(font)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self._update_icon()


class ThemedContainer(QFrame):
    """Theme-aware container component"""

    def __init__(self, layout_type: str = "vertical", parent=None):
        super().__init__(parent)
        self.layout_type = layout_type
        self._setup_container()
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def _setup_container(self):
        """Setup container layout"""
        if self.layout_type == "vertical":
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)

        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.MD)
        self.setLayout(layout)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self.style().unpolish(self)
        self.style().polish(self)


class ThemedChart(QFrame):
    """Theme-aware chart container"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.chart_title = title
        self.setProperty("class", "chart-container")
        self._setup_chart()
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def _setup_chart(self):
        """Setup chart container"""
        layout = QVBoxLayout(self)

        if self.chart_title:
            title_label = ThemedLabel(self.chart_title, "chart-title")
            layout.addWidget(title_label)

        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        self.setLayout(layout)

    def add_chart_widget(self, widget: QWidget):
        """Add a chart widget to the container"""
        self.layout().addWidget(widget)

    def get_chart_colors(self) -> list:
        """Get theme-appropriate chart colors"""
        palette = theme_provider.current_palette
        return [
            palette.chart_primary,
            palette.chart_secondary,
            palette.chart_tertiary,
            palette.chart_quaternary,
        ]

    def get_chart_background(self) -> QColor:
        """Get chart background color"""
        return theme_provider.current_palette.chart_background

    def get_chart_text_color(self) -> QColor:
        """Get chart text color"""
        return theme_provider.current_palette.chart_legend

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self.style().unpolish(self)
        self.style().polish(self)


class ThemedStatsCard(ThemedCard):
    """Enhanced stats card with theme awareness"""

    def __init__(self, title: str, value: str, icon_name: str = "", parent=None):
        super().__init__("stats-card", parent)
        self.card_title = title
        self.card_value = value
        self.card_icon = icon_name
        self._setup_stats_card()

    def _setup_stats_card(self):
        """Setup stats card layout"""
        layout = QVBoxLayout(self)

        # Icon if provided
        if self.card_icon:
            icon = ThemedIcon(self.card_icon, IconSystem.SIZE_LG)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon)

        # Value (large number)
        value_label = QLabel(self.card_value)
        value_label.setObjectName("stats_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)

        # Title
        title_label = QLabel(self.card_title)
        title_label.setObjectName("stats_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.SM)
        self.setLayout(layout)

        # Make card hoverable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def update_value(self, new_value: str):
        """Update the card value"""
        self.card_value = new_value
        value_label = self.findChild(QLabel)
        if value_label and value_label.objectName() == "stats_value":
            value_label.setText(new_value)


class ThemedTitle(ThemedLabel):
    """Convenient title label"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, "title", parent)


class ThemedSubtitle(ThemedLabel):
    """Convenient subtitle label"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, "subtitle", parent)


class ThemedHeading(ThemedLabel):
    """Convenient heading label"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, "heading", parent)


class ThemedCaption(ThemedLabel):
    """Convenient caption label"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, "caption", parent)
