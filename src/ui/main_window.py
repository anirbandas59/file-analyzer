#!/usr/bin/env python3
# File: src/ui/main_window.py

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QSplitter, QStatusBar,
                             QTabWidget, QVBoxLayout, QWidget)

from .directory_tree import DirectoryTreeView
from .file_table import FileTableView
from .visualization import FileTypeBar


class MainWindow(QMainWindow):
    """
    Main application window that contains all UI components.
    """

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("File System Analyzer")

        # Create the central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a horizontal splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create and setup the left panel (directory tree)
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.directory_label = QLabel("Directories")
        self.directory_label.setStyleSheet(
            "font-weight: bold; font-size: 14px;")
        self.directory_tree = DirectoryTreeView()
        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.on_scan_clicked)

        self.left_layout.addWidget(self.directory_label)
        self.left_layout.addWidget(
            self.directory_tree, 1)  # 1 = stretch factor
        self.left_layout.addWidget(self.scan_button)

        # Create and setup the right panel (content area)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)

        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        self.files_tab = QWidget()
        self.charts_tab = QWidget()

        # Setup files tab
        self.files_layout = QVBoxLayout(self.files_tab)

        # Add search bar
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_layout.addStretch(1)
        self.search_layout.addWidget(self.search_input)

        # Add file table
        self.file_table = FileTableView()

        # Add visualization bar
        self.viz_frame = QFrame()
        self.viz_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.viz_frame.setMinimumHeight(40)
        self.viz_layout = QHBoxLayout(self.viz_frame)
        self.viz_label = QLabel("Size Distribution:")
        self.viz_layout.addWidget(self.viz_label)
        self.file_type_bar = FileTypeBar()
        self.viz_layout.addWidget(self.file_type_bar, 1)  # 1 = stretch factor

        # Assemble files tab
        self.files_layout.addLayout(self.search_layout)
        self.files_layout.addWidget(self.file_table, 1)  # 1 = stretch factor
        self.files_layout.addWidget(self.viz_frame)

        # Setup charts tab (placeholder for now)
        self.charts_layout = QVBoxLayout(self.charts_tab)
        self.charts_placeholder = QLabel(
            "Charts view will be implemented in phase 2")
        self.charts_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.charts_layout.addWidget(self.charts_placeholder)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.files_tab, "Files")
        self.tab_widget.addTab(self.charts_tab, "Charts")

        # Add tab widget to right panel
        self.right_layout.addWidget(self.tab_widget)

        # Add panels to splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)

        # Set initial sizes for the splitter (30% left, 70% right)
        self.splitter.setSizes([300, 700])

        # Create main layout with the splitter
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addWidget(self.splitter)

        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Connect signals
        self.directory_tree.directory_selected.connect(
            self.on_directory_selected)
        self.file_type_bar.bar_clicked.connect(self.on_file_type_clicked)

        # Initial status message
        self.update_status("Ready - Select a directory to analyze")

    def on_directory_selected(self, path):
        """Handler for when a directory is selected in the tree view."""
        self.update_status(f"Selected directory: {path}")
        self.file_table.update_files(path)

    def on_scan_clicked(self):
        """Handler for scan button click."""
        current_path = self.directory_tree.get_selected_path()
        if current_path:
            self.update_status(f"Scanning directory: {current_path}")
            self.file_table.update_files(current_path, full_scan=True)

    def on_search_text_changed(self, text):
        """Handler for search input changes."""
        self.file_table.filter_files(text)

    def on_file_type_clicked(self, file_type):
        """Handler for when a file type segment is clicked in the visualization."""
        self.search_input.setText(file_type)

    def update_status(self, message):
        """Updates the status bar with a message."""
        self.status_label.setText(message)
