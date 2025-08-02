#!/usr/bin/env python3
# File: src/ui/directory_tree.py

import os
from pathlib import Path

from PyQt6.QtCore import QDir, QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QAbstractItemView, QTreeView


class DirectoryTreeView(QTreeView):
    """Tree view for navigating the file system directories."""

    # Custom signal emitted when a directory is selected
    directory_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Set up the model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Directories"])
        self.setModel(self.model)

        # Configure the tree view
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setHeaderHidden(False)

        # Path dictionary to keep track of paths for items
        self.path_dict = {}

        # Connect signals
        self.clicked.connect(self.on_directory_clicked)

        # Populate with drives/home directory
        self.populate_tree()

    def populate_tree(self):
        """Populate the directory tree with initial items"""
        # Use home directory as root
        home_dir = str(Path.home())
        root_item = QStandardItem(os.path.basename(home_dir))
        root_item.setData(home_dir, Qt.ItemDataRole.UserRole)
        self.model.appendRow(root_item)
        self.path_dict[self.model.indexFromItem(root_item)] = home_dir

        # Populate first level subdirectories
        self.populate_subdirectories(root_item, home_dir)

        # Expand the root item
        self.expand(self.model.indexFromItem(root_item))

    def populate_subdirectories(self, parent_item, parent_path):
        """Populate the subdirectories of a given directory"""
        try:
            directories = []
            with os.scandir(parent_path) as entries:
                for entry in entries:
                    if entry.is_dir() and not entry.name.startswith("."):
                        directories.append((entry.name, entry.path))

            # Sort directories alphabetically
            directories.sort(key=lambda x: x[0].lower())

            # Add directories to the tree
            for name, path in directories:
                item = QStandardItem(name)
                item.setData(path, Qt.ItemDataRole.UserRole)
                parent_item.appendRow(item)
                self.path_dict[self.model.indexFromItem(item)] = path

            # Check if directory has subdirectories
            has_subdirs = False
            try:
                with os.scandir(path) as subentries:
                    for subentry in subentries:
                        if subentry.is_dir() and not subentry.name.startswith("."):
                            has_subdirs = True
                            break
            except (PermissionError, FileNotFoundError):
                pass

            # If directory has subdirectories, add a placeholder item
            if has_subdirs:
                placeholder = QStandardItem("Loading...")
                item.appendRow(placeholder)

        except (PermissionError, FileNotFoundError):
            # If we cannot access the directory, just return
            pass

    def on_directory_clicked(self, index):
        """Handle directory item click events"""
        if not index.isValid():
            return

        # Get the file path from the model
        path = self.path_dict.get(index)

        # Check if the directory has been expanded
        item = self.model.itemFromIndex(index)
        if item.rowCount() == 1 and item.child(0).text() == "Loading...":
            # Remove the placeholder item
            item.removeRow(0)
            # Populate subdirectories
            self.populate_subdirectories(item, path)

        # Emit the directory selected signal with the path
        if path:
            self.directory_selected.emit(path)

    def get_selected_path(self):
        """Returns the currently selected directory path or None if none selected"""
        indexes = self.selectedIndexes()
        if not indexes:
            return None

        # We only care about the first column
        index = [idx for idx in indexes if idx.column() == 0][0]
        return self.path_dict.get(index)
