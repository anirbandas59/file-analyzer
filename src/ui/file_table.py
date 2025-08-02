#!/usr/bin/env python3
# File: src/ui/file_table.py

import os
import time
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import (QAbstractTableModel, QModelIndex, QSize, Qt, QThread,
                          QVariant, pyqtSignal)
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QTableView

from src.models.file_system_model import FileSystemTableModel
from src.utils.file_utils import format_size, get_file_type, scan_directory


class FileTableView(QTableView):
    """
    Table view for displaying files in the selected directory.
    """

    def __init__(self):
        super().__init__()

        # Setup the model
        self.model = FileSystemTableModel()
        self.setModel(self.model)

        # Configure the table view
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)

        # Set up header
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 4):  # Columns 1-3 (Size, Date, Type)
            header.setSectionResizeMode(
                i, QHeaderView.ResizeMode.ResizeToContents)

        # Initial sort by name ascending
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Scanner thread for background processing
        self.scanner_thread = None

    def update_files(self, path, full_scan=False):
        """Update the file list for the given directory path."""
        if not path or not os.path.isdir(path):
            return

        # If a scan is already running, stop it
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.terminate()
            self.scanner_thread.wait()

        # Start a new scan in a background thread
        self.scanner_thread = ScannerThread(path, full_scan)
        self.scanner_thread.files_ready.connect(self.on_files_scanned)
        self.scanner_thread.start()

    def on_files_scanned(self, file_list, total_size, scan_time):
        """Handler for when file scanning is complete."""
        self.model.update_data(file_list)

        # Reset the sort to reflect new data
        current_sort_column = self.horizontalHeader().sortIndicatorSection()
        current_sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.model.sort(current_sort_column, current_sort_order)

        # Get the parent window to update status and visualization
        main_window = self.window()
        if hasattr(main_window, 'update_status'):
            size_str = format_size(total_size)
            main_window.update_status(
                f"{len(file_list):,} files, {size_str} total, scan completed in {scan_time:.2f}s"
            )

        # Update the visualization bar if available
        if hasattr(main_window, 'file_type_bar'):
            main_window.file_type_bar.update_data(file_list)
            
        # Update the dashboard if available
        if hasattr(main_window, 'visualization_dashboard'):
            current_path = getattr(main_window, 'current_scan_path', "")
            main_window.visualization_dashboard.update_data(file_list, current_path)
            
        # Update the management dashboard if available
        if hasattr(main_window, 'management_dashboard'):
            current_path = getattr(main_window, 'current_scan_path', "")
            main_window.management_dashboard.update_data(file_list, current_path)

    def filter_files(self, text):
        """Filter files based on search text."""
        self.model.filter_text = text
        self.model.layoutChanged.emit()


class ScannerThread(QThread):
    """Background thread for scanning directories."""
    files_ready = pyqtSignal(list, int, float)  # files, total size, scan time

    def __init__(self, path, full_scan=False):
        super().__init__()
        self.path = path
        self.full_scan = full_scan

    def run(self):
        """Thread execution method."""
        start_time = time.time()
        file_list, total_size = scan_directory(self.path, self.full_scan)
        scan_time = time.time() - start_time

        # Emit the signal with results
        self.files_ready.emit(file_list, total_size, scan_time)
