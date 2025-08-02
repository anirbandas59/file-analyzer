#!/usr/bin/env python3
# File: src/ui/themes/styles.py

from typing import ClassVar

from PyQt6.QtGui import QColor


class ModernTheme:
    """
    Modern theme constants for the File Analyzer application.
    Based on the mockup design with #3498db accent color.
    """

    # Primary Colors (Blue theme from mockup)
    PRIMARY = QColor("#3498db")  # Main accent blue
    PRIMARY_DARK = QColor("#2980b9")  # Darker blue for hover states
    PRIMARY_LIGHT = QColor("#5dade2")  # Lighter blue for backgrounds

    # Neutral Colors
    WHITE = QColor("#ffffff")
    LIGHT_GRAY = QColor("#f8f9fa")  # Panel backgrounds
    MEDIUM_GRAY = QColor("#e9ecef")  # Borders and dividers
    DARK_GRAY = QColor("#6c757d")  # Secondary text
    VERY_DARK_GRAY = QColor("#343a40")  # Primary text

    # Background Colors
    BACKGROUND = QColor("#f5f5f5")  # Main background (from mockup)
    PANEL_BACKGROUND = QColor("#ffffff")  # Panel backgrounds
    ALTERNATE_ROW = QColor("#f9f9f9")  # Table alternate rows

    # Interactive Colors
    HOVER = QColor("#e3f2fd")  # Light blue hover state
    SELECTED = QColor("#e6f7ff")  # Selection background (from mockup)
    BORDER = QColor("#ddd")  # Default border color

    # Status Colors
    SUCCESS = QColor("#2ecc71")  # Green
    WARNING = QColor("#f1c40f")  # Yellow
    ERROR = QColor("#e74c3c")  # Red
    INFO = PRIMARY  # Blue

    # File Type Colors (updated to match theme)
    FILE_COLORS: ClassVar = {
        "EXE": QColor("#3498db"),  # Primary blue
        "DLL": QColor("#2ecc71"),  # Green
        "PDF": QColor("#e74c3c"),  # Red
        "DOC": QColor("#9b59b6"),  # Purple
        "DOCX": QColor("#9b59b6"),  # Purple
        "XLS": QColor("#27ae60"),  # Dark green
        "XLSX": QColor("#27ae60"),  # Dark green
        "JPG": QColor("#f39c12"),  # Orange
        "JPEG": QColor("#f39c12"),  # Orange
        "PNG": QColor("#e67e22"),  # Dark orange
        "TXT": QColor("#95a5a6"),  # Gray
        "ZIP": QColor("#34495e"),  # Dark blue-gray
        "RAR": QColor("#34495e"),  # Dark blue-gray
        "MP3": QColor("#8e44ad"),  # Purple
        "MP4": QColor("#2980b9"),  # Dark blue
        "OTHER": QColor("#bdc3c7"),  # Light gray
    }


class Spacing:
    """Consistent spacing values based on 8px grid system."""

    XS = 4  # Extra small spacing
    SM = 8  # Small spacing
    MD = 16  # Medium spacing
    LG = 24  # Large spacing
    XL = 32  # Extra large spacing
    XXL = 48  # Extra extra large spacing


class Typography:
    """Typography constants for consistent text styling."""

    # Font Families
    MAIN_FONT = "Arial, sans-serif"
    MONO_FONT = "Consolas, Monaco, monospace"

    # Font Sizes
    FONT_XS = "10px"
    FONT_SM = "12px"
    FONT_MD = "14px"
    FONT_LG = "16px"
    FONT_XL = "18px"
    FONT_XXL = "24px"

    # Font Weights
    WEIGHT_NORMAL = "normal"
    WEIGHT_MEDIUM = "500"
    WEIGHT_BOLD = "bold"


class BorderRadius:
    """Border radius values for consistent rounded corners."""

    NONE = "0px"
    SM = "3px"  # Small radius for buttons
    MD = "5px"  # Medium radius for panels
    LG = "8px"  # Large radius for cards
    ROUND = "50%"  # Full round for circular elements


class Shadows:
    """Box shadow definitions for depth."""

    NONE = "none"
    SM = "0 1px 3px rgba(0, 0, 0, 0.1)"
    MD = "0 2px 6px rgba(0, 0, 0, 0.15)"
    LG = "0 4px 12px rgba(0, 0, 0, 0.2)"
