#!/usr/bin/env python3
# File: src/ui/components/card_widget.py

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..themes.styles import BorderRadius, ModernTheme, Spacing, Typography


class CardWidget(QFrame):
    """
    A modern card widget with rounded corners, shadow, and consistent theming.
    Provides a clean container for grouping related content.
    """

    def __init__(self, parent=None, elevation="md"):
        super().__init__(parent)

        self.elevation = elevation
        self.setup_card()

    def setup_card(self):
        """Initialize card styling and shadow effects."""
        # Set frame properties
        self.setFrameShape(QFrame.Shape.NoFrame)

        # Apply card styling
        stylesheet = f"""
        CardWidget {{
            background-color: {ModernTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.MD}px;
        }}
        """
        self.setStyleSheet(stylesheet)

        # Add shadow effect based on elevation
        self.add_shadow_effect()

    def add_shadow_effect(self):
        """Add drop shadow based on elevation level."""
        shadow = QGraphicsDropShadowEffect()

        # Configure shadow based on elevation
        if self.elevation == "sm":
            shadow.setBlurRadius(4)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 30))
        elif self.elevation == "lg":
            shadow.setBlurRadius(12)
            shadow.setXOffset(0)
            shadow.setYOffset(6)
            shadow.setColor(QColor(0, 0, 0, 60))
        else:  # md (default)
            shadow.setBlurRadius(8)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 40))

        self.setGraphicsEffect(shadow)

    def set_elevation(self, elevation):
        """
        Change the card elevation.

        Args:
            elevation: One of "sm", "md", "lg"
        """
        self.elevation = elevation
        self.add_shadow_effect()


class TitleCard(CardWidget):
    """
    A card widget with a built-in title header section.
    """

    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(parent)

        self.title_text = title
        self.subtitle_text = subtitle

        # Setup the layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create header section
        self.create_header()

        # Create content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(
            Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD
        )

        self.main_layout.addWidget(self.content_widget)

    def create_header(self):
        """Create the title header section."""
        self.header_widget = QWidget()
        self.header_layout = QVBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(
            Spacing.MD, Spacing.MD, Spacing.MD, Spacing.SM
        )

        # Title label
        if self.title_text:
            self.title_label = QLabel(self.title_text)
            self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_LG};
                font-weight: {Typography.WEIGHT_BOLD};
                color: {ModernTheme.VERY_DARK_GRAY.name()};
                background-color: transparent;
                border: none;
            }}
            """)
            self.header_layout.addWidget(self.title_label)

        # Subtitle label
        if self.subtitle_text:
            self.subtitle_label = QLabel(self.subtitle_text)
            self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_SM};
                color: {ModernTheme.DARK_GRAY.name()};
                background-color: transparent;
                border: none;
            }}
            """)
            self.header_layout.addWidget(self.subtitle_label)

        # Add separator line
        if self.title_text or self.subtitle_text:
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernTheme.MEDIUM_GRAY.name()};
                border: none;
                max-height: 1px;
            }}
            """)
            self.header_layout.addWidget(separator)

        self.main_layout.addWidget(self.header_widget)

    def set_title(self, title):
        """Update the card title."""
        self.title_text = title
        if hasattr(self, "title_label"):
            self.title_label.setText(title)

    def set_subtitle(self, subtitle):
        """Update the card subtitle."""
        self.subtitle_text = subtitle
        if hasattr(self, "subtitle_label"):
            self.subtitle_label.setText(subtitle)

    def add_content_widget(self, widget):
        """Add a widget to the content area."""
        self.content_layout.addWidget(widget)

    def add_content_layout(self, layout):
        """Add a layout to the content area."""
        self.content_layout.addLayout(layout)


class StatsCard(CardWidget):
    """
    A specialized card for displaying statistics with value and label.
    """

    def __init__(self, title="", value="", unit="", parent=None):
        super().__init__(parent)

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.XS)

        # Value label (large number)
        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"""
        QLabel {{
            font-size: {Typography.FONT_XXL};
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernTheme.PRIMARY.name()};
            background-color: transparent;
            border: none;
        }}
        """)

        # Unit label (if provided)
        if unit:
            value_with_unit = QHBoxLayout()
            value_with_unit.addWidget(self.value_label)

            unit_label = QLabel(unit)
            unit_label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_MD};
                color: {ModernTheme.DARK_GRAY.name()};
                background-color: transparent;
                border: none;
            }}
            """)
            value_with_unit.addWidget(unit_label)
            value_with_unit.addStretch()

            layout.addLayout(value_with_unit)
        else:
            layout.addWidget(self.value_label)

        # Title label
        if title:
            self.title_label = QLabel(title)
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_SM};
                color: {ModernTheme.DARK_GRAY.name()};
                background-color: transparent;
                border: none;
            }}
            """)
            layout.addWidget(self.title_label)

    def update_value(self, value, unit=""):
        """Update the displayed value."""
        self.value_label.setText(str(value))


class ActionCard(TitleCard):
    """
    A card with built-in action buttons in the header.
    """

    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(title, subtitle, parent)

        # Add actions area to header
        self.actions_layout = QHBoxLayout()
        self.actions_layout.addStretch()  # Push buttons to the right

        # Insert actions into header layout (before separator)
        header_layout = self.header_layout
        separator_index = header_layout.count() - 1  # Last item should be separator
        header_layout.insertLayout(separator_index, self.actions_layout)

    def add_action_button(self, button):
        """Add an action button to the header."""
        # Remove the stretch before adding button
        self.actions_layout.takeAt(self.actions_layout.count() - 1)

        # Add the button
        self.actions_layout.addWidget(button)

        # Add stretch back at the end
        self.actions_layout.addStretch()
