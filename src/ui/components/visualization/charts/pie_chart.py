#!/usr/bin/env python3
# File: src/ui/components/visualization/charts/pie_chart.py

import math
from typing import Any

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from ....themes.styles import ModernTheme, Typography
from ..models.chart_data import ChartMetadata, FileTypeData
from .base_chart import InteractiveChart


class PieChartWidget(QWidget):
    """
    Custom pie chart widget using QPainter for perfect theme integration.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = []
        self.segments = []  # Store segment info for mouse events
        self.hover_segment = -1
        self.setMinimumSize(300, 300)

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

    def update_data(self, data: list[FileTypeData]):
        """Update the pie chart with new data."""
        self.data = data
        self.segments = []
        self.update()

    def paintEvent(self, event):
        """Paint the pie chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.data:
            self.draw_no_data_message(painter)
            return

        # Calculate chart area
        margin = 40
        chart_rect = QRect(
            margin, margin, self.width() - 2 * margin, self.height() - 2 * margin
        )

        # Make it square (use the smaller dimension)
        side = min(chart_rect.width(), chart_rect.height())
        chart_rect = QRect(
            (self.width() - side) // 2, (self.height() - side) // 2, side, side
        )

        # Draw pie segments
        self.draw_pie_segments(painter, chart_rect)

        # Draw legend
        self.draw_legend(painter, chart_rect)

    def draw_pie_segments(self, painter: QPainter, chart_rect: QRect):
        """Draw the pie chart segments."""
        if not self.data:
            return

        # Calculate total size
        total_size = sum(item.total_size for item in self.data)
        if total_size == 0:
            return

        # Clear segments list
        self.segments = []

        # Starting angle (12 o'clock position)
        start_angle = 90 * 16  # Qt uses 1/16th degree units

        for i, item in enumerate(self.data):
            # Calculate span angle
            span_angle = int((item.total_size / total_size) * 360 * 16)

            # Get color
            color = QColor(item.color)

            # Highlight hovered segment
            if i == self.hover_segment:
                color = color.lighter(120)

            # Draw the segment
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(ModernTheme.WHITE.name()), 2))
            painter.drawPie(chart_rect, start_angle, span_angle)

            # Store segment info for mouse events
            self.segments.append(
                {
                    "start_angle": start_angle,
                    "span_angle": span_angle,
                    "data": item,
                    "index": i,
                }
            )

            # Draw percentage text for larger segments
            if item.percentage > 5:  # Only show text for segments > 5%
                self.draw_segment_label(
                    painter, chart_rect, start_angle, span_angle, item
                )

            start_angle += span_angle

    def draw_segment_label(
        self,
        painter: QPainter,
        chart_rect: QRect,
        start_angle: int,
        span_angle: int,
        item: FileTypeData,
    ):
        """Draw text label on pie segment."""
        # Calculate label position (middle of the segment)
        mid_angle = (start_angle + span_angle / 2) / 16  # Convert to degrees
        mid_angle_rad = math.radians(mid_angle)

        # Calculate position on the pie (2/3 of the radius from center)
        center_x = chart_rect.center().x()
        center_y = chart_rect.center().y()
        radius = min(chart_rect.width(), chart_rect.height()) / 2
        label_radius = radius * 0.65

        label_x = center_x + label_radius * math.cos(mid_angle_rad)
        label_y = center_y - label_radius * math.sin(
            mid_angle_rad
        )  # Negative because Y is inverted

        # Setup text drawing
        painter.setPen(QPen(QColor(ModernTheme.WHITE.name())))
        font = QFont(Typography.MAIN_FONT.split(",")[0], 10)
        font.setBold(True)
        painter.setFont(font)

        # Draw percentage
        text = f"{item.percentage:.1f}%"
        text_rect = painter.fontMetrics().boundingRect(text)

        # Center the text at the calculated position
        painter.drawText(
            int(label_x - text_rect.width() / 2),
            int(label_y + text_rect.height() / 2),
            text,
        )

    def draw_legend(self, painter: QPainter, chart_rect: QRect):
        """Draw the legend beside the pie chart."""
        if not self.data:
            return

        # Legend area (to the right of the pie)
        legend_x = chart_rect.right() + 20
        legend_y = chart_rect.top()

        # If there's not enough space on the right, put it below
        if legend_x + 150 > self.width():
            legend_x = 20
            legend_y = chart_rect.bottom() + 20

        # Setup text drawing
        painter.setPen(QPen(QColor(ModernTheme.VERY_DARK_GRAY.name())))
        font = QFont(Typography.MAIN_FONT.split(",")[0], 9)
        painter.setFont(font)

        line_height = 20
        current_y = legend_y

        for item in self.data[:8]:  # Show top 8 items in legend
            # Draw color box
            color_rect = QRect(legend_x, current_y, 12, 12)
            painter.fillRect(color_rect, QColor(item.color))
            painter.setPen(QPen(QColor(ModernTheme.BORDER.name())))
            painter.drawRect(color_rect)

            # Draw text
            painter.setPen(QPen(QColor(ModernTheme.VERY_DARK_GRAY.name())))
            text = f"{item.type} ({item.percentage:.1f}%)"
            painter.drawText(legend_x + 18, current_y + 10, text)

            current_y += line_height

    def draw_no_data_message(self, painter: QPainter):
        """Draw a message when there's no data."""
        painter.setPen(QPen(QColor(ModernTheme.DARK_GRAY.name())))
        font = QFont(Typography.MAIN_FONT.split(",")[0], 14)
        painter.setFont(font)

        text = "No data available"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

    def mouseMoveEvent(self, event):
        """Handle mouse move for hover effects."""
        # Find which segment the mouse is over
        old_hover = self.hover_segment
        self.hover_segment = -1

        mouse_pos = event.position().toPoint()
        segment_index = self.get_segment_at_position(mouse_pos)

        if segment_index >= 0:
            self.hover_segment = segment_index

        # Update if hover changed
        if old_hover != self.hover_segment:
            self.update()

    def mousePressEvent(self, event):
        """Handle mouse clicks on segments."""
        if event.button() == Qt.MouseButton.LeftButton:
            mouse_pos = event.position().toPoint()
            segment_index = self.get_segment_at_position(mouse_pos)

            if segment_index >= 0 and hasattr(self.parent(), "on_segment_clicked"):
                data_item = self.data[segment_index]
                self.parent().on_segment_clicked(data_item)

    def get_segment_at_position(self, pos: QPoint) -> int:
        """Get the segment index at the given position."""
        if not self.segments:
            return -1

        # Calculate center and radius
        center_x = self.width() // 2
        center_y = self.height() // 2

        # Check if point is within the pie circle
        dx = pos.x() - center_x
        dy = pos.y() - center_y
        distance = math.sqrt(dx * dx + dy * dy)

        margin = 40
        radius = min(self.width(), self.height()) // 2 - margin

        if distance > radius:
            return -1

        # Calculate angle of the mouse position
        angle = math.degrees(math.atan2(-dy, dx))  # Negative dy because Y is inverted
        if angle < 0:
            angle += 360

        # Convert to Qt angle format (starting from 3 o'clock, going clockwise)
        qt_angle = (90 - angle) % 360
        qt_angle * 16

        # Find which segment contains this angle
        for i, segment in enumerate(self.segments):
            start = segment["start_angle"] / 16
            span = segment["span_angle"] / 16
            end = (start + span) % 360

            if start <= end:
                if start <= qt_angle <= end:
                    return i
            else:  # Segment crosses 0 degrees
                if qt_angle >= start or qt_angle <= end:
                    return i

        return -1


class FileTypePieChart(InteractiveChart):
    """
    File type distribution pie chart component.
    """

    def __init__(self, parent=None):
        super().__init__("File Type Distribution", parent)

    def setup_chart(self):
        """Setup the pie chart widget."""
        self.pie_widget = PieChartWidget(self)
        self.chart_layout.addWidget(self.pie_widget)

    def update_data(
        self, data: list[FileTypeData], metadata: ChartMetadata | None = None
    ):
        """Update the chart with new data."""
        self.chart_data = data
        self.metadata = metadata

        if not data:
            self.show_no_data_message("No files to analyze")
            return

        # Clear any existing no-data message
        self.clear_chart()

        # Re-add the pie widget if it was cleared
        if not hasattr(self, "pie_widget") or not self.pie_widget.parent():
            self.setup_chart()

        self.pie_widget.update_data(data)

    def on_segment_clicked(self, data_item: FileTypeData):
        """Handle pie segment clicks."""
        # Emit drill-down signal with file type filter
        self.emit_item_clicked(
            data_item.type,
            {
                "filter_type": "file_type",
                "filter_value": data_item.type,
                "data": data_item,
            },
        )

    def get_chart_type(self) -> str:
        """Get the chart type identifier."""
        return "pie_chart"

    def get_item_at_position(self, x: int, y: int) -> dict[str, Any] | None:
        """Get the chart item at the specified position."""
        if hasattr(self, "pie_widget"):
            segment_index = self.pie_widget.get_segment_at_position(QPoint(x, y))
            if segment_index >= 0 and segment_index < len(self.chart_data):
                return {
                    "type": "segment",
                    "data": self.chart_data[segment_index],
                    "index": segment_index,
                }
        return None
