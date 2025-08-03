"""
Chart Theming Module

This module provides theme-aware chart styling for matplotlib and other charting libraries.
It ensures charts integrate seamlessly with the application's theme system.
"""

try:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    rc_params = None
from PyQt6.QtGui import QColor

from .design_system import Typography
from .theme_provider import theme_provider


class ChartThemeManager:
    """Manages chart theming across different chart libraries"""

    def __init__(self):
        self._matplotlib_configured = False
        theme_provider.theme_changed.connect(self._on_theme_changed)

    def configure_matplotlib(self):
        """Configure matplotlib with current theme"""
        if not MATPLOTLIB_AVAILABLE:
            return

        palette = theme_provider.current_palette

        # Convert QColors to hex strings
        bg_color = palette.chart_background.name()
        text_color = palette.chart_legend.name()
        grid_color = palette.chart_grid.name()

        # Chart colors
        chart_colors = [
            palette.chart_primary.name(),
            palette.chart_secondary.name(),
            palette.chart_tertiary.name(),
            palette.chart_quaternary.name(),
        ]

        # Configure matplotlib rcParams
        rcParams.update({
            # Figure and axes
            'figure.facecolor': bg_color,
            'figure.edgecolor': bg_color,
            'axes.facecolor': bg_color,
            'axes.edgecolor': text_color,
            'axes.linewidth': 1.0,

            # Text
            'text.color': text_color,
            'axes.labelcolor': text_color,
            'xtick.color': text_color,
            'ytick.color': text_color,

            # Grid
            'axes.grid': True,
            'grid.color': grid_color,
            'grid.linestyle': '-',
            'grid.linewidth': 0.5,
            'grid.alpha': 0.3,

            # Spines
            'axes.spines.left': True,
            'axes.spines.bottom': True,
            'axes.spines.top': False,
            'axes.spines.right': False,

            # Colors
            'axes.prop_cycle': plt.cycler('color', chart_colors),

            # Font
            'font.family': 'sans-serif',
            'font.sans-serif': ['Segoe UI', 'system-ui', 'DejaVu Sans'],
            'font.size': Typography.FONT_SM,

            # Legend
            'legend.facecolor': bg_color,
            'legend.edgecolor': text_color,
            'legend.framealpha': 0.9,
            'legend.fancybox': True,
            'legend.shadow': False,
        })

        self._matplotlib_configured = True

    def get_chart_style_config(self) -> dict:
        """Get chart styling configuration for custom charts"""
        palette = theme_provider.current_palette

        return {
            'background_color': palette.chart_background,
            'text_color': palette.chart_legend,
            'grid_color': palette.chart_grid,
            'colors': [
                palette.chart_primary,
                palette.chart_secondary,
                palette.chart_tertiary,
                palette.chart_quaternary,
            ],
            'border_color': palette.border,
            'font_family': Typography.FONT_FAMILY_PRIMARY,
            'font_size': Typography.FONT_SM,
        }

    def style_pie_chart(self, colors: list[str] | None = None) -> dict:
        """Get styling for pie charts"""
        palette = theme_provider.current_palette

        if colors is None:
            colors = [
                palette.chart_primary.name(),
                palette.chart_secondary.name(),
                palette.chart_tertiary.name(),
                palette.chart_quaternary.name(),
            ]

        return {
            'colors': colors,
            'explode': (0.05, 0.05, 0.05, 0.05),  # Slight separation
            'autopct': '%1.1f%%',
            'startangle': 90,
            'textprops': {
                'color': palette.chart_legend.name(),
                'fontsize': Typography.FONT_SM,
                'fontfamily': Typography.FONT_FAMILY_PRIMARY.split(',')[0]
            },
            'wedgeprops': {
                'edgecolor': palette.chart_background.name(),
                'linewidth': 2
            }
        }

    def style_bar_chart(self) -> dict:
        """Get styling for bar charts"""
        palette = theme_provider.current_palette

        return {
            'color': palette.chart_primary.name(),
            'edgecolor': palette.chart_background.name(),
            'linewidth': 1,
            'alpha': 0.8,
            'grid': True,
            'grid_alpha': 0.3,
            'grid_color': palette.chart_grid.name(),
        }

    def style_line_chart(self) -> dict:
        """Get styling for line charts"""
        palette = theme_provider.current_palette

        return {
            'colors': [
                palette.chart_primary.name(),
                palette.chart_secondary.name(),
                palette.chart_tertiary.name(),
                palette.chart_quaternary.name(),
            ],
            'linewidth': 2,
            'marker': 'o',
            'markersize': 4,
            'grid': True,
            'grid_alpha': 0.3,
            'grid_color': palette.chart_grid.name(),
        }

    def get_contrasting_text_color(self, background_color: QColor) -> QColor:
        """Get contrasting text color for given background"""
        # Calculate luminance
        r, g, b = background_color.red(), background_color.green(), background_color.blue()
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

        # Return light or dark text based on background luminance
        if luminance > 0.5:
            return QColor(33, 33, 33)  # Dark text
        else:
            return QColor(255, 255, 255)  # Light text

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        if self._matplotlib_configured:
            self.configure_matplotlib()


class PyQtChartStyler:
    """Styler for PyQt charts (if using QtCharts)"""

    def __init__(self):
        self.theme_manager = chart_theme_manager

    def style_chart_series(self, series, color_index: int = 0):
        """Style a chart series with theme colors"""
        config = self.theme_manager.get_chart_style_config()
        colors = config['colors']

        if hasattr(series, 'setColor'):
            color = colors[color_index % len(colors)]
            series.setColor(color)

    def style_chart_background(self, chart):
        """Style chart background"""
        config = self.theme_manager.get_chart_style_config()

        if hasattr(chart, 'setBackgroundBrush'):
            chart.setBackgroundBrush(config['background_color'])

        if hasattr(chart, 'setPlotAreaBackgroundBrush'):
            chart.setPlotAreaBackgroundBrush(config['background_color'])


class MatplotlibIntegration:
    """Integration helpers for matplotlib in PyQt applications"""

    @staticmethod
    def create_themed_figure(figsize: tuple[float, float] = (8, 6)):
        """Create a matplotlib figure with current theme"""
        if not MATPLOTLIB_AVAILABLE:
            return None, None

        chart_theme_manager.configure_matplotlib()

        fig, ax = plt.subplots(figsize=figsize)

        # Apply additional theming
        palette = theme_provider.current_palette

        # Set face colors
        fig.patch.set_facecolor(palette.chart_background.name())
        ax.set_facecolor(palette.chart_background.name())

        # Style spines
        for spine in ax.spines.values():
            spine.set_color(palette.text_secondary.name())
            spine.set_linewidth(0.8)

        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Style ticks
        ax.tick_params(colors=palette.chart_legend.name(), which='both')

        return fig, ax

    @staticmethod
    def save_themed_figure(fig, filename: str, **kwargs):
        """Save figure with theme-appropriate settings"""
        if not MATPLOTLIB_AVAILABLE or fig is None:
            return

        palette = theme_provider.current_palette

        default_kwargs = {
            'facecolor': palette.chart_background.name(),
            'edgecolor': 'none',
            'bbox_inches': 'tight',
            'dpi': 150,
            'transparent': False
        }

        # Update with user provided kwargs
        default_kwargs.update(kwargs)

        fig.savefig(filename, **default_kwargs)


# Global instance
chart_theme_manager = ChartThemeManager()


def apply_chart_theme():
    """Convenience function to apply chart theme"""
    chart_theme_manager.configure_matplotlib()


def get_chart_colors() -> list[str]:
    """Get current theme chart colors as hex strings"""
    config = chart_theme_manager.get_chart_style_config()
    return [color.name() for color in config['colors']]


def get_chart_background_color() -> str:
    """Get current theme chart background color as hex string"""
    config = chart_theme_manager.get_chart_style_config()
    return config['background_color'].name()


def get_chart_text_color() -> str:
    """Get current theme chart text color as hex string"""
    config = chart_theme_manager.get_chart_style_config()
    return config['text_color'].name()
