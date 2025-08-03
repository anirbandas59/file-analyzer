#!/usr/bin/env python3
# File: src/ui/components/visualization/dashboard.py

from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...themes.styles import ModernTheme, Spacing, Typography
from ..card_widget import CardWidget, StatsCard, TitleCard
from ..modern_button import ModernButton
from .charts import DirectoryTreeChart, FileAgeChart, FileTypePieChart, SizeDistributionChart
from .services.data_service import VisualizationDataService


class VisualizationDashboard(QWidget):
    """
    Main visualization dashboard that contains multiple chart widgets.
    Replaces the Charts tab placeholder in the main window.
    """

    # Signals
    drill_down_requested = pyqtSignal(str, dict)  # path, filter_data
    export_requested = pyqtSignal(str, str)  # chart_type, export_format

    def __init__(self, parent=None):
        super().__init__(parent)

        # Data service
        self.data_service = VisualizationDataService()

        # Chart widgets
        self.charts = {}

        # Setup UI
        self.setup_ui()

        # Connect signals
        self.setup_signals()

    def setup_ui(self):
        """Setup the dashboard UI."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD
        )
        self.main_layout.setSpacing(Spacing.MD)

        # Dashboard header
        self.setup_header()

        # Stats overview
        self.setup_stats_overview()

        # Charts area
        self.setup_charts_area()

    def setup_header(self):
        """Setup the dashboard header with title and controls."""
        self.header_card = CardWidget()
        header_layout = QHBoxLayout(self.header_card)

        # Title
        title_label = QLabel("Visualization Dashboard")
        title_label.setStyleSheet(f"""
        QLabel {{
            font-size: {Typography.FONT_XL};
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            border: none;
            background: transparent;
        }}
        """)

        # Export all button
        self.export_all_button = ModernButton("Export All", "secondary")
        self.export_all_button.clicked.connect(self.on_export_all_clicked)

        # Refresh button
        self.refresh_button = ModernButton("Refresh", "primary")
        self.refresh_button.clicked.connect(self.on_refresh_clicked)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.export_all_button)
        header_layout.addWidget(self.refresh_button)

        self.main_layout.addWidget(self.header_card)

    def setup_stats_overview(self):
        """Setup the statistics overview cards."""
        self.stats_layout = QHBoxLayout()

        # Total files card
        self.total_files_card = StatsCard("Total Files", "0")

        # Total size card
        self.total_size_card = StatsCard("Total Size", "0 B")

        # File types card
        self.file_types_card = StatsCard("File Types", "0")

        # Average file size card
        self.avg_size_card = StatsCard("Average Size", "0 B")

        self.stats_layout.addWidget(self.total_files_card)
        self.stats_layout.addWidget(self.total_size_card)
        self.stats_layout.addWidget(self.file_types_card)
        self.stats_layout.addWidget(self.avg_size_card)

        self.main_layout.addLayout(self.stats_layout)

    def setup_charts_area(self):
        """Setup the charts area with scroll support."""
        # Create scroll area for charts
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Charts container widget
        self.charts_widget = QWidget()
        self.charts_layout = QGridLayout(self.charts_widget)
        self.charts_layout.setSpacing(Spacing.MD)

        # Create initial charts
        self.create_charts()

        self.scroll_area.setWidget(self.charts_widget)
        self.main_layout.addWidget(self.scroll_area, 1)  # Stretch to fill

    def create_charts(self):
        """Create and layout the chart widgets."""
        # File type pie chart
        self.file_type_chart = FileTypePieChart()
        self.charts["file_type"] = self.file_type_chart
        self.charts_layout.addWidget(self.file_type_chart, 0, 0)

        # Directory structure chart
        self.directory_chart = DirectoryTreeChart()
        self.charts["directory_structure"] = self.directory_chart
        self.charts_layout.addWidget(self.directory_chart, 0, 1)

        # File size distribution chart
        self.size_chart = SizeDistributionChart()
        self.charts["size_distribution"] = self.size_chart
        self.charts_layout.addWidget(self.size_chart, 1, 0)

        # File age analysis chart
        self.age_chart = FileAgeChart()
        self.charts["file_age"] = self.age_chart
        self.charts_layout.addWidget(self.age_chart, 1, 1)


    def setup_signals(self):
        """Connect chart signals to dashboard handlers."""
        # Connect file type chart signals
        if hasattr(self, "file_type_chart"):
            self.file_type_chart.item_clicked.connect(self.on_chart_item_clicked)
            self.file_type_chart.export_requested.connect(
                self.on_chart_export_requested
            )

        # Connect directory chart signals
        if hasattr(self, "directory_chart"):
            self.directory_chart.item_clicked.connect(self.on_chart_item_clicked)
            self.directory_chart.export_requested.connect(
                self.on_chart_export_requested
            )
            self.directory_chart.drill_down_requested.connect(
                lambda path, data: self.drill_down_requested.emit(path, data)
            )

        # Connect size distribution chart signals
        if hasattr(self, "size_chart"):
            self.size_chart.export_requested.connect(self.on_chart_export_requested)

        # Connect file age chart signals
        if hasattr(self, "age_chart"):
            self.age_chart.export_requested.connect(self.on_chart_export_requested)

    def update_data(self, file_list: list[dict[str, Any]], directory_path: str = ""):
        """
        Update the dashboard with new file data.

        Args:
            file_list: List of file dictionaries from scanner
            directory_path: Path of the scanned directory
        """
        # Update data service
        self.data_service.update_data(file_list, directory_path)

        # Update statistics overview
        self.update_stats_overview()

        # Update charts
        self.update_charts()

    def update_stats_overview(self):
        """Update the statistics overview cards."""
        metadata = self.data_service.get_metadata()

        # Update cards with new values
        self.total_files_card.update_value(f"{metadata.total_files:,}")
        self.total_size_card.update_value(metadata.total_size_formatted)

        # Calculate unique file types
        file_type_data = self.data_service.get_file_type_data()
        unique_types = len(file_type_data)
        self.file_types_card.update_value(str(unique_types))

        # Calculate average file size
        if metadata.total_files > 0:
            avg_size = metadata.total_size // metadata.total_files
            from src.utils.file_utils import format_size

            avg_size_formatted = format_size(avg_size)
        else:
            avg_size_formatted = "0 B"
        self.avg_size_card.update_value(avg_size_formatted)

    def update_charts(self):
        """Update all chart widgets with new data."""
        from src.utils.logger import logger
        
        metadata = self.data_service.get_metadata()
        logger.debug(f"Dashboard update_charts: Processing {metadata.total_files} files")

        # Update file type pie chart
        file_type_data = self.data_service.get_file_type_data()
        logger.debug(f"Dashboard update_charts: File type data has {len(file_type_data)} types")
        self.file_type_chart.update_data(file_type_data, metadata)

        # Update directory structure chart
        directory_hierarchy = self.data_service.get_directory_hierarchy()
        if directory_hierarchy:
            logger.debug(f"Dashboard update_charts: Directory hierarchy available")
            self.directory_chart.update_data(directory_hierarchy, metadata)
        else:
            logger.debug(f"Dashboard update_charts: No directory hierarchy data")

        # Update file size distribution chart
        size_distribution = self.data_service.get_file_size_distribution()
        logger.debug(f"Dashboard update_charts: Size distribution updating")
        self.size_chart.update_data(size_distribution, metadata)

        # Update file age analysis chart
        age_distribution = self.data_service.get_file_age_distribution()
        logger.debug(f"Dashboard update_charts: Age distribution updating")
        self.age_chart.update_data(age_distribution, metadata)

    def on_chart_item_clicked(self, item_id: str, data: dict[str, Any]):
        """Handle chart item click events."""
        # Extract filter information and emit drill-down signal
        if "filter_type" in data and "filter_value" in data:
            filter_data = {
                "type": data["filter_type"],
                "value": data["filter_value"],
                "source_chart": item_id,
            }
            self.drill_down_requested.emit("filter", filter_data)

    def on_chart_export_requested(self, chart_type: str):
        """Handle chart export requests."""
        self.export_requested.emit(chart_type, "png")

    def on_export_all_clicked(self):
        """Handle export all button click."""
        self.export_requested.emit("dashboard", "pdf")

    def on_refresh_clicked(self):
        """Handle refresh button click."""
        # Re-trigger data update from parent
        if hasattr(self.parent(), "refresh_dashboard"):
            self.parent().refresh_dashboard()

    def show_no_data_message(self):
        """Show a message when there's no data to display."""
        # Clear existing content
        self.clear_charts()

        # Show no data message
        no_data_widget = CardWidget()
        no_data_layout = QVBoxLayout(no_data_widget)

        no_data_label = QLabel("No data to visualize")
        no_data_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_LG};
            padding: {Spacing.XXL}px;
            text-align: center;
            background: transparent;
            border: none;
        }}
        """)
        no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        instruction_label = QLabel(
            "Select a directory and click 'Scan' to analyze files"
        )
        instruction_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_MD};
            text-align: center;
            background: transparent;
            border: none;
        }}
        """)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        no_data_layout.addWidget(no_data_label)
        no_data_layout.addWidget(instruction_label)

        self.charts_layout.addWidget(no_data_widget, 0, 0, 2, 2)  # Span 2x2 grid

    def clear_charts(self):
        """Clear all charts from the layout."""
        while self.charts_layout.count():
            child = self.charts_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def get_chart_widget(self, chart_type: str) -> QWidget | None:
        """Get a specific chart widget by type."""
        return self.charts.get(chart_type)

    def export_chart(
        self, chart_type: str, file_path: str, format: str = "png"
    ) -> bool:
        """
        Export a specific chart to file.

        Args:
            chart_type: Type of chart to export
            file_path: Path where to save the file
            format: Export format ("png", "pdf", "svg")

        Returns:
            True if export was successful
        """
        chart_widget = self.get_chart_widget(chart_type)
        if not chart_widget:
            return False

        if hasattr(chart_widget, "export_as_image"):
            return chart_widget.export_as_image(file_path)

        return False
