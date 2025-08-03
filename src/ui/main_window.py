#!/usr/bin/env python3
# File: src/ui/main_window.py

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..utils.logger import logger
from ..utils.settings import settings
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

        logger.info("Initializing MainWindow")

        # Set window properties
        self.setWindowTitle("File System Analyzer")

        # Load theme from settings (main.py will override this)
        saved_theme = settings.get_theme()
        theme_manager.apply_theme(saved_theme)

        # Initialize state
        self.current_scan_path = settings.get_last_directory()

        logger.debug(f"Initial scan path: {self.current_scan_path}")

        # Create the central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a horizontal splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create and setup the left panel (directory tree)
        self.left_panel = TitleCard("Directories", "Navigate and select folders")
        self.directory_tree = DirectoryTreeView()

        # Add recent directories dropdown
        self.recent_dirs_combo = QComboBox()
        self.recent_dirs_combo.setToolTip("Select from recently accessed directories")
        self.recent_dirs_combo.currentTextChanged.connect(self.on_recent_directory_selected)
        self.setup_recent_directories()

        # Add button layout for directory controls
        self.dir_button_layout = QHBoxLayout()
        self.browse_button = ModernButton("Browse", "secondary")
        self.browse_button.setToolTip("Select a directory to analyze")
        self.browse_button.clicked.connect(self.on_browse_clicked)

        self.scan_button = ModernButton("Scan", "primary")
        self.scan_button.setToolTip("Scan the selected directory")
        self.scan_button.clicked.connect(self.on_scan_clicked)

        self.dir_button_layout.addWidget(self.browse_button)
        self.dir_button_layout.addWidget(self.scan_button)

        self.left_panel.add_content_widget(self.directory_tree)
        self.left_panel.add_content_widget(self.recent_dirs_combo)

        # Create a widget to hold the button layout
        self.button_widget = QWidget()
        self.button_widget.setLayout(self.dir_button_layout)
        self.left_panel.add_content_widget(self.button_widget)

        # Create and set up the right panel (content area)
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

        # Create header with theme toggle
        self.header_layout = QHBoxLayout()

        # App title
        self.title_label = QLabel("File System Analyzer")
        self.title_label.setObjectName("main_title")
        self.update_title_style()

        # Theme toggle button
        self.theme_toggle_btn = ModernButton("Dark", "secondary")
        self.theme_toggle_btn.setMaximumWidth(60)
        self.theme_toggle_btn.setToolTip("Toggle Dark/Light Theme")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)

        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.theme_toggle_btn)

        # Create main layout with header and splitter
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addLayout(self.header_layout)
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
        self.file_table.files_ready.connect(self.on_files_ready)

        # Initial status message
        self.update_status("Ready - Select a directory to analyze")

    def on_directory_selected(self, path):
        """Handler for when a directory is selected in the tree view."""
        logger.log_ui_action("directory_selected", "directory_tree", {"path": path})

        self.current_scan_path = path
        settings.set_last_directory(path)
        settings.add_recent_directory(path)
        self.update_recent_directories()

        self.update_status(f"Selected directory: {path}")
        self.file_table.update_files(path)

    def on_browse_clicked(self):
        """Handler for browse button click - opens directory selection dialog."""
        logger.log_ui_action("browse_clicked", "browse_button")

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        # Start from current selected directory, root directory, or home
        current_path = self.directory_tree.get_selected_path()
        if not current_path:
            current_path = self.directory_tree.get_root_path()
        if current_path:
            dialog.setDirectory(current_path)

        if dialog.exec():
            selected_dirs = dialog.selectedFiles()
            if selected_dirs:
                selected_path = selected_dirs[0]
                logger.info(f"User selected directory: {selected_path}")

                # Set the new root directory in the tree
                if self.directory_tree.set_root_directory(selected_path):
                    self.current_scan_path = selected_path
                    settings.set_last_directory(selected_path)
                    settings.add_recent_directory(selected_path)
                    self.update_recent_directories()

                    self.update_status(f"Selected directory: {selected_path}")

                    # Auto-scan the new directory
                    logger.info("Starting auto-scan of selected directory")
                    self.file_table.update_files(selected_path, full_scan=True)
                else:
                    QMessageBox.warning(
                        self,
                        "Invalid Directory",
                        f"Cannot access directory: {selected_path}\n"
                        "Please check permissions and try again."
                    )

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

    def on_files_ready(self, files, total_size, scan_time):
        """Handler for when file scanning is complete."""
        logger.log_scan_results(self.current_scan_path, len(files), total_size, scan_time)

        # Update visualization dashboard with the new file data
        try:
            self.visualization_dashboard.update_data(files, self.current_scan_path)
            logger.debug("Visualization dashboard updated successfully")
        except Exception as e:
            logger.error("Failed to update visualization dashboard", e)

        # Update management dashboard too
        try:
            self.management_dashboard.update_data(files)
            logger.debug("Management dashboard updated successfully")
        except Exception as e:
            logger.error("Failed to update management dashboard", e)

        # Update status with scan results
        self.update_status(f"Scanned {len(files)} files ({scan_time:.2f}s)")

    def update_status(self, message):
        """Updates the status bar with a message."""
        self.status_label.setText(message)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = theme_manager.get_current_theme()
        new_theme = "dark" if current_theme == "light" else "light"

        logger.log_ui_action("theme_toggle", "theme_button", {
            "from": current_theme,
            "to": new_theme
        })

        theme_manager.apply_theme(new_theme)
        settings.set_theme(new_theme)

        # Update button text and tooltip
        if new_theme == "dark":
            self.theme_toggle_btn.setText("Light")
            self.theme_toggle_btn.setToolTip("Switch to Light Theme")
        else:
            self.theme_toggle_btn.setText("Dark")
            self.theme_toggle_btn.setToolTip("Switch to Dark Theme")

        # Update title styling
        self.update_title_style()

    def update_title_style(self):
        """Update the title label styling based on current theme."""
        current_theme = theme_manager.get_current_theme()
        if current_theme == "dark":
            title_color = "#e8eaed"
        else:
            title_color = "#2c3e50"

        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {title_color};
                padding: 5px 0px;
            }}
        """)

    def setup_recent_directories(self):
        """Setup the recent directories dropdown."""
        self.recent_dirs_combo.clear()
        self.recent_dirs_combo.addItem("Recent Directories...", "")

        recent_dirs = settings.get_recent_directories()
        for directory in recent_dirs:
            # Shorten path for display but keep full path as data
            display_name = self.shorten_path(directory)
            self.recent_dirs_combo.addItem(display_name, directory)

        if not recent_dirs:
            self.recent_dirs_combo.addItem("(No recent directories)", "")
            self.recent_dirs_combo.setEnabled(False)
        else:
            self.recent_dirs_combo.setEnabled(True)

        logger.debug(f"Setup recent directories: {len(recent_dirs)} items")

    def shorten_path(self, path: str, max_length: int = 50) -> str:
        """Shorten a path for display in the dropdown."""
        if len(path) <= max_length:
            return path

        # Try to keep the last part of the path
        parts = path.split('/')
        if len(parts) > 2:
            return f".../{'/'.join(parts[-2:])}"
        elif len(parts) == 2:
            return f".../{parts[-1]}"
        else:
            return path[:max_length-3] + "..."

    def on_recent_directory_selected(self, display_text: str):
        """Handle selection from recent directories dropdown."""
        if not display_text or display_text in ["Recent Directories...", "(No recent directories)"]:
            return

        # Get the actual path from the combo box data
        current_index = self.recent_dirs_combo.currentIndex()
        if current_index > 0:  # Skip the first placeholder item
            actual_path = self.recent_dirs_combo.itemData(current_index)
            if actual_path and actual_path != "":
                logger.log_ui_action("recent_directory_selected", "recent_dirs_combo", {
                    "path": actual_path,
                    "display": display_text
                })

                # Set the new root directory in the tree
                if self.directory_tree.set_root_directory(actual_path):
                    self.current_scan_path = actual_path
                    settings.set_last_directory(actual_path)
                    settings.add_recent_directory(actual_path)  # Move to front

                    self.update_status(f"Selected recent directory: {actual_path}")

                    # Auto-scan the directory
                    logger.info(f"Starting scan of recent directory: {actual_path}")
                    self.file_table.update_files(actual_path, full_scan=True)

                    # Refresh the dropdown to reflect new order
                    self.setup_recent_directories()
                else:
                    # Directory not accessible, remove from recent list
                    logger.warning(f"Recent directory not accessible: {actual_path}")
                    QMessageBox.warning(
                        self,
                        "Directory Not Found",
                        f"The directory is no longer accessible:\n{actual_path}\n\n"
                        "It will be removed from recent directories."
                    )
                    # Remove from recent directories (settings class should handle this)
                    recent = settings.get_recent_directories()
                    if actual_path in recent:
                        recent.remove(actual_path)
                        settings.set("recent_directories", recent)
                        settings.save()
                    self.setup_recent_directories()

    def update_recent_directories(self):
        """Update the recent directories dropdown after a new directory is added."""
        self.setup_recent_directories()
