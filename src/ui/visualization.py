#!/usr/bin/env python3
# File: src/ui/visualization.py

import math
from collections import defaultdict

from PyQt6.QtCore import QRect, Qt, pyqtSignal
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from .themes.styles import ModernTheme, FILE_COLORS


class FileTypeBar(QWidget):
    """
    Widget that displays a horizontal bar chart of file types by size.
    """

    # Signal emitted when a bar segment is clicked
    bar_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Setup widget
        self.setMinimumHeight(40)
        self.setMinimumWidth(100)

        # Initialize data structures
        self.data = {}  # Dictionary of {type: size}
        self.total_size = 0
        # Use theme colors for consistent styling
        self.colors = FILE_COLORS

        # Setup layout
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        # Test data for development
        self.test_data = {
            "EXE": 6000000,
            "DLL": 2000000,
            "PDF": 500000,
            "DOC": 200000,
            "OTHER": 1000000,
        }

    def update_data(self, file_list):
        """
        Update the chart with new file data.

        Args:
            file_list: List of file dictionaries from the file model
        """
        # Reset data
        self.data = defaultdict(int)
        self.total_size = 0

        # Calculate total size for each file type
        for file in file_list:
            file_type = file["type"]
            size = file["size"]

            self.data[file_type] += size
            self.total_size += size

        # Sort and limit to top 10 file types
        sorted_types = sorted(self.data.items(), key=lambda x: x[1], reverse=True)

        # If we have more than 10 types, combine the smallest into "OTHER"
        if len(sorted_types) > 10:
            top_types = sorted_types[:9]
            other_size = sum(size for _, size in sorted_types[9:])

            self.data = {file_type: size for file_type, size in top_types}
            self.data["OTHER"] = other_size

        # Update the widget
        self.update()

    def paintEvent(self, event):
        """
        Paint the bar chart.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # If no data, just draw a placeholder
        if not self.data and not self.test_data:
            painter.fillRect(self.rect(), ModernTheme.LIGHT_GRAY)
            painter.setPen(ModernTheme.DARK_GRAY)
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "No data available"
            )
            return

        # Use test data if no real data is available
        data = self.data if self.data else self.test_data
        total = self.total_size if self.total_size else sum(self.test_data.values())

        # Draw the segments
        x = 0
        width = self.width()
        height = self.height()

        # Store the segments for mouse events
        self.segments = []

        for i, (file_type, size) in enumerate(
            sorted(data.items(), key=lambda x: x[1], reverse=True)
        ):
            # Calculate the width of this segment
            segment_width = math.floor((size / total) * width) if total > 0 else 0

            # If this is the last segment, make sure it extends to the end
            if i == len(data) - 1:
                segment_width = width - x

            # Choose color
            color = self.colors.get(file_type, self.colors["OTHER"])

            # Draw the segment
            painter.fillRect(x, 0, segment_width, height, color)

            # Store segment info for mouse events
            self.segments.append(
                {
                    "type": file_type,
                    "rect": QRect(x, 0, segment_width, height),
                    "size": size,
                }
            )

            # Draw the text if the segment is wide enough
            if segment_width > 60:
                painter.setPen(Qt.GlobalColor.white)
                # Calculate text width and see if it fits
                text = f"{file_type} ({size / total:.1%})"
                text_rect = QRect(x + 5, 0, segment_width - 10, height)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, text)

            # Move x for the next segment
            x += segment_width

    def mousePressEvent(self, event):
        """
        Handle mouse clicks to identify which segment was clicked.
        """
        if not hasattr(self, "segments"):
            return

        for segment in self.segments:
            if segment["rect"].contains(event.position().toPoint()):
                self.bar_clicked.emit(segment["type"])
                break
