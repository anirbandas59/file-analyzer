#!/usr/bin/env python3
# File: src/ui/components/visualization/charts/bar_chart.py

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ....themes.styles import ModernTheme, Spacing, Typography
from ..models.chart_data import ChartMetadata, FileAgeData, FileDistributionData
from .base_chart import BaseChart


class BarWidget(QWidget):
    """Custom widget for drawing individual bars."""

    def __init__(self, value: float, max_value: float, label: str, color: str = None):
        super().__init__()
        self.value = value
        self.max_value = max_value
        self.label = label
        self.color = color or ModernTheme.PRIMARY.name()
        self.setMinimumHeight(30)
        self.setMaximumHeight(50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate bar width as percentage of widget width
        if self.max_value > 0:
            bar_width = int((self.value / self.max_value) * (self.width() - 100))
        else:
            bar_width = 0

        # Draw background
        painter.fillRect(0, 0, self.width() - 100, self.height(), QColor(ModernTheme.LIGHT_GRAY.name()))

        # Draw bar
        if bar_width > 0:
            painter.fillRect(0, 0, bar_width, self.height(), QColor(self.color))

        # Draw value text
        painter.setPen(QPen(QColor(ModernTheme.VERY_DARK_GRAY.name()), 1))
        text_rect = painter.fontMetrics().boundingRect(f"{int(self.value)}")
        text_x = self.width() - 90
        text_y = self.height() // 2 + text_rect.height() // 2
        painter.drawText(text_x, text_y, f"{int(self.value)}")


class SizeDistributionChart(BaseChart):
    """Bar chart for file size distribution."""

    def __init__(self, parent=None):
        super().__init__("File Size Distribution", parent)
        self.distribution_data = None

    def setup_chart(self):
        """Setup the bar chart content."""
        self.bars_widget = QWidget()
        self.bars_layout = QVBoxLayout(self.bars_widget)
        self.bars_layout.setSpacing(Spacing.SM)
        self.chart_layout.addWidget(self.bars_widget)

    def update_data(self, data: FileDistributionData, metadata: ChartMetadata = None):
        """Update the chart with size distribution data."""
        self.distribution_data = data
        self.metadata = metadata
        self.refresh_chart()

    def refresh_chart(self):
        """Refresh the chart display."""
        from src.utils.logger import logger
        
        # Clear existing bars
        for i in reversed(range(self.bars_layout.count())):
            child = self.bars_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        if not self.distribution_data or not any(self.distribution_data.file_counts):
            logger.debug(f"Size distribution chart: No data to display - data exists: {bool(self.distribution_data)}, counts: {self.distribution_data.file_counts if self.distribution_data else 'None'}")
            self.show_no_data_message("No file size data available")
            return
            
        logger.debug(f"Size distribution chart: Displaying {len(self.distribution_data.size_ranges)} size ranges")

        # Find max count for scaling
        max_count = max(self.distribution_data.file_counts) if self.distribution_data.file_counts else 1

        # Create bars for each size range
        for i, (size_range, count, total_size, percentage) in enumerate(
            zip(
                self.distribution_data.size_ranges,
                self.distribution_data.file_counts,
                self.distribution_data.total_sizes,
                self.distribution_data.percentages,
            )
        ):
            if count == 0:
                continue

            # Create container for bar and label
            bar_container = QWidget()
            bar_layout = QVBoxLayout(bar_container)
            bar_layout.setContentsMargins(0, 0, 0, 0)
            bar_layout.setSpacing(2)

            # Label
            label = QLabel(size_range)
            label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_SM};
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {ModernTheme.VERY_DARK_GRAY.name()};
                background: transparent;
                border: none;
            }}
            """)

            # Bar with count info
            bar_info_layout = QHBoxLayout()

            # Bar widget
            bar_widget = BarWidget(count, max_count, size_range, self._get_bar_color(i))

            # Info label
            from src.utils.file_utils import format_size
            info_text = f"{count} files, {format_size(total_size)}, {percentage:.1f}%"
            info_label = QLabel(info_text)
            info_label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_XS};
                color: {ModernTheme.DARK_GRAY.name()};
                background: transparent;
                border: none;
            }}
            """)

            bar_layout.addWidget(label)
            bar_layout.addWidget(bar_widget)
            bar_layout.addWidget(info_label)

            self.bars_layout.addWidget(bar_container)

    def _get_bar_color(self, index: int) -> str:
        """Get color for bar based on index."""
        colors = [
            ModernTheme.SUCCESS.name(),
            ModernTheme.PRIMARY.name(),
            ModernTheme.WARNING.name(),
            ModernTheme.ERROR.name(),
            ModernTheme.DARK_GRAY.name(),
        ]
        return colors[index % len(colors)]

    def get_chart_type(self) -> str:
        return "size_distribution"


class FileAgeChart(BaseChart):
    """Bar chart for file age analysis."""

    def __init__(self, parent=None):
        super().__init__("File Age Analysis", parent)
        self.age_data = None

    def setup_chart(self):
        """Setup the bar chart content."""
        self.bars_widget = QWidget()
        self.bars_layout = QVBoxLayout(self.bars_widget)
        self.bars_layout.setSpacing(Spacing.SM)
        self.chart_layout.addWidget(self.bars_widget)

    def update_data(self, data: FileAgeData, metadata: ChartMetadata = None):
        """Update the chart with age distribution data."""
        self.age_data = data
        self.metadata = metadata
        self.refresh_chart()

    def refresh_chart(self):
        """Refresh the chart display."""
        from src.utils.logger import logger
        
        # Clear existing bars
        for i in reversed(range(self.bars_layout.count())):
            child = self.bars_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        if not self.age_data or not any(self.age_data.file_counts):
            logger.debug(f"File age chart: No data to display - data exists: {bool(self.age_data)}, counts: {self.age_data.file_counts if self.age_data else 'None'}")
            self.show_no_data_message("No file age data available")
            return
            
        logger.debug(f"File age chart: Displaying {len(self.age_data.age_ranges)} age ranges")

        # Find max count for scaling
        max_count = max(self.age_data.file_counts) if self.age_data.file_counts else 1

        # Create bars for each age range
        for i, (age_range, count, total_size, percentage) in enumerate(
            zip(
                self.age_data.age_ranges,
                self.age_data.file_counts,
                self.age_data.total_sizes,
                self.age_data.percentages,
            )
        ):
            if count == 0:
                continue

            # Create container for bar and label
            bar_container = QWidget()
            bar_layout = QVBoxLayout(bar_container)
            bar_layout.setContentsMargins(0, 0, 0, 0)
            bar_layout.setSpacing(2)

            # Label
            label = QLabel(age_range)
            label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_SM};
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {ModernTheme.VERY_DARK_GRAY.name()};
                background: transparent;
                border: none;
            }}
            """)

            # Bar with count info
            bar_widget = BarWidget(count, max_count, age_range, self._get_age_color(i))

            # Info label
            from src.utils.file_utils import format_size
            info_text = f"{count} files, {format_size(total_size)}, {percentage:.1f}%"
            info_label = QLabel(info_text)
            info_label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_XS};
                color: {ModernTheme.DARK_GRAY.name()};
                background: transparent;
                border: none;
            }}
            """)

            bar_layout.addWidget(label)
            bar_layout.addWidget(bar_widget)
            bar_layout.addWidget(info_label)

            self.bars_layout.addWidget(bar_container)

    def _get_age_color(self, index: int) -> str:
        """Get color for bar based on age (newer = green, older = red)."""
        colors = [
            ModernTheme.SUCCESS.name(),  # Today - green
            ModernTheme.PRIMARY.name(),  # This week - blue
            ModernTheme.INFO.name(),     # This month - blue
            ModernTheme.WARNING.name(),  # 3 months - yellow
            ModernTheme.ERROR.name(),    # This year - red
            ModernTheme.DARK_GRAY.name(), # Older - gray
        ]
        return colors[index % len(colors)]

    def get_chart_type(self) -> str:
        return "file_age"