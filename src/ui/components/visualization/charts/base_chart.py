#!/usr/bin/env python3
# File: src/ui/components/visualization/charts/base_chart.py

from abc import abstractmethod
from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ....themes.styles import ModernTheme, Typography
from ...card_widget import CardWidget
from ...modern_button import ModernButton
from ..models.chart_data import ChartMetadata


class BaseChart(CardWidget):
    """
    Abstract base class for all chart widgets.
    Provides common functionality like theming, export, and event handling.
    """

    # Signals
    item_clicked = pyqtSignal(str, dict)  # item_id, data
    export_requested = pyqtSignal(str)  # chart_type

    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(parent)

        self.chart_title = title
        self.chart_data = None
        self.metadata = None

        # Setup the widget
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Setup the basic UI structure."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(8)

        # Header with title and export button
        self.setup_header()

        # Chart content area
        self.chart_widget = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_widget)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.chart_widget, 1)  # Stretch to fill

        # Setup the actual chart content (implemented by subclasses)
        self.setup_chart()

    def setup_header(self):
        """Setup the chart header with title and controls."""
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        self.title_label = QLabel(self.chart_title)
        self.title_label.setStyleSheet(f"""
        QLabel {{
            font-size: {Typography.FONT_LG};
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            border: none;
            background: transparent;
        }}
        """)

        # Export button
        self.export_button = ModernButton("Export", "secondary")
        self.export_button.setMaximumWidth(80)
        self.export_button.clicked.connect(self.on_export_clicked)

        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.export_button)

        self.main_layout.addWidget(self.header_widget)

    @abstractmethod
    def setup_chart(self):
        """Setup the chart-specific content. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def update_data(self, data: Any, metadata: ChartMetadata | None = None):
        """Update the chart with new data. Must be implemented by subclasses."""
        pass

    def apply_theme(self):
        """Apply theme styling to the chart."""
        # Base theming is handled by CardWidget
        # Subclasses can override for chart-specific theming
        pass

    def set_title(self, title: str):
        """Update the chart title."""
        self.chart_title = title
        self.title_label.setText(title)

    def get_title(self) -> str:
        """Get the current chart title."""
        return self.chart_title

    def on_export_clicked(self):
        """Handle export button click."""
        self.export_requested.emit(self.get_chart_type())

    def export_as_image(
        self, file_path: str, width: int = 800, height: int = 600
    ) -> bool:
        """
        Export the chart as a PNG image.

        Args:
            file_path: Path where to save the image
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            True if export was successful
        """
        try:
            # Create a pixmap of the specified size
            pixmap = QPixmap(width, height)
            pixmap.fill(ModernTheme.WHITE)

            # Render the widget to the pixmap
            painter = QPainter(pixmap)
            self.render(painter)
            painter.end()

            # Save the pixmap
            return pixmap.save(file_path, "PNG")

        except Exception as e:
            print(f"Error exporting chart: {e}")
            return False

    @abstractmethod
    def get_chart_type(self) -> str:
        """Get the chart type identifier. Must be implemented by subclasses."""
        pass

    def get_data(self) -> Any:
        """Get the current chart data."""
        return self.chart_data

    def get_metadata(self) -> ChartMetadata | None:
        """Get the current chart metadata."""
        return self.metadata

    def show_no_data_message(self, message: str = "No data available"):
        """Show a message when there's no data to display."""
        # Clear existing chart content
        for i in reversed(range(self.chart_layout.count())):
            child = self.chart_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add no data label
        no_data_label = QLabel(message)
        no_data_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_MD};
            padding: 40px;
            text-align: center;
            border: none;
            background: transparent;
        }}
        """)
        no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.chart_layout.addWidget(no_data_label)

    def clear_chart(self):
        """Clear all chart content."""
        for i in reversed(range(self.chart_layout.count())):
            child = self.chart_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

    def emit_item_clicked(self, item_id: str, data: dict[str, Any]):
        """Emit the item clicked signal with data."""
        self.item_clicked.emit(item_id, data)


class InteractiveChart(BaseChart):
    """
    Base class for charts that support user interaction and drill-down.
    """

    # Additional signals for interactive charts
    drill_down_requested = pyqtSignal(str, dict)  # path, filter_data
    filter_requested = pyqtSignal(str, Any)  # filter_type, filter_value

    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(title, parent)

        # Track interaction state
        self.is_interactive = True
        self.hover_enabled = True

    def set_interactive(self, interactive: bool):
        """Enable or disable chart interactivity."""
        self.is_interactive = interactive

    def set_hover_enabled(self, enabled: bool):
        """Enable or disable hover effects."""
        self.hover_enabled = enabled

    def on_item_clicked(self, item_id: str, data: dict[str, Any]):
        """Handle item click events."""
        if not self.is_interactive:
            return

        # Emit the base signal
        self.emit_item_clicked(item_id, data)

        # Handle drill-down logic if applicable
        self.handle_drill_down(item_id, data)

    def handle_drill_down(self, item_id: str, data: dict[str, Any]):
        """Handle drill-down navigation. Can be overridden by subclasses."""
        # Default implementation: emit drill-down signal
        if "path" in data:
            self.drill_down_requested.emit(data["path"], data)
        elif "filter_type" in data:
            self.filter_requested.emit(data["filter_type"], data.get("filter_value"))

    @abstractmethod
    def get_item_at_position(self, x: int, y: int) -> dict[str, Any] | None:
        """Get the chart item at the specified position. Must be implemented by subclasses."""
        pass
