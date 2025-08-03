"""
Comprehensive Design System for File Analyzer Application

This module defines the complete design system including:
- Color palettes for light and dark themes
- Typography system
- Component specifications
- Icon definitions
- Spacing and layout constants
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar

from PyQt6.QtGui import QColor


class ColorRole(Enum):
    """Semantic color roles for consistent theming"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

    # Surface colors
    BACKGROUND = "background"
    SURFACE = "surface"
    SURFACE_VARIANT = "surface_variant"
    SURFACE_CONTAINER = "surface_container"

    # Text colors
    TEXT_PRIMARY = "text_primary"
    TEXT_SECONDARY = "text_secondary"
    TEXT_TERTIARY = "text_tertiary"
    TEXT_INVERSE = "text_inverse"

    # Border and outline
    BORDER = "border"
    BORDER_VARIANT = "border_variant"
    OUTLINE = "outline"

    # Interactive states
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"
    FOCUS = "focus"


@dataclass
class ColorPalette:
    """Complete color palette for a theme"""
    # Primary colors
    primary: QColor
    primary_variant: QColor
    primary_hover: QColor
    primary_pressed: QColor

    # Secondary colors
    secondary: QColor
    secondary_variant: QColor
    secondary_hover: QColor
    secondary_pressed: QColor

    # Accent color
    accent: QColor
    accent_hover: QColor
    accent_pressed: QColor

    # Semantic colors
    success: QColor
    warning: QColor
    error: QColor
    info: QColor

    # Background and surface
    background: QColor
    surface: QColor
    surface_variant: QColor
    surface_container: QColor
    surface_hover: QColor

    # Text colors
    text_primary: QColor
    text_secondary: QColor
    text_tertiary: QColor
    text_inverse: QColor
    text_disabled: QColor

    # Border and outline
    border: QColor
    border_variant: QColor
    outline: QColor
    outline_variant: QColor

    # Interactive states
    hover_overlay: QColor
    pressed_overlay: QColor
    disabled_overlay: QColor
    focus_ring: QColor

    # Chart specific colors
    chart_primary: QColor
    chart_secondary: QColor
    chart_tertiary: QColor
    chart_quaternary: QColor
    chart_background: QColor
    chart_grid: QColor
    chart_legend: QColor


class LightThemePalette:
    """Light theme color palette following Material Design 3 principles"""

    @staticmethod
    def get_palette() -> ColorPalette:
        return ColorPalette(
            # Primary colors - Blue based
            primary=QColor(25, 118, 210),  # #1976D2
            primary_variant=QColor(21, 101, 192),  # #1565C0
            primary_hover=QColor(30, 136, 229),  # #1E88E5
            primary_pressed=QColor(13, 71, 161),  # #0D47A1

            # Secondary colors - Teal based
            secondary=QColor(0, 150, 136),  # #009688
            secondary_variant=QColor(0, 121, 107),  # #00796B
            secondary_hover=QColor(26, 175, 162),  # #1AAFA2
            secondary_pressed=QColor(0, 105, 92),  # #00695C

            # Accent color - Orange
            accent=QColor(255, 152, 0),  # #FF9800
            accent_hover=QColor(255, 167, 38),  # #FFA726
            accent_pressed=QColor(245, 124, 0),  # #F57C00

            # Semantic colors
            success=QColor(76, 175, 80),  # #4CAF50
            warning=QColor(255, 193, 7),  # #FFC107
            error=QColor(244, 67, 54),  # #F44336
            info=QColor(33, 150, 243),  # #2196F3

            # Background and surface
            background=QColor(250, 250, 250),  # #FAFAFA
            surface=QColor(255, 255, 255),  # #FFFFFF
            surface_variant=QColor(245, 245, 245),  # #F5F5F5
            surface_container=QColor(240, 240, 240),  # #F0F0F0
            surface_hover=QColor(235, 235, 235),  # #EBEBEB

            # Text colors
            text_primary=QColor(33, 33, 33),  # #212121
            text_secondary=QColor(97, 97, 97),  # #616161
            text_tertiary=QColor(158, 158, 158),  # #9E9E9E
            text_inverse=QColor(255, 255, 255),  # #FFFFFF
            text_disabled=QColor(189, 189, 189),  # #BDBDBD

            # Border and outline
            border=QColor(224, 224, 224),  # #E0E0E0
            border_variant=QColor(238, 238, 238),  # #EEEEEE
            outline=QColor(189, 189, 189),  # #BDBDBD
            outline_variant=QColor(204, 204, 204),  # #CCCCCC

            # Interactive states
            hover_overlay=QColor(0, 0, 0, 8),  # 3% black overlay
            pressed_overlay=QColor(0, 0, 0, 12),  # 5% black overlay
            disabled_overlay=QColor(255, 255, 255, 61),  # 24% white overlay
            focus_ring=QColor(25, 118, 210, 64),  # 25% primary

            # Chart specific colors
            chart_primary=QColor(25, 118, 210),  # #1976D2
            chart_secondary=QColor(0, 150, 136),  # #009688
            chart_tertiary=QColor(255, 152, 0),  # #FF9800
            chart_quaternary=QColor(156, 39, 176),  # #9C27B0
            chart_background=QColor(255, 255, 255),  # #FFFFFF
            chart_grid=QColor(224, 224, 224),  # #E0E0E0
            chart_legend=QColor(97, 97, 97),  # #616161
        )


class DarkThemePalette:
    """Dark theme color palette following Material Design 3 principles"""

    @staticmethod
    def get_palette() -> ColorPalette:
        return ColorPalette(
            # Primary colors - Lighter blue for dark theme
            primary=QColor(100, 181, 246),  # #64B5F6
            primary_variant=QColor(66, 165, 245),  # #42A5F5
            primary_hover=QColor(129, 199, 249),  # #81C7F9
            primary_pressed=QColor(33, 150, 243),  # #2196F3

            # Secondary colors - Lighter teal
            secondary=QColor(77, 182, 172),  # #4DB6AC
            secondary_variant=QColor(38, 166, 154),  # #26A69A
            secondary_hover=QColor(102, 187, 179),  # #66BBB3
            secondary_pressed=QColor(0, 150, 136),  # #009688

            # Accent color - Lighter orange
            accent=QColor(255, 183, 77),  # #FFB74D
            accent_hover=QColor(255, 204, 128),  # #FFCC80
            accent_pressed=QColor(255, 152, 0),  # #FF9800

            # Semantic colors
            success=QColor(129, 199, 132),  # #81C784
            warning=QColor(255, 213, 79),  # #FFD54F
            error=QColor(239, 154, 154),  # #EF9A9A
            info=QColor(100, 181, 246),  # #64B5F6

            # Background and surface
            background=QColor(18, 18, 18),  # #121212
            surface=QColor(30, 30, 30),  # #1E1E1E
            surface_variant=QColor(40, 40, 40),  # #282828
            surface_container=QColor(50, 50, 50),  # #323232
            surface_hover=QColor(60, 60, 60),  # #3C3C3C

            # Text colors
            text_primary=QColor(255, 255, 255),  # #FFFFFF
            text_secondary=QColor(224, 224, 224),  # #E0E0E0
            text_tertiary=QColor(189, 189, 189),  # #BDBDBD
            text_inverse=QColor(33, 33, 33),  # #212121
            text_disabled=QColor(97, 97, 97),  # #616161

            # Border and outline
            border=QColor(66, 66, 66),  # #424242
            border_variant=QColor(82, 82, 82),  # #525252
            outline=QColor(117, 117, 117),  # #757575
            outline_variant=QColor(97, 97, 97),  # #616161

            # Interactive states
            hover_overlay=QColor(255, 255, 255, 8),  # 3% white overlay
            pressed_overlay=QColor(255, 255, 255, 12),  # 5% white overlay
            disabled_overlay=QColor(0, 0, 0, 61),  # 24% black overlay
            focus_ring=QColor(100, 181, 246, 64),  # 25% primary

            # Chart specific colors
            chart_primary=QColor(100, 181, 246),  # #64B5F6
            chart_secondary=QColor(77, 182, 172),  # #4DB6AC
            chart_tertiary=QColor(255, 183, 77),  # #FFB74D
            chart_quaternary=QColor(186, 104, 200),  # #BA68C8
            chart_background=QColor(30, 30, 30),  # #1E1E1E
            chart_grid=QColor(66, 66, 66),  # #424242
            chart_legend=QColor(224, 224, 224),  # #E0E0E0
        )


@dataclass
class Typography:
    """Typography system with semantic naming"""
    # Font families - Modern cross-platform font stacks optimized for readability and performance
    FONT_FAMILY_PRIMARY = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'Roboto', 'Ubuntu', 'Cantarell', 'Oxygen', 'Fira Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
    FONT_FAMILY_MONOSPACE = "'SF Mono', 'Cascadia Code', 'JetBrains Mono', 'Fira Code', 'Source Code Pro', 'Monaco', 'Menlo', 'Ubuntu Mono', 'DejaVu Sans Mono', 'Consolas', 'Courier New', monospace"

    # Font sizes (in pt)
    FONT_XXS = 10
    FONT_XS = 11
    FONT_SM = 12
    FONT_BASE = 14
    FONT_LG = 16
    FONT_XL = 18
    FONT_XXL = 24
    FONT_XXXL = 32

    # Font weights
    WEIGHT_LIGHT = 300
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700

    # Line heights
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.4
    LINE_HEIGHT_RELAXED = 1.6


@dataclass
class Spacing:
    """Spacing system using 8px base unit"""
    # Base unit
    BASE = 8

    # Spacing scale
    XS = BASE // 2  # 4px
    SM = BASE      # 8px
    MD = BASE * 2  # 16px
    LG = BASE * 3  # 24px
    XL = BASE * 4  # 32px
    XXL = BASE * 6  # 48px
    XXXL = BASE * 8  # 64px


@dataclass
class BorderRadius:
    """Border radius system"""
    NONE = 0
    SM = 4
    MD = 8
    LG = 12
    XL = 16
    FULL = 9999


@dataclass
class Elevation:
    """Elevation system for shadows and depth"""
    NONE = "none"
    SM = "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)"
    MD = "0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)"
    LG = "0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)"
    XL = "0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)"


class ComponentSpecs:
    """Component specifications for consistent styling"""

    @staticmethod
    def get_button_specs() -> dict[str, Any]:
        return {
            "primary": {
                "height": 36,
                "padding": f"{Spacing.SM}px {Spacing.MD}px",
                "border_radius": BorderRadius.MD,
                "font_size": Typography.FONT_BASE,
                "font_weight": Typography.WEIGHT_MEDIUM,
            },
            "secondary": {
                "height": 36,
                "padding": f"{Spacing.SM}px {Spacing.MD}px",
                "border_radius": BorderRadius.MD,
                "font_size": Typography.FONT_BASE,
                "font_weight": Typography.WEIGHT_NORMAL,
                "border_width": 1,
            },
            "icon": {
                "size": 32,
                "border_radius": BorderRadius.FULL,
                "padding": Spacing.SM,
            }
        }

    @staticmethod
    def get_card_specs() -> dict[str, Any]:
        return {
            "default": {
                "border_radius": BorderRadius.LG,
                "padding": Spacing.LG,
                "elevation": Elevation.SM,
                "border_width": 1,
            },
            "elevated": {
                "border_radius": BorderRadius.LG,
                "padding": Spacing.LG,
                "elevation": Elevation.MD,
                "border_width": 0,
            }
        }

    @staticmethod
    def get_input_specs() -> dict[str, Any]:
        return {
            "default": {
                "height": 40,
                "padding": f"{Spacing.SM}px {Spacing.MD}px",
                "border_radius": BorderRadius.MD,
                "border_width": 1,
                "font_size": Typography.FONT_BASE,
            },
            "large": {
                "height": 48,
                "padding": f"{Spacing.MD}px {Spacing.LG}px",
                "border_radius": BorderRadius.LG,
                "border_width": 1,
                "font_size": Typography.FONT_LG,
            }
        }


class IconSystem:
    """Icon system with theme-aware specifications"""

    # Icon sizes
    SIZE_XS = 12
    SIZE_SM = 16
    SIZE_MD = 20
    SIZE_LG = 24
    SIZE_XL = 32
    SIZE_XXL = 48

    # Icon mappings - now using SVG files from resource/icons/
    ICONS: ClassVar[dict[str, str]] = {
        "folder": "folder",
        "file": "file",
        "chart": "chart",
        "settings": "settings",
        "refresh": "refresh",
        "search": "search",
        "home": "home",
        "close": "close",
        "menu": "menu"
    }
