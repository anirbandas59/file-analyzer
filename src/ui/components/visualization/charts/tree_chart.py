#!/usr/bin/env python3
# File: src/ui/components/visualization/charts/tree_chart.py

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from ....themes.styles import ModernTheme, Spacing, Typography
from ..models.chart_data import ChartMetadata, DirectoryNode
from .base_chart import InteractiveChart


class DirectoryTreeChart(InteractiveChart):
    """Tree chart for directory structure visualization."""

    def __init__(self, parent=None):
        super().__init__("Directory Structure", parent)
        self.directory_data = None

    def setup_chart(self):
        """Setup the tree chart content."""
        # Create tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Size", "Files", "Type"])
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setStyleSheet(f"""
        QTreeWidget {{
            background-color: {ModernTheme.WHITE.name()};
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: 4px;
            font-size: {Typography.FONT_SM};
        }}
        QTreeWidget::item {{
            padding: 4px;
            border: none;
        }}
        QTreeWidget::item:selected {{
            background-color: {ModernTheme.SELECTED.name()};
        }}
        QTreeWidget::item:hover {{
            background-color: {ModernTheme.HOVER.name()};
        }}
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAYAAADgkQYQAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFHSURBVBiVY/z//z8DJQAggJiQOYAAYqAVAAggGlyAAAKiGAAIIEZcbkAAAVEcAAQQPgABBITLAEAAMeJzPgIIiJYBgABixGcgAgiIlgGAAGLE5yACCIiWAYAAYsTrOAQQEC0DAAHESMj5CCAg2gUAAgjZcQggIFoGAAKIEa/jEEBAtAwABBAjIecjgIBoFwAIIGTHIYCAaBkACCBGvI5DAAHR8gEggJAdJ0AA0TIAEECY/0UAAVH+CwIIiPJfEEBAlP+CAAKi/BcEEBDlvyCA/v//DwWAAAJBfQgCCJjyQQABUf4LAgjo8l8QQEDz/+CAgGj5AwggoON/qAGAAAI6/ocaAAgg5P+CAAKi/BcEEBDlvyCAkP8LAgjo+B8QQMj/BQEERPM/EEBAlP+CAAKi/BcEEBDlvyCA/v//DwIAAQYALY0j+bt24EQAAAAASUVORK5CYII=);
        }}
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAYAAADgkQYQAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFHSURBVBiVY/z//z8DJQAggJiQOYAAYqAVAAggGlyAAAKiGAAIIEZcbkAAAVEcAAQQPgABBITLAEAAMeJzPgIIiJYBgABixGcgAgiIlgGAAGLE5yACCIiWAYAAYsTrOAQQEC0DAAHESMj5CCAg2gUAAgjZcQggIFoGAAKIEa/jEEBAtAwABBAjIecjgIBoFwAIIGTHIYCAaBkACCBGvI5DAAHR8gEggJAdJ0AA0TIAEECY/0UAAVH+CwIIiPJfEEBAlP+CAAKi/BcEEBDlvyCA/v//DwWAAAJBfQgCCJjyQQABUf4LAgjo8l8QQEDz/+CAgGj5AwggoON/qAGAAAI6/ocaAAgg5P+CAAKi/BcEEBDlvyCAkP8LAgjo+B8QQMj/BQEERPM/EEBAlP+CAAKi/BcEEBDlvyCA/v//DwIAAQYALY0j+bt24EQAAAAASUVORK5CYII=);
        }}
        """)

        # Connect tree signals
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        self.tree_widget.itemDoubleClicked.connect(self.on_tree_item_double_clicked)

        # Add to layout
        self.chart_layout.addWidget(self.tree_widget)

        # Add summary info
        self.setup_summary_info()

    def setup_summary_info(self):
        """Setup summary information display."""
        self.summary_widget = QWidget()
        self.summary_layout = QHBoxLayout(self.summary_widget)
        self.summary_layout.setContentsMargins(0, Spacing.SM, 0, 0)

        # Summary labels
        self.total_dirs_label = QLabel("Directories: 0")
        self.total_files_label = QLabel("Files: 0")
        self.total_size_label = QLabel("Total Size: 0 B")

        for label in [self.total_dirs_label, self.total_files_label, self.total_size_label]:
            label.setStyleSheet(f"""
            QLabel {{
                font-size: {Typography.FONT_SM};
                color: {ModernTheme.DARK_GRAY.name()};
                background: transparent;
                border: none;
                padding: 2px 8px;
            }}
            """)

        self.summary_layout.addWidget(self.total_dirs_label)
        self.summary_layout.addWidget(self.total_files_label)
        self.summary_layout.addWidget(self.total_size_label)
        self.summary_layout.addStretch()

        self.chart_layout.addWidget(self.summary_widget)

    def update_data(self, data: DirectoryNode, metadata: ChartMetadata = None):
        """Update the chart with directory hierarchy data."""
        self.directory_data = data
        self.metadata = metadata
        self.refresh_chart()

    def refresh_chart(self):
        """Refresh the chart display."""
        self.tree_widget.clear()

        if not self.directory_data:
            self.show_no_data_message("No directory structure data available")
            return

        # Populate tree
        self.populate_tree_item(None, self.directory_data)

        # Update summary
        self.update_summary()

        # Expand first level
        self.tree_widget.expandToDepth(1)

        # Resize columns to fit content
        for i in range(self.tree_widget.columnCount()):
            self.tree_widget.resizeColumnToContents(i)

    def populate_tree_item(self, parent_item: QTreeWidgetItem, node: DirectoryNode):
        """Recursively populate tree items."""
        from src.utils.file_utils import format_size

        # Create tree item
        if parent_item is None:
            item = QTreeWidgetItem(self.tree_widget)
        else:
            item = QTreeWidgetItem(parent_item)

        # Set item data
        item.setText(0, node.name or "Root")
        item.setText(1, format_size(node.total_size))
        item.setText(2, str(node.file_count))

        if node.is_file:
            item.setText(3, node.file_type or "File")
            # Style file items differently
            item.setForeground(0, ModernTheme.DARK_GRAY)
        else:
            item.setText(3, "Directory")
            # Style directory items
            item.setForeground(0, ModernTheme.VERY_DARK_GRAY)

        # Store node data in item
        item.setData(0, Qt.ItemDataRole.UserRole, node)

        # Add children
        for child in node.children:
            self.populate_tree_item(item, child)

        # Sort children by size (descending)
        if not node.is_file:
            item.sortChildren(1, Qt.SortOrder.DescendingOrder)

    def update_summary(self):
        """Update summary information."""
        if not self.directory_data:
            return

        # Count directories and files
        dir_count, file_count = self.count_nodes(self.directory_data)

        from src.utils.file_utils import format_size

        self.total_dirs_label.setText(f"Directories: {dir_count}")
        self.total_files_label.setText(f"Files: {file_count}")
        self.total_size_label.setText(f"Total Size: {format_size(self.directory_data.total_size)}")

    def count_nodes(self, node: DirectoryNode) -> tuple[int, int]:
        """Count directories and files recursively."""
        dir_count = 0
        file_count = 0

        if node.is_file:
            file_count = 1
        else:
            dir_count = 1

        for child in node.children:
            child_dirs, child_files = self.count_nodes(child)
            dir_count += child_dirs
            file_count += child_files

        return dir_count, file_count

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click."""
        node = item.data(0, Qt.ItemDataRole.UserRole)
        if node and self.is_interactive:
            # Emit click signal with node data
            self.emit_item_clicked(
                f"node_{id(node)}",
                {
                    "node": node,
                    "path": node.path,
                    "is_file": node.is_file,
                    "size": node.total_size,
                    "filter_type": "directory" if not node.is_file else "file",
                    "filter_value": node.path,
                }
            )

    def on_tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item double click."""
        node = item.data(0, Qt.ItemDataRole.UserRole)
        if node and self.is_interactive:
            # Emit drill-down signal
            self.drill_down_requested.emit(
                node.path,
                {
                    "type": "directory_drill_down",
                    "path": node.path,
                    "node": node,
                }
            )

    def get_item_at_position(self, x: int, y: int) -> dict[str, Any] | None:
        """Get the tree item at the specified position."""
        item = self.tree_widget.itemAt(x, y)
        if item:
            node = item.data(0, Qt.ItemDataRole.UserRole)
            if node:
                return {
                    "node": node,
                    "path": node.path,
                    "is_file": node.is_file,
                    "size": node.total_size,
                }
        return None

    def get_chart_type(self) -> str:
        return "directory_structure"
