"""
Modern Theme Provider Architecture

This module provides a comprehensive theme management system that:
- Uses the design system for consistent styling
- Generates CSS stylesheets dynamically
- Provides theme-aware component styling
- Supports runtime theme switching
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication

from .design_system import (
    BorderRadius,
    ColorPalette,
    ComponentSpecs,
    DarkThemePalette,
    LightThemePalette,
    Spacing,
    Typography,
)


class ThemeProvider(QObject):
    """Central theme provider that manages theme state and generates styles"""

    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._current_theme = "light"
        self._palettes = {
            "light": LightThemePalette.get_palette(),
            "dark": DarkThemePalette.get_palette()
        }
        self._style_cache: dict[str, str] = {}

    @property
    def current_theme(self) -> str:
        return self._current_theme

    @property
    def current_palette(self) -> ColorPalette:
        return self._palettes[self._current_theme]

    def set_theme(self, theme_name: str) -> None:
        """Switch to a different theme"""
        if theme_name in self._palettes and theme_name != self._current_theme:
            self._current_theme = theme_name
            self._style_cache.clear()  # Clear cache when theme changes
            self.theme_changed.emit(theme_name)

    def get_color(self, role: str) -> QColor:
        """Get a color by role name from current palette"""
        return getattr(self.current_palette, role)

    def apply_theme_to_app(self) -> None:
        """Apply the current theme to the entire application"""
        try:
            app = QApplication.instance()
            if app:
                stylesheet = self.generate_global_stylesheet()
                app.setStyleSheet(stylesheet)
        except Exception:
            # Silently fail in test environments or if no app instance
            pass


class StylesheetGenerator:
    """Generates CSS stylesheets from the design system"""

    def __init__(self, theme_provider: ThemeProvider):
        self.theme_provider = theme_provider

    def generate_global_stylesheet(self) -> str:
        """Generate the complete global stylesheet"""
        palette = self.theme_provider.current_palette

        styles = []

        # Base application styles
        styles.append(self._generate_base_styles(palette))

        # Component styles
        styles.append(self._generate_button_styles(palette))
        styles.append(self._generate_card_styles(palette))
        styles.append(self._generate_input_styles(palette))
        styles.append(self._generate_label_styles(palette))
        styles.append(self._generate_layout_styles(palette))
        styles.append(self._generate_chart_styles(palette))

        return "\n\n".join(styles)

    def _generate_base_styles(self, palette: ColorPalette) -> str:
        """Generate base application styles"""
        return f"""
            /* Base Application Styles */
            QMainWindow, QWidget {{
                background-color: {palette.background.name()};
                color: {palette.text_primary.name()};
                font-family: "{Typography.FONT_FAMILY_PRIMARY}";
                font-size: {Typography.FONT_BASE}pt;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {palette.border.name()};
                background-color: {palette.surface.name()};
                border-radius: {BorderRadius.MD}px;
            }}
            
            QTabBar::tab {{
                background-color: {palette.surface_variant.name()};
                color: {palette.text_secondary.name()};
                padding: {Spacing.SM}px {Spacing.MD}px;
                margin-right: 2px;
                border-top-left-radius: {BorderRadius.MD}px;
                border-top-right-radius: {BorderRadius.MD}px;
                border: 1px solid {palette.border.name()};
                border-bottom: none;
            }}
            
            QTabBar::tab:selected {{
                background-color: {palette.surface.name()};
                color: {palette.text_primary.name()};
                border-color: {palette.primary.name()};
                border-bottom: 2px solid {palette.primary.name()};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {palette.surface_hover.name()};
                color: {palette.text_primary.name()};
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background-color: {palette.surface_variant.name()};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {palette.outline.name()};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {palette.text_secondary.name()};
            }}
            """

    def _generate_button_styles(self, palette: ColorPalette) -> str:
        """Generate button component styles"""
        button_specs = ComponentSpecs.get_button_specs()

        return f"""
            /* Button Styles */
            QPushButton {{
                border: none;
                border-radius: {button_specs['primary']['border_radius']}px;
                padding: {button_specs['primary']['padding']};
                font-size: {button_specs['primary']['font_size']}pt;
                font-weight: {button_specs['primary']['font_weight']};
                min-height: {button_specs['primary']['height']}px;
            }}
            
            QPushButton[class="primary"] {{
                background-color: {palette.primary.name()};
                color: {palette.text_inverse.name()};
            }}
            
            QPushButton[class="primary"]:hover {{
                background-color: {palette.primary_hover.name()};
            }}
            
            QPushButton[class="primary"]:pressed {{
                background-color: {palette.primary_pressed.name()};
            }}
            
            QPushButton[class="secondary"] {{
                background-color: transparent;
                color: {palette.primary.name()};
                border: {button_specs['secondary']['border_width']}px solid {palette.primary.name()};
            }}
            
            QPushButton[class="secondary"]:hover {{
                background-color: {palette.primary.name()};
                color: {palette.text_inverse.name()};
            }}
            
            QPushButton[class="ghost"] {{
                background-color: transparent;
                color: {palette.text_primary.name()};
                border: none;
            }}
            
            QPushButton[class="ghost"]:hover {{
                background-color: {palette.surface_hover.name()};
            }}
            
            QPushButton:disabled {{
                background-color: {palette.surface_variant.name()};
                color: {palette.text_disabled.name()};
                border: none;
            }}
            """

    def _generate_card_styles(self, palette: ColorPalette) -> str:
        """Generate card component styles"""
        card_specs = ComponentSpecs.get_card_specs()

        return f"""
            /* Card Styles */
            QFrame[class="card"] {{
                background-color: {palette.surface.name()};
                border: 1px solid {palette.border.name()};
                border-radius: {card_specs['default']['border_radius']}px;
                padding: {card_specs['default']['padding']}px;
            }}
            
            QFrame[class="card-elevated"] {{
                background-color: {palette.surface.name()};
                border: none;
                border-radius: {card_specs['elevated']['border_radius']}px;
                padding: {card_specs['elevated']['padding']}px;
            }}
            
            QFrame[class="stats-card"] {{
                background-color: {palette.surface.name()};
                border: 1px solid {palette.border.name()};
                border-radius: {BorderRadius.LG}px;
                padding: {Spacing.LG}px;
                margin: {Spacing.SM}px;
            }}
            
            QFrame[class="stats-card"]:hover {{
                border-color: {palette.primary.name()};
                background-color: {palette.surface_hover.name()};
            }}
            """

    def _generate_input_styles(self, palette: ColorPalette) -> str:
        """Generate input component styles"""
        input_specs = ComponentSpecs.get_input_specs()

        return f"""
            /* Input Styles */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {palette.surface.name()};
                border: 1px solid {palette.border.name()};
                border-radius: {input_specs['default']['border_radius']}px;
                padding: {input_specs['default']['padding']};
                color: {palette.text_primary.name()};
                font-size: {input_specs['default']['font_size']}pt;
                min-height: {input_specs['default']['height']}px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {palette.primary.name()};
                outline: 2px solid {palette.focus_ring.name()};
            }}
            
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                background-color: {palette.surface_variant.name()};
                color: {palette.text_disabled.name()};
                border-color: {palette.border_variant.name()};
            }}
            
            QComboBox {{
                background-color: {palette.surface.name()};
                border: 1px solid {palette.border.name()};
                border-radius: {input_specs['default']['border_radius']}px;
                padding: {Spacing.SM}px {Spacing.MD}px;
                color: {palette.text_primary.name()};
                min-height: {input_specs['default']['height']}px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {palette.text_secondary.name()};
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {palette.surface.name()};
                border: 1px solid {palette.border.name()};
                border-radius: {BorderRadius.MD}px;
                selection-background-color: {palette.primary.name()};
                selection-color: {palette.text_inverse.name()};
            }}
            """

    def _generate_label_styles(self, palette: ColorPalette) -> str:
        """Generate label and text styles"""
        return f"""
            /* Label and Text Styles */
            QLabel[class="title"] {{
                color: {palette.text_primary.name()};
                font-size: {Typography.FONT_XL}pt;
                font-weight: {Typography.WEIGHT_BOLD};
                margin: {Spacing.MD}px 0px;
            }}
            
            QLabel[class="subtitle"] {{
                color: {palette.text_secondary.name()};
                font-size: {Typography.FONT_LG}pt;
                font-weight: {Typography.WEIGHT_MEDIUM};
                margin: {Spacing.SM}px 0px;
            }}
            
            QLabel[class="heading"] {{
                color: {palette.text_primary.name()};
                font-size: {Typography.FONT_LG}pt;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                margin: {Spacing.SM}px 0px;
            }}
            
            QLabel[class="body"] {{
                color: {palette.text_primary.name()};
                font-size: {Typography.FONT_BASE}pt;
                font-weight: {Typography.WEIGHT_NORMAL};
                line-height: {Typography.LINE_HEIGHT_NORMAL};
            }}
            
            QLabel[class="caption"] {{
                color: {palette.text_secondary.name()};
                font-size: {Typography.FONT_SM}pt;
                font-weight: {Typography.WEIGHT_NORMAL};
            }}
            
            QLabel[class="muted"] {{
                color: {palette.text_tertiary.name()};
                font-size: {Typography.FONT_SM}pt;
            }}
            
            QLabel#stats_value {{
                color: {palette.primary.name()};
                font-size: {Typography.FONT_XXL}pt;
                font-weight: {Typography.WEIGHT_BOLD};
                background-color: transparent;
            }}
            
            QLabel#stats_label {{
                color: {palette.text_secondary.name()};
                font-size: {Typography.FONT_SM}pt;
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}
            """

    def _generate_layout_styles(self, palette: ColorPalette) -> str:
        """Generate layout and container styles"""
        return f"""
            /* Layout and Container Styles */
            QSplitter::handle {{
                background-color: {palette.border.name()};
            }}
            
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            
            QSplitter::handle:vertical {{
                height: 2px;
            }}
            
            QGroupBox {{
                font-weight: {Typography.WEIGHT_MEDIUM};
                border: 1px solid {palette.border.name()};
                border-radius: {BorderRadius.MD}px;
                margin-top: {Spacing.MD}px;
                padding-top: {Spacing.SM}px;
                background-color: {palette.surface.name()};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Spacing.MD}px;
                padding: 0 {Spacing.SM}px 0 {Spacing.SM}px;
                color: {palette.text_primary.name()};
                background-color: {palette.surface.name()};
            }}
            
            QProgressBar {{
                border: 1px solid {palette.border.name()};
                border-radius: {BorderRadius.SM}px;
                text-align: center;
                background-color: {palette.surface_variant.name()};
                color: {palette.text_primary.name()};
            }}
            
            QProgressBar::chunk {{
                background-color: {palette.primary.name()};
                border-radius: {BorderRadius.SM}px;
            }}
            """

    def _generate_chart_styles(self, palette: ColorPalette) -> str:
        """Generate chart-specific styles"""
        return f"""
            /* Chart Styles */
            QFrame[class="chart-container"] {{
                background-color: {palette.chart_background.name()};
                border: 1px solid {palette.border.name()};
                border-radius: {BorderRadius.LG}px;
                padding: {Spacing.LG}px;
            }}
            
            QLabel[class="chart-title"] {{
                color: {palette.text_primary.name()};
                font-size: {Typography.FONT_LG}pt;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                margin-bottom: {Spacing.MD}px;
            }}
            
            QLabel[class="chart-legend"] {{
                color: {palette.chart_legend.name()};
                font-size: {Typography.FONT_SM}pt;
                background-color: transparent;
            }}
            
            QFrame[class="chart-legend-item"] {{
                background-color: transparent;
                border: none;
                padding: {Spacing.XS}px;
            }}
            """


# Global theme provider instance
theme_provider = ThemeProvider()
stylesheet_generator = StylesheetGenerator(theme_provider)

# Extend ThemeProvider with stylesheet generation
def generate_global_stylesheet(self) -> str:
    return stylesheet_generator.generate_global_stylesheet()

ThemeProvider.generate_global_stylesheet = generate_global_stylesheet
