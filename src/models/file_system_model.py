#!/usr/bin/env python3
# File: src/models/file_system_model.py


from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt6.QtGui import QBrush, QColor

from src.utils.file_utils import format_size


class FileSystemTableModel(QAbstractTableModel):
    """
    Model for the file table view that displays file information.
    """

    def __init__(self):
        super().__init__()
        self.headers = ["Name", "Size", "Modified", "Type"]
        self.files = []  # List of file info dictionaries
        self.original_files = []  # For filtering purposes
        self.filter_text = ""

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows."""
        return len(self.files)

    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns."""
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Return the data at the given index."""
        if not index.isValid() or index.row() >= len(self.files):
            return QVariant()

        file_info = self.files[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:  # Name
                return file_info["name"]
            elif column == 1:  # Size
                return format_size(file_info["size"])
            elif column == 2:  # Modified date
                return file_info["modified"].strftime("%Y-%m-%d %H:%M")
            elif column == 3:  # Type
                return file_info["type"]

        elif role == Qt.ItemDataRole.BackgroundRole:
            # Alternate row colors
            if index.row() % 2 == 0:
                return QBrush(QColor(248, 248, 248))
            else:
                return QBrush(QColor(255, 255, 255))

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column == 1:  # Size
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            else:
                return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return the header data."""
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self.headers[section]
        return QVariant()

    def sort(self, column, order=Qt.SortOrder.AscendingOrder):
        """Sort the data by the given column."""
        self.layoutAboutToBeChanged.emit()

        if column == 0:  # Name
            self.files.sort(
                key=lambda x: x["name"].lower(),
                reverse=(order == Qt.SortOrder.DescendingOrder),
            )
        elif column == 1:  # Size
            self.files.sort(
                key=lambda x: x["size"], reverse=(order == Qt.SortOrder.DescendingOrder)
            )
        elif column == 2:  # Modified date
            self.files.sort(
                key=lambda x: x["modified"],
                reverse=(order == Qt.SortOrder.DescendingOrder),
            )
        elif column == 3:  # Type
            self.files.sort(
                key=lambda x: x["type"].lower(),
                reverse=(order == Qt.SortOrder.DescendingOrder),
            )

        self.layoutChanged.emit()

    def update_data(self, files):
        """Update the model with new file data."""
        self.layoutAboutToBeChanged.emit()
        self.original_files = files

        # Apply filter if one exists
        if self.filter_text:
            self.apply_filter()
        else:
            self.files = self.original_files

        self.layoutChanged.emit()

    def apply_filter(self):
        """Apply the current filter to the file list."""
        if not self.filter_text:
            self.files = self.original_files
            return

        filter_text = self.filter_text.lower()
        self.files = [
            file
            for file in self.original_files
            if filter_text in file["name"].lower()
            or filter_text in file["type"].lower()
        ]
