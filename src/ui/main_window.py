#!/usr/bin/env python3
# File: src/ui/main_window.py

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .components.card_widget import CardWidget, TitleCard
from .components.management import ManagementDashboard
from .components.modern_button import ModernButton
from .components.visualization import VisualizationDashboard
from .directory_tree import DirectoryTreeView
from .file_table import FileTableView
from .themes.theme_manager import theme_manager
from .visualization import FileTypeBar


class MainWindow(QMainWindow):
    """
    Main application window that contains all UI components.
    """

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("File System Analyzer")

        # Apply modern theme
        theme_manager.apply_theme("light")

        # Initialize state
        self.current_scan_path = ""

        # Create the central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a horizontal splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create and setup the left panel (directory tree)
        self.left_panel = TitleCard("Directories", "Navigate and select folders")
        self.directory_tree = DirectoryTreeView()
        self.scan_button = ModernButton("Scan", "primary")
        self.scan_button.clicked.connect(self.on_scan_clicked)

        self.left_panel.add_content_widget(self.directory_tree)
        self.left_panel.add_content_widget(self.scan_button)

        # Create and setup the right panel (content area)
        self.right_panel = CardWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        self.files_tab = QWidget()
        self.charts_tab = QWidget()
        self.management_tab = QWidget()

        # Setup files tab
        self.files_layout = QVBoxLayout(self.files_tab)

        # Add search bar and theme toggle
        self.search_layout = QHBoxLayout()

        # Theme toggle button
        self.theme_toggle_btn = ModernButton("🌙", "secondary")
        self.theme_toggle_btn.setMaximumWidth(40)
        self.theme_toggle_btn.setToolTip("Toggle Dark/Light Theme")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.textChanged.connect(self.on_search_text_changed)

        self.search_layout.addWidget(self.theme_toggle_btn)
        self.search_layout.addStretch(1)
        self.search_layout.addWidget(self.search_input)

        # Add file table
        self.file_table = FileTableView()

        # Add visualization bar
        self.viz_card = CardWidget()
        self.viz_card.setMinimumHeight(60)
        self.viz_layout = QHBoxLayout(self.viz_card)
        self.viz_label = QLabel("File Type Distribution:")
        self.viz_layout.addWidget(self.viz_label)
        self.file_type_bar = FileTypeBar()
        self.viz_layout.addWidget(self.file_type_bar, 1)  # 1 = stretch factor

        # Assemble files tab
        self.files_layout.addLayout(self.search_layout)
        self.files_layout.addWidget(self.file_table, 1)  # 1 = stretch factor
        self.files_layout.addWidget(self.viz_card)

        # Setup charts tab with visualization dashboard
        self.charts_layout = QVBoxLayout(self.charts_tab)
        self.charts_layout.setContentsMargins(0, 0, 0, 0)
        self.visualization_dashboard = VisualizationDashboard()
        self.charts_layout.addWidget(self.visualization_dashboard)

        # Setup management tab with smart file management dashboard
        self.management_layout = QVBoxLayout(self.management_tab)
        self.management_layout.setContentsMargins(0, 0, 0, 0)
        self.management_dashboard = ManagementDashboard()
        self.management_layout.addWidget(self.management_dashboard)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.files_tab, "Files")
        self.tab_widget.addTab(self.charts_tab, "Charts")
        self.tab_widget.addTab(self.management_tab, "Management")

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
        self.directory_tree.directory_selected.connect(self.on_directory_selected)
        self.file_type_bar.bar_clicked.connect(self.on_file_type_clicked)
        self.visualization_dashboard.drill_down_requested.connect(
            self.on_dashboard_drill_down
        )

        # Initial status message
        self.update_status("Ready - Select a directory to analyze")

    def on_directory_selected(self, path):
        """Handler for when a directory is selected in the tree view."""
        self.current_scan_path = path
        self.update_status(f"Selected directory: {path}")
        self.file_table.update_files(path)

    def on_scan_clicked(self):
        """Handler for scan button click."""
        current_path = self.directory_tree.get_selected_path()
        if current_path:
            self.current_scan_path = current_path
            self.update_status(f"Scanning directory: {current_path}")
            self.file_table.update_files(current_path, full_scan=True)

    def on_search_text_changed(self, text):
        """Handler for search input changes."""
        self.file_table.filter_files(text)

    def on_file_type_clicked(self, file_type):
        """Handler for when a file type segment is clicked in the visualization."""
        self.search_input.setText(file_type)

    def on_dashboard_drill_down(self, path, filter_data):
        """Handler for dashboard drill-down requests."""
        if filter_data.get("type") == "file_type":
            # Filter by file type
            file_type = filter_data.get("value", "")
            self.search_input.setText(file_type)
        elif filter_data.get("type") == "directory":
            # Navigate to directory (future implementation)
            pass

    def update_status(self, message):
        """Updates the status bar with a message."""
        self.status_label.setText(message)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = theme_manager.get_current_theme()
        new_theme = "dark" if current_theme == "light" else "light"
        theme_manager.apply_theme(new_theme)

        # Update button icon and tooltip
        if new_theme == "dark":
            self.theme_toggle_btn.setText("☀️")
            self.theme_toggle_btn.setToolTip("Switch to Light Theme")
        else:
            self.theme_toggle_btn.setText("🌙")
            self.theme_toggle_btn.setToolTip("Switch to Dark Theme")
