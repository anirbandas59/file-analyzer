#!/usr/bin/env python3
# File: src/ui/file_table.py

import os
import time

from PyQt6.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QTableView

from src.models.file_system_model import FileSystemTableModel
from src.utils.file_utils import scan_directory
from src.utils.logger import logger


class FileTableView(QTableView):
    """
    Table view for displaying files in the selected directory.
    """

    # Signal emitted when files are ready
    files_ready = pyqtSignal(list, int, float)  # files, total_size, scan_time

    def __init__(self):
        super().__init__()

        # Setup the model
        self.model = FileSystemTableModel()
        self.setModel(self.model)

        # Configure the table view
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)

        # Set up header
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 4):  # Columns 1-3 (Size, Date, Type)
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        # Initial sort by name ascending
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Scanner thread for background processing
        self.scanner_thread = None

    def update_files(self, path, full_scan=False):
        """Update the file list for the given directory path."""
        if not path or not os.path.isdir(path):
            logger.warning(f"Invalid path for file scanning: {path}")
            return

        logger.info(f"Starting file scan: {path} (full_scan={full_scan})")

        # If a scan is already running, stop it
        if self.scanner_thread and self.scanner_thread.isRunning():
            logger.debug("Terminating existing scanner thread")
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

        # Update the visualization bar if available
        main_window = self.window()
        if hasattr(main_window, "file_type_bar"):
            main_window.file_type_bar.update_data(file_list)

        # Emit files_ready signal for main window to handle dashboard updates
        self.files_ready.emit(file_list, total_size, scan_time)

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
        try:
            logger.debug(f"Scanner thread started for: {self.path}")
            start_time = time.time()

            file_list, total_size = scan_directory(self.path, self.full_scan)
            scan_time = time.time() - start_time

            logger.debug(f"Scan completed: {len(file_list)} files, {scan_time:.3f}s")

            # Emit the signal with results
            self.files_ready.emit(file_list, total_size, scan_time)

        except Exception as e:
            logger.error(f"Error during directory scan: {self.path}", e)
            # Emit empty results on error
            self.files_ready.emit([], 0, 0.0)
