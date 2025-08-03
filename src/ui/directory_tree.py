#!/usr/bin/env python3
# File: src/ui/directory_tree.py

import os
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
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
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setHeaderHidden(False)

        # Path dictionary to keep track of paths for items
        self.path_dict = {}

        # Connect signals
        self.clicked.connect(self.on_directory_clicked)

        # Populate with drives/home directory
        self.populate_tree()

    def populate_tree(self, root_path=None):
        """Populate the directory tree with initial items"""
        # Use provided root path or default to home directory
        if root_path is None:
            root_path = str(Path.home())

        # Validate the root path
        if not os.path.exists(root_path) or not os.path.isdir(root_path):
            root_path = str(Path.home())  # Fallback to home if invalid

        # Clear existing tree
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Directories"])
        self.path_dict.clear()

        root_item = QStandardItem(os.path.basename(root_path) or root_path)
        root_item.setData(root_path, Qt.ItemDataRole.UserRole)
        self.model.appendRow(root_item)
        self.path_dict[self.model.indexFromItem(root_item)] = root_path

        # Populate first level subdirectories
        self.populate_subdirectories(root_item, root_path)

        # Expand the root item
        self.expand(self.model.indexFromItem(root_item))

    def set_root_directory(self, root_path):
        """
        Set a new root directory for the tree view.

        Args:
            root_path: Path to the new root directory

        Returns:
            bool: True if successful, False if path is invalid
        """
        if not root_path or not os.path.exists(root_path) or not os.path.isdir(root_path):
            return False

        try:
            # Check if we have read permissions
            os.listdir(root_path)
            self.populate_tree(root_path)
            return True
        except PermissionError:
            return False

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

                # Check if this directory has subdirectories
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
        index = next(idx for idx in indexes if idx.column() == 0)
        return self.path_dict.get(index)

    def get_root_path(self):
        """Returns the current root directory path"""
        if self.model.rowCount() > 0:
            root_index = self.model.index(0, 0)
            return self.path_dict.get(root_index)
        return str(Path.home())
