#!/usr/bin/env python3
# File: src/ui/components/management/management_dashboard.py

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ...themes.styles import ModernTheme, Spacing, Typography
from ..card_widget import CardWidget, StatsCard, TitleCard
from ..modern_button import ModernButton
from .tools.age_analyzer import FileAgeAnalyzerTool
from .tools.duplicate_finder import DuplicateFinderTool
from .tools.large_file_analyzer import LargeFileAnalyzerTool


class ManagementOverview(QWidget):
    """Overview widget showing management tool summary and quick actions."""

    tool_selected = pyqtSignal(str)  # tool_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the overview UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.MD)

        # Welcome header
        welcome_card = TitleCard(
            "Smart File Management",
            "Optimize your storage with intelligent file analysis and cleanup tools",
        )
        layout.addWidget(welcome_card)

        # Tool cards
        self.setup_tool_cards(layout)

        # Quick stats (placeholder until analysis is run)
        self.setup_quick_stats(layout)

    def setup_tool_cards(self, layout):
        """Setup cards for each management tool."""
        tools_frame = CardWidget()
        tools_layout = QVBoxLayout(tools_frame)

        # Tools grid
        tools_grid = QHBoxLayout()

        # Duplicate Finder Tool
        duplicate_card = self.create_tool_card(
            "🔍 Duplicate Finder",
            "Find and remove duplicate files to free up disk space",
            "Find exact duplicates using content analysis",
            "duplicate_finder",
        )

        # Large Files Tool
        large_files_card = self.create_tool_card(
            "📊 Large Files",
            "Identify the largest files consuming disk space",
            "Analyze file sizes and get cleanup recommendations",
            "large_files",
        )

        # File Age Analysis Tool
        age_analysis_card = self.create_tool_card(
            "📅 File Age Analysis",
            "Analyze file ages and get archival recommendations",
            "Find old unused files ready for archiving",
            "age_analysis",
        )

        tools_grid.addWidget(duplicate_card)
        tools_grid.addWidget(large_files_card)
        tools_grid.addWidget(age_analysis_card)

        tools_layout.addLayout(tools_grid)
        layout.addWidget(tools_frame)

    def create_tool_card(
        self, title: str, description: str, details: str, tool_id: str
    ) -> CardWidget:
        """Create a tool selection card."""
        card = CardWidget()
        card.setMinimumHeight(150)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(Spacing.SM)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
        QLabel {{
            font-size: {Typography.FONT_LG};
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_MD};
            background: transparent;
            border: none;
        }}
        """)

        # Details
        details_label = QLabel(details)
        details_label.setWordWrap(True)
        details_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
            font-style: italic;
            background: transparent;
            border: none;
        }}
        """)

        # Launch button
        launch_button = ModernButton("Launch Tool", "primary")
        launch_button.clicked.connect(lambda: self.tool_selected.emit(tool_id))

        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        card_layout.addWidget(details_label)
        card_layout.addStretch()
        card_layout.addWidget(launch_button)

        return card

    def setup_quick_stats(self, layout):
        """Setup quick statistics display."""
        stats_card = TitleCard(
            "Quick Statistics", "Analysis results will appear here after running tools"
        )

        # Placeholder stats
        stats_layout = QHBoxLayout()

        files_stat = StatsCard("Files Scanned", "0")
        duplicates_stat = StatsCard("Duplicates Found", "0")
        savings_stat = StatsCard("Potential Savings", "0 B")

        stats_layout.addWidget(files_stat)
        stats_layout.addWidget(duplicates_stat)
        stats_layout.addWidget(savings_stat)

        stats_card.add_content_layout(stats_layout)
        layout.addWidget(stats_card)

        # Store references for updating
        self.files_stat = files_stat
        self.duplicates_stat = duplicates_stat
        self.savings_stat = savings_stat

    def update_stats(self, stats: Dict):
        """Update the quick statistics display."""
        self.files_stat.update_value(str(stats.get("total_files", 0)))
        self.duplicates_stat.update_value(str(stats.get("duplicate_groups", 0)))

        savings = stats.get("potential_savings", 0)
        if savings > 0:
            from src.utils.file_utils import format_size

            self.savings_stat.update_value(format_size(savings))
        else:
            self.savings_stat.update_value("0 B")


class ManagementDashboard(QWidget):
    """
    Main dashboard for smart file management tools.
    Provides access to duplicate finder, large file analysis, and file age analysis.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_files = []
        self.current_path = ""

        # Tool instances
        self.duplicate_finder = None
        self.large_files_tool = None
        self.age_analysis_tool = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the management dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()

        # Overview page
        self.overview = ManagementOverview()
        self.overview.tool_selected.connect(self.launch_tool)
        self.stacked_widget.addWidget(self.overview)

        # Tool pages (created on demand)
        self.tool_pages = {}

        layout.addWidget(self.stacked_widget)

        # Navigation bar
        self.setup_navigation(layout)

    def setup_navigation(self, layout):
        """Setup navigation bar for tool switching."""
        nav_frame = QFrame()
        nav_frame.setFixedHeight(50)
        nav_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {ModernTheme.LIGHT_GRAY.name()};
            border-top: 1px solid {ModernTheme.BORDER.name()};
        }}
        """)

        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)

        # Back to overview button
        self.back_button = ModernButton("← Overview", "secondary")
        self.back_button.clicked.connect(self.show_overview)
        self.back_button.setVisible(False)

        # Current tool label
        self.current_tool_label = QLabel("Smart File Management")
        self.current_tool_label.setStyleSheet(f"""
        QLabel {{
            font-size: {Typography.FONT_MD};
            font-weight: {Typography.WEIGHT_MEDIUM};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.current_tool_label)
        nav_layout.addStretch()

        layout.addWidget(nav_frame)

    def launch_tool(self, tool_name: str):
        """Launch a specific management tool."""
        if tool_name == "duplicate_finder":
            self.show_duplicate_finder()
        elif tool_name == "large_files":
            self.show_large_files_tool()
        elif tool_name == "age_analysis":
            self.show_age_analysis_tool()

    def show_duplicate_finder(self):
        """Show the duplicate finder tool."""
        if "duplicate_finder" not in self.tool_pages:
            self.duplicate_finder = DuplicateFinderTool()
            self.duplicate_finder.update_files(self.current_files)
            self.tool_pages["duplicate_finder"] = self.duplicate_finder
            self.stacked_widget.addWidget(self.duplicate_finder)

        self.stacked_widget.setCurrentWidget(self.duplicate_finder)
        self.current_tool_label.setText("Duplicate File Finder")
        self.back_button.setVisible(True)

    def show_large_files_tool(self):
        """Show the large files analysis tool."""
        if "large_files" not in self.tool_pages:
            self.large_files_tool = LargeFileAnalyzerTool()
            self.large_files_tool.update_files(self.current_files)
            self.tool_pages["large_files"] = self.large_files_tool
            self.stacked_widget.addWidget(self.large_files_tool)

        self.stacked_widget.setCurrentWidget(self.large_files_tool)
        self.current_tool_label.setText("Large Files Analyzer")
        self.back_button.setVisible(True)

    def show_age_analysis_tool(self):
        """Show the file age analysis tool."""
        if "age_analysis" not in self.tool_pages:
            self.age_analysis_tool = FileAgeAnalyzerTool()
            self.age_analysis_tool.update_files(self.current_files)
            self.tool_pages["age_analysis"] = self.age_analysis_tool
            self.stacked_widget.addWidget(self.age_analysis_tool)

        self.stacked_widget.setCurrentWidget(self.age_analysis_tool)
        self.current_tool_label.setText("File Age Analyzer")
        self.back_button.setVisible(True)

    def create_tool_placeholder(self, title: str, description: str) -> QWidget:
        """Create a placeholder widget for tools not yet implemented."""
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)

        card = TitleCard(title, "Coming Soon")

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_MD};
            padding: {Spacing.XL}px;
            border: 2px dashed {ModernTheme.MEDIUM_GRAY.name()};
            border-radius: 8px;
            background: transparent;
            text-align: center;
        }}
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card.add_content_widget(desc_label)
        layout.addWidget(card)
        layout.addStretch()

        return placeholder

    def show_overview(self):
        """Return to the overview page."""
        self.stacked_widget.setCurrentWidget(self.overview)
        self.current_tool_label.setText("Smart File Management")
        self.back_button.setVisible(False)

    def update_data(self, files: List[Dict], directory_path: str = ""):
        """
        Update the dashboard with new file data.

        Args:
            files: List of file dictionaries from scanner
            directory_path: Path of the scanned directory
        """
        self.current_files = files
        self.current_path = directory_path

        # Update tools if they exist
        if self.duplicate_finder:
            self.duplicate_finder.update_files(files)

        if self.large_files_tool:
            self.large_files_tool.update_files(files)

        if self.age_analysis_tool:
            self.age_analysis_tool.update_files(files)

        # Update overview stats if duplicate analysis has been run
        if (
            hasattr(self.duplicate_finder, "duplicate_groups")
            and self.duplicate_finder.duplicate_groups
        ):
            stats = self.duplicate_finder.get_analysis_summary()
            stats["total_files"] = len(files)
            self.overview.update_stats(stats)
        else:
            # Reset stats
            self.overview.update_stats({"total_files": len(files)})

    def get_current_tool(self) -> Optional[str]:
        """Get the currently active tool name."""
        current_widget = self.stacked_widget.currentWidget()

        if current_widget == self.overview:
            return "overview"
        elif current_widget == self.duplicate_finder:
            return "duplicate_finder"
        else:
            # Check tool pages
            for tool_name, widget in self.tool_pages.items():
                if current_widget == widget:
                    return tool_name

        return None

    def has_analysis_results(self) -> bool:
        """Check if any analysis results are available."""
        if self.duplicate_finder and hasattr(self.duplicate_finder, "duplicate_groups"):
            return len(self.duplicate_finder.duplicate_groups) > 0
        return False

    def get_management_summary(self) -> Dict:
        """Get overall management summary statistics."""
        summary = {
            "total_files": len(self.current_files),
            "tools_used": [],
            "total_potential_savings": 0,
        }

        # Add duplicate finder results
        if self.duplicate_finder and hasattr(self.duplicate_finder, "duplicate_groups"):
            duplicate_stats = self.duplicate_finder.get_analysis_summary()
            summary["tools_used"].append("duplicate_finder")
            summary["duplicate_groups"] = duplicate_stats.get("duplicate_groups", 0)
            summary["total_potential_savings"] += duplicate_stats.get(
                "potential_savings", 0
            )

        return summary
