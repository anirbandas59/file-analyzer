#!/usr/bin/env python3
# File: src/ui/themes/styles.py


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
    MEDIUM_GRAY = QColor("#dee2e6")  # Borders and dividers
    DARK_GRAY = QColor("#495057")  # Secondary text (darker for better contrast)
    VERY_DARK_GRAY = QColor("#212529")  # Primary text (darker for better contrast)

    # Background Colors
    BACKGROUND = QColor("#f5f5f5")  # Main background (from mockup)
    PANEL_BACKGROUND = QColor("#ffffff")  # Panel backgrounds
    ALTERNATE_ROW = QColor("#f9f9f9")  # Table alternate rows

    # File Table Colors (matching screenshots)
    FILE_ROW_BACKGROUND = QColor("#2c3e50")  # Dark navy blue for file rows
    FILE_ROW_TEXT = QColor("#ffffff")  # White text on dark background
    FILE_ROW_HOVER = QColor("#34495e")  # Slightly lighter for hover
    FILE_ROW_SELECTED = QColor("#3498db")  # Primary blue for selection

    # Interactive Colors
    HOVER = QColor("#e3f2fd")  # Light blue hover state
    SELECTED = QColor("#e6f7ff")  # Selection background (from mockup)
    BORDER = QColor("#ddd")  # Default border color

    # Status Colors
    SUCCESS = QColor("#2ecc71")  # Green
    WARNING = QColor("#f1c40f")  # Yellow
    ERROR = QColor("#e74c3c")  # Red
    INFO = PRIMARY  # Blue


class DarkTheme:
    """
    Dark theme variant for the File Analyzer application.
    Maintains the same blue accent while inverting backgrounds.
    """

    # Primary Colors (same blue accent)
    PRIMARY = QColor("#3498db")  # Main accent blue
    PRIMARY_DARK = QColor("#2980b9")  # Darker blue for hover states
    PRIMARY_LIGHT = QColor("#5dade2")  # Lighter blue for backgrounds

    # Neutral Colors (inverted)
    WHITE = QColor("#ffffff")
    LIGHT_GRAY = QColor("#3c4043")  # Dark panel backgrounds
    MEDIUM_GRAY = QColor("#5f6368")  # Dark borders and dividers
    DARK_GRAY = QColor("#9aa0a6")  # Medium secondary text for better contrast
    VERY_DARK_GRAY = QColor("#e8eaed")  # Light primary text with better contrast

    # Background Colors (dark variants)
    BACKGROUND = QColor("#202124")  # Dark main background
    PANEL_BACKGROUND = QColor("#2d2e30")  # Dark panel backgrounds
    ALTERNATE_ROW = QColor("#35363a")  # Dark table alternate rows

    # File Table Colors (enhanced for dark theme)
    FILE_ROW_BACKGROUND = QColor("#35363a")  # Dark gray for file rows
    FILE_ROW_TEXT = QColor("#e8eaed")  # Light text on dark background
    FILE_ROW_HOVER = QColor("#42464a")  # Lighter gray for hover
    FILE_ROW_SELECTED = QColor("#3498db")  # Primary blue for selection

    # Interactive Colors (dark variants)
    HOVER = QColor("#42464a")  # Dark hover state
    SELECTED = QColor("#1a73e8")  # Dark blue selection
    BORDER = QColor("#5f6368")  # Dark border color

    # Status Colors (same for consistency)
    SUCCESS = QColor("#2ecc71")  # Green
    WARNING = QColor("#f1c40f")  # Yellow
    ERROR = QColor("#e74c3c")  # Red
    INFO = PRIMARY  # Blue


# Shared File Type Colors (used by both light and dark themes)
FILE_COLORS: dict = {
        "EXE": QColor("#3498db"),  # Primary blue (matching main theme)
        "DLL": QColor("#2ecc71"),  # Emerald green
        "PDF": QColor("#e74c3c"),  # Alizarin red
        "DOC": QColor("#9b59b6"),  # Amethyst purple
        "DOCX": QColor("#8e44ad"),  # Wisteria purple (darker variant)
        "XLS": QColor("#27ae60"),  # Nephritis green
        "XLSX": QColor("#16a085"),  # Green sea (darker variant)
        "JPG": QColor("#f39c12"),  # Orange
        "JPEG": QColor("#e67e22"),  # Carrot orange (darker variant)
        "PNG": QColor("#d35400"),  # Pumpkin orange (even darker)
        "GIF": QColor("#f1c40f"),  # Sun flower yellow
        "TXT": QColor("#95a5a6"),  # Concrete gray
        "LOG": QColor("#7f8c8d"),  # Asbestos gray (darker)
        "DAT": QColor("#34495e"),  # Wet asphalt blue-gray
        "ZIP": QColor("#2c3e50"),  # Midnight blue
        "RAR": QColor("#2c3e50"),  # Midnight blue
        "7Z": QColor("#2c3e50"),   # Midnight blue
        "MP3": QColor("#8e44ad"),  # Wisteria purple
        "MP4": QColor("#2980b9"),  # Belize hole blue
        "AVI": QColor("#3498db"),  # Peter river blue
        "JSON": QColor("#1abc9c"), # Turquoise
        "XML": QColor("#16a085"),  # Green sea
        "YML": QColor("#27ae60"),  # Nephritis
        "YAML": QColor("#2ecc71"), # Emerald
        "CONFIG": QColor("#f39c12"), # Orange
        "BLF": QColor("#e67e22"),  # Carrot
        "REGTRANS-MS": QColor("#d35400"), # Pumpkin
        "OTHER": QColor("#bdc3c7"),  # Silver gray
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
    MAIN_FONT = "Roboto, 'Segoe UI', Arial, sans-serif"
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
