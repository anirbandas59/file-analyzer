#!/usr/bin/env python3
# File: src/ui/components/modern_button.py

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QPushButton

from ..themes.styles import BorderRadius, ModernTheme, Spacing, Typography


class ModernButton(QPushButton):
    """
    A modern-styled button with hover effects, animations, and consistent theming.
    Supports different button styles: primary, secondary, danger, success.
    """

    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)

        self.button_type = button_type
        self._hover_color = ModernTheme.PRIMARY_DARK
        self._normal_color = ModernTheme.PRIMARY

        # Setup the button
        self.setup_button()
        self.setup_animations()

    def setup_button(self):
        """Initialize button styling and properties."""
        # Set minimum size for better touch targets
        self.setMinimumHeight(36)
        self.setMinimumWidth(80)

        # Apply style based on button type
        self.apply_button_style()

        # Add subtle shadow effect
        self.add_shadow_effect()

    def apply_button_style(self):
        """Apply styling based on button type."""
        styles = {
            "primary": {
                "normal": ModernTheme.PRIMARY,
                "hover": ModernTheme.PRIMARY_DARK,
                "text": ModernTheme.WHITE,
            },
            "secondary": {
                "normal": ModernTheme.LIGHT_GRAY,
                "hover": ModernTheme.MEDIUM_GRAY,
                "text": ModernTheme.VERY_DARK_GRAY,
            },
            "danger": {
                "normal": ModernTheme.ERROR,
                "hover": QColor("#c0392b"),  # Darker red
                "text": ModernTheme.WHITE,
            },
            "success": {
                "normal": ModernTheme.SUCCESS,
                "hover": QColor("#27ae60"),  # Darker green
                "text": ModernTheme.WHITE,
            },
        }

        style = styles.get(self.button_type, styles["primary"])
        self._normal_color = style["normal"]
        self._hover_color = style["hover"]

        # Apply the stylesheet
        stylesheet = f"""
        ModernButton {{
            background-color: {style["normal"].name()};
            color: {style["text"].name()};
            border: none;
            border-radius: {BorderRadius.SM};
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            font-size: {Typography.FONT_MD};
            font-family: {Typography.MAIN_FONT};
        }}

        ModernButton:hover {{
            background-color: {style["hover"].name()};
        }}

        ModernButton:pressed {{
            background-color: {style["hover"].name()};
            padding-top: {Spacing.SM + 1}px;
            padding-bottom: {Spacing.SM - 1}px;
        }}

        ModernButton:disabled {{
            background-color: {ModernTheme.MEDIUM_GRAY.name()};
            color: {ModernTheme.DARK_GRAY.name()};
        }}
        """

        self.setStyleSheet(stylesheet)

    def add_shadow_effect(self):
        """Add a subtle drop shadow effect for depth."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 50))  # Semi-transparent black
        self.setGraphicsEffect(shadow)

    def setup_animations(self):
        """Setup hover animations (placeholder for future enhancement)."""
        # TODO: Add smooth color transition animations
        # This could be implemented using QPropertyAnimation on custom properties
        pass

    def set_button_type(self, button_type):
        """
        Change the button type and update styling.

        Args:
            button_type: One of "primary", "secondary", "danger", "success"
        """
        self.button_type = button_type
        self.apply_button_style()

    def set_loading(self, loading=True):
        """
        Set loading state for the button.

        Args:
            loading: True to show loading state, False to show normal state
        """
        if loading:
            self.setEnabled(False)
            self.setText("Loading...")
            # TODO: Add spinner animation
        else:
            self.setEnabled(True)
            # Restore original text - would need to store it

    def enterEvent(self, event):
        """Handle mouse enter event for hover effects."""
        # Additional hover effects can be added here
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event."""
        # Reset any hover-specific effects
        super().leaveEvent(event)


class IconButton(ModernButton):
    """
    A modern button designed for icons with optional text.
    Square shape and smaller padding for icon-only buttons.
    """

    def __init__(self, icon=None, text="", parent=None):
        super().__init__(text, parent=parent)

        # Make it more square for icons
        self.setMinimumHeight(32)
        self.setMinimumWidth(32)

        if icon:
            self.setIcon(icon)

        # Adjust padding for icon buttons
        if not text:  # Icon-only button
            self.setStyleSheet(
                self.styleSheet()
                + f"""
            ModernButton {{
                padding: {Spacing.XS}px;
            }}
            """
            )


class PillButton(ModernButton):
    """
    A button with fully rounded corners (pill shape).
    Good for toggle buttons or special actions.
    """

    def setup_button(self):
        """Override to use pill-shaped styling."""
        super().setup_button()

        # Override border radius to be fully rounded
        current_style = self.styleSheet()
        pill_style = current_style.replace(
            f"border-radius: {BorderRadius.SM}",
            f"border-radius: {self.height() // 2}px",
        )
        self.setStyleSheet(pill_style)

    def resizeEvent(self, event):
        """Update border radius when button is resized."""
        super().resizeEvent(event)
        # Update the pill shape when size changes
        self.setup_button()
