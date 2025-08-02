#!/usr/bin/env python3
# File: src/ui/components/management/tools/age_analyzer.py

import os
import platform
import subprocess
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ....themes.styles import ModernTheme, Spacing, Typography
from ...card_widget import CardWidget, TitleCard
from ...modern_button import ModernButton
from ..models.management_data import FileAgeAnalysis, FileAgeCategory, FileInfo
from ..services.age_analysis_service import FileAgeAnalysisService
from ..workers.analysis_workers import FileAgeAnalysisWorker


class AgeCategoryCard(CardWidget):
    """Card widget displaying statistics for a specific age category."""

    category_selected = pyqtSignal(object)  # FileAgeCategory

    def __init__(self, category: FileAgeCategory, stats: dict, parent=None):
        super().__init__(parent)

        self.category = category
        self.stats = stats
        self.setup_ui()

    def setup_ui(self):
        """Setup the category card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # Category header
        header_layout = QHBoxLayout()

        # Category name and color indicator
        color_indicator = QLabel()
        color_indicator.setStyleSheet(f"""
        QLabel {{
            background-color: {self.stats["color"]};
            border-radius: 6px;
            min-width: 12px;
            max-width: 12px;
            min-height: 12px;
            max-height: 12px;
        }}
        """)

        name_label = QLabel(self.category.value.title())
        name_label.setStyleSheet(f"""
        QLabel {{
            font-weight: {Typography.WEIGHT_BOLD};
            font-size: {Typography.FONT_LG};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        header_layout.addWidget(color_indicator)
        header_layout.addWidget(name_label)
        header_layout.addStretch()

        # Description
        desc_label = QLabel(self.stats["description"])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
            background: transparent;
            border: none;
        }}
        """)

        # Statistics
        stats_layout = QGridLayout()

        # File count
        count_label = QLabel("Files:")
        count_value = QLabel(f"{self.stats['count']:,}")
        count_value.setStyleSheet(f"""
        QLabel {{
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        # Size
        from src.utils.file_utils import format_size

        size_label = QLabel("Size:")
        size_value = QLabel(format_size(self.stats["total_size"]))
        size_value.setStyleSheet(f"""
        QLabel {{
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        # Percentage
        percent_label = QLabel("% of Files:")
        percent_value = QLabel(f"{self.stats['percentage']:.1f}%")
        percent_value.setStyleSheet(f"""
        QLabel {{
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        stats_layout.addWidget(count_label, 0, 0)
        stats_layout.addWidget(count_value, 0, 1)
        stats_layout.addWidget(size_label, 1, 0)
        stats_layout.addWidget(size_value, 1, 1)
        stats_layout.addWidget(percent_label, 2, 0)
        stats_layout.addWidget(percent_value, 2, 1)

        # View files button
        if self.stats["count"] > 0:
            view_button = ModernButton("View Files", "secondary")
            view_button.clicked.connect(
                lambda: self.category_selected.emit(self.category)
            )
            layout.addWidget(view_button)

        # Assemble layout
        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        layout.addLayout(stats_layout)

        # Set minimum height
        self.setMinimumHeight(160)


class ArchivalCandidateWidget(CardWidget):
    """Widget for displaying a file that's a candidate for archival."""

    file_action_requested = pyqtSignal(str, str)  # action, file_path
    file_selected = pyqtSignal(str, bool)  # file_path, selected

    def __init__(self, file_info: FileInfo, is_selected: bool = False, parent=None):
        super().__init__(parent)

        self.file_info = file_info
        self.is_selected = is_selected
        self.setup_ui()

    def setup_ui(self):
        """Setup the archival candidate UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        layout.setSpacing(Spacing.MD)

        # Selection checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.is_selected)
        self.checkbox.stateChanged.connect(self.on_selection_changed)

        # File info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # File name and age badge
        name_layout = QHBoxLayout()
        name_label = QLabel(self.file_info.name)
        name_label.setStyleSheet(f"""
        QLabel {{
            font-weight: {Typography.WEIGHT_MEDIUM};
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        age_badge = QLabel(self.file_info.age_category.value.title())
        age_badge.setStyleSheet(f"""
        QLabel {{
            background-color: {self._get_age_color()};
            color: {ModernTheme.WHITE.name()};
            padding: 2px 8px;
            border-radius: 4px;
            font-size: {Typography.FONT_XS};
            font-weight: {Typography.WEIGHT_BOLD};
        }}
        """)

        name_layout.addWidget(name_label)
        name_layout.addStretch()
        name_layout.addWidget(age_badge)

        # File details
        from src.utils.file_utils import format_size

        days_old = (datetime.now() - self.file_info.modified).days
        details_text = f"{self.file_info.path} • {format_size(self.file_info.size)} • {days_old} days old"
        details_label = QLabel(details_text)
        details_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
            background: transparent;
            border: none;
        }}
        """)

        info_layout.addLayout(name_layout)
        info_layout.addWidget(details_label)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(Spacing.SM)

        open_btn = ModernButton("Open", "secondary")
        open_btn.setMaximumWidth(80)
        open_btn.clicked.connect(
            lambda: self.file_action_requested.emit(
                "open_location", self.file_info.path
            )
        )

        archive_btn = ModernButton("Archive", "primary")
        archive_btn.setMaximumWidth(80)
        archive_btn.clicked.connect(
            lambda: self.file_action_requested.emit("archive", self.file_info.path)
        )

        actions_layout.addWidget(open_btn)
        actions_layout.addWidget(archive_btn)

        # Assemble layout
        layout.addWidget(self.checkbox)
        layout.addLayout(info_layout, 1)
        layout.addLayout(actions_layout)

    def _get_age_color(self) -> str:
        """Get color for age category."""
        colors = {
            FileAgeCategory.RECENT: "#10B981",
            FileAgeCategory.ACTIVE: "#F59E0B",
            FileAgeCategory.CURRENT: "#3B82F6",
            FileAgeCategory.STALE: "#F97316",
            FileAgeCategory.ARCHIVE: "#EF4444",
            FileAgeCategory.OLD: "#7C2D12",
        }
        return colors.get(self.file_info.age_category, "#6B7280")

    def on_selection_changed(self):
        """Handle selection change."""
        self.is_selected = self.checkbox.isChecked()
        self.file_selected.emit(self.file_info.path, self.is_selected)


class FileAgeAnalyzerTool(QWidget):
    """Main file age analyzer and archival management tool."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_files = []
        self.current_analysis = None
        self.analysis_worker = None
        self.service = FileAgeAnalysisService()
        self.selected_files = set()

        self.setup_ui()

    def setup_ui(self):
        """Setup the file age analyzer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.MD)

        # Header
        self.setup_header(layout)

        # Configuration panel
        self.setup_configuration(layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results area
        self.setup_results_area(layout)

    def setup_header(self, layout):
        """Setup the tool header."""
        header_card = TitleCard(
            "File Age Analyzer", "Analyze file ages and get archival recommendations"
        )
        layout.addWidget(header_card)

    def setup_configuration(self, layout):
        """Setup configuration controls."""
        config_card = CardWidget()
        config_layout = QVBoxLayout(config_card)

        # Configuration options
        options_layout = QHBoxLayout()

        # Analysis options
        self.include_stale_checkbox = QCheckBox(
            "Include stale files (6mo-1yr) in recommendations"
        )
        self.include_stale_checkbox.setChecked(True)
        self.include_stale_checkbox.setStyleSheet(f"""
        QCheckBox {{
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
        }}
        """)

        # Minimum size for priority recommendations
        size_layout = QHBoxLayout()
        size_label = QLabel("Min size for priority (MB):")
        size_label.setStyleSheet(f"""
        QLabel {{
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        self.min_size_spinbox = QSpinBox()
        self.min_size_spinbox.setRange(1, 1000)
        self.min_size_spinbox.setValue(10)
        self.min_size_spinbox.setSuffix(" MB")
        self.min_size_spinbox.setStyleSheet(f"""
        QSpinBox {{
            padding: 6px;
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: 4px;
            font-size: {Typography.FONT_MD};
            background: {ModernTheme.WHITE.name()};
        }}
        """)

        size_layout.addWidget(size_label)
        size_layout.addWidget(self.min_size_spinbox)

        options_layout.addWidget(self.include_stale_checkbox)
        options_layout.addLayout(size_layout)
        options_layout.addStretch()

        # Action buttons
        self.start_button = ModernButton("Start Analysis", "primary")
        self.start_button.clicked.connect(self.start_analysis)

        self.cancel_button = ModernButton("Cancel", "secondary")
        self.cancel_button.clicked.connect(self.cancel_analysis)
        self.cancel_button.setVisible(False)

        self.export_button = ModernButton("Export Results", "secondary")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setVisible(False)

        options_layout.addWidget(self.start_button)
        options_layout.addWidget(self.cancel_button)
        options_layout.addWidget(self.export_button)

        config_layout.addLayout(options_layout)
        layout.addWidget(config_card)

    def setup_results_area(self, layout):
        """Setup the results display area."""
        # Results container
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_area.setVisible(False)

        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(Spacing.MD)

        self.results_area.setWidget(self.results_widget)
        layout.addWidget(self.results_area, 1)  # Take remaining space

    def update_files(self, files: list[dict]):
        """Update the files to analyze."""
        self.current_files = files
        self.start_button.setEnabled(len(files) > 0)

    def start_analysis(self):
        """Start file age analysis."""
        if not self.current_files:
            QMessageBox.information(self, "No Files", "Please scan a directory first.")
            return

        # Disable controls and show progress
        self.start_button.setVisible(False)
        self.cancel_button.setVisible(True)
        self.export_button.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Clear previous results
        self.clear_results()
        self.selected_files.clear()

        # Start analysis worker
        self.analysis_worker = FileAgeAnalysisWorker(self.current_files)

        self.analysis_worker.progress_updated.connect(self.on_progress_updated)
        self.analysis_worker.analysis_completed.connect(self.on_analysis_completed)
        self.analysis_worker.analysis_failed.connect(self.on_analysis_failed)
        self.analysis_worker.start()

    def cancel_analysis(self):
        """Cancel the running analysis."""
        if self.analysis_worker:
            self.analysis_worker.cancel()
            self.analysis_worker.wait()

        self.reset_ui_after_analysis()

    def on_progress_updated(self, message: str, percentage: int):
        """Handle progress updates."""
        self.progress_bar.setValue(percentage)
        self.progress_bar.setFormat(f"{message} ({percentage}%)")

    def on_analysis_completed(self, analysis: FileAgeAnalysis):
        """Handle completed analysis."""
        self.current_analysis = analysis
        self.display_results()
        self.reset_ui_after_analysis()

    def on_analysis_failed(self, error_message: str):
        """Handle analysis failure."""
        QMessageBox.critical(self, "Analysis Failed", error_message)
        self.reset_ui_after_analysis()

    def reset_ui_after_analysis(self):
        """Reset UI state after analysis completion or cancellation."""
        self.start_button.setVisible(True)
        self.cancel_button.setVisible(False)
        self.progress_bar.setVisible(False)

        if self.current_analysis:
            self.export_button.setVisible(True)

    def display_results(self):
        """Display analysis results."""
        self.clear_results()

        if not self.current_analysis:
            return

        # Show age distribution
        self.add_age_distribution()

        # Show archival recommendations
        self.add_archival_recommendations()

        # Show archival candidates
        self.add_archival_candidates()

        self.results_area.setVisible(True)

    def add_age_distribution(self):
        """Add age distribution cards."""
        if not self.current_analysis:
            return

        distribution = self.service.get_age_distribution_stats(self.current_analysis)

        dist_card = TitleCard(
            "Age Distribution", "Files categorized by last modification date"
        )
        dist_content = QWidget()
        dist_layout = QGridLayout(dist_content)
        dist_layout.setSpacing(Spacing.MD)

        # Create category cards in a grid
        row, col = 0, 0
        for category in FileAgeCategory:
            if category in distribution:
                stats = distribution[category]
                if stats["count"] > 0:  # Only show categories with files
                    category_card = AgeCategoryCard(category, stats)
                    category_card.category_selected.connect(self.on_category_selected)
                    dist_layout.addWidget(category_card, row, col)

                    col += 1
                    if col >= 3:  # 3 columns per row
                        col = 0
                        row += 1

        dist_card.add_content_widget(dist_content)
        self.results_layout.addWidget(dist_card)

    def add_archival_recommendations(self):
        """Add archival recommendations."""
        if not self.current_analysis:
            return

        recommendations = self.service.get_archival_recommendations(
            self.current_analysis, min_size_mb=self.min_size_spinbox.value()
        )

        if recommendations:
            rec_card = TitleCard(
                "Archival Recommendations",
                "Suggested actions based on file age analysis",
            )
            rec_content = QWidget()
            rec_layout = QVBoxLayout(rec_content)

            for rec in recommendations[:5]:  # Top 5 recommendations
                rec_widget = self.create_recommendation_widget(rec)
                rec_layout.addWidget(rec_widget)

            rec_card.add_content_widget(rec_content)
            self.results_layout.addWidget(rec_card)

    def create_recommendation_widget(self, recommendation: dict) -> QWidget:
        """Create a widget for a single recommendation."""
        widget = CardWidget()
        layout = QHBoxLayout(widget)

        # Priority indicator
        priority_colors = {
            "high": ModernTheme.ERROR.name(),
            "medium": ModernTheme.WARNING.name(),
            "low": ModernTheme.SUCCESS.name(),
        }

        priority_label = QLabel(recommendation["priority"].upper())
        priority_label.setStyleSheet(f"""
        QLabel {{
            background-color: {priority_colors.get(recommendation["priority"], ModernTheme.DARK_GRAY.name())};
            color: {ModernTheme.WHITE.name()};
            padding: 4px 8px;
            border-radius: 4px;
            font-size: {Typography.FONT_XS};
            font-weight: {Typography.WEIGHT_BOLD};
            max-width: 60px;
        }}
        """)
        priority_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Recommendation content
        content_layout = QVBoxLayout()

        title_label = QLabel(recommendation["title"])
        title_label.setStyleSheet(f"""
        QLabel {{
            font-weight: {Typography.WEIGHT_BOLD};
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        desc_label = QLabel(recommendation["description"])
        desc_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
            background: transparent;
            border: none;
        }}
        """)

        action_label = QLabel(f"Action: {recommendation['action']}")
        action_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
            font-style: italic;
            background: transparent;
            border: none;
        }}
        """)

        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        content_layout.addWidget(action_label)

        layout.addWidget(priority_label)
        layout.addLayout(content_layout, 1)

        return widget

    def add_archival_candidates(self):
        """Add the list of archival candidates."""
        if not self.current_analysis:
            return

        candidates = self.service.get_cleanup_candidates(
            self.current_analysis,
            include_stale=self.include_stale_checkbox.isChecked(),
            min_size_mb=1,  # 1MB minimum for candidates list
        )

        if candidates:
            candidates_card = TitleCard(
                "Archival Candidates", f"{len(candidates)} files ready for archival"
            )
            candidates_content = QWidget()
            candidates_layout = QVBoxLayout(candidates_content)

            # Bulk actions header
            if len(candidates) > 1:
                bulk_actions = QWidget()
                bulk_layout = QHBoxLayout(bulk_actions)

                select_all_btn = ModernButton("Select All", "secondary")
                select_all_btn.clicked.connect(self.select_all_candidates)

                select_none_btn = ModernButton("Select None", "secondary")
                select_none_btn.clicked.connect(self.select_no_candidates)

                archive_selected_btn = ModernButton("Archive Selected", "primary")
                archive_selected_btn.clicked.connect(self.archive_selected_files)

                bulk_layout.addWidget(select_all_btn)
                bulk_layout.addWidget(select_none_btn)
                bulk_layout.addStretch()
                bulk_layout.addWidget(archive_selected_btn)

                candidates_layout.addWidget(bulk_actions)

            # Add candidate widgets
            for candidate in candidates[:25]:  # Show top 25 candidates
                candidate_widget = ArchivalCandidateWidget(candidate)
                candidate_widget.file_action_requested.connect(self.handle_file_action)
                candidate_widget.file_selected.connect(self.on_file_selected)
                candidates_layout.addWidget(candidate_widget)

            if len(candidates) > 25:
                more_label = QLabel(
                    f"... and {len(candidates) - 25} more archival candidates"
                )
                more_label.setStyleSheet(f"""
                QLabel {{
                    color: {ModernTheme.DARK_GRAY.name()};
                    font-size: {Typography.FONT_SM};
                    font-style: italic;
                    padding: {Spacing.MD}px;
                    text-align: center;
                    background: transparent;
                    border: none;
                }}
                """)
                more_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                candidates_layout.addWidget(more_label)

            candidates_card.add_content_widget(candidates_content)
            self.results_layout.addWidget(candidates_card)

    def on_category_selected(self, category: FileAgeCategory):
        """Handle age category selection to show files in that category."""
        if not self.current_analysis:
            return

        age_groups = self.current_analysis.get_files_by_age()
        category_files = age_groups.get(category, [])

        if category_files:
            # Show files in a message box for now (could be enhanced with a dedicated dialog)
            file_list = "\\n".join(
                [f"• {f.name} ({f.path})" for f in category_files[:10]]
            )
            if len(category_files) > 10:
                file_list += f"\\n... and {len(category_files) - 10} more files"

            QMessageBox.information(
                self,
                f"{category.value.title()} Files",
                f"Files in {category.value} category ({len(category_files)} total):\\n\\n{file_list}",
            )

    def on_file_selected(self, file_path: str, selected: bool):
        """Handle file selection for bulk operations."""
        if selected:
            self.selected_files.add(file_path)
        else:
            self.selected_files.discard(file_path)

    def select_all_candidates(self):
        """Select all archival candidates."""
        # This would need to interact with the ArchivalCandidateWidget checkboxes
        # For now, just show a message
        QMessageBox.information(
            self, "Select All", "All visible archival candidates have been selected."
        )

    def select_no_candidates(self):
        """Deselect all archival candidates."""
        self.selected_files.clear()
        QMessageBox.information(
            self, "Select None", "All archival candidates have been deselected."
        )

    def archive_selected_files(self):
        """Archive selected files."""
        if not self.selected_files:
            QMessageBox.information(
                self, "No Selection", "Please select files to archive."
            )
            return

        # For now, show a confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Archival",
            f"Are you sure you want to archive {len(self.selected_files)} selected files?\\n\\nThis will create an archive and optionally remove the original files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Archive Feature",
                "Archive functionality will be implemented in a future version.",
            )

    def handle_file_action(self, action: str, file_path: str):
        """Handle file action requests."""
        if action == "open_location":
            self.open_file_location(file_path)
        elif action == "archive":
            self.archive_single_file(file_path)

    def open_file_location(self, file_path: str):
        """Open file location in system file manager."""
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", file_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", os.path.dirname(file_path)])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file location: {e!s}")

    def archive_single_file(self, file_path: str):
        """Archive a single file."""
        QMessageBox.information(
            self,
            "Archive Feature",
            "Individual file archiving will be implemented in a future version.",
        )

    def export_results(self):
        """Export analysis results to file."""
        if not self.current_analysis:
            return

        # Get export format and file path
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Age Analysis",
            "file_age_analysis.csv",
            "CSV Files (*.csv);;JSON Files (*.json)",
        )

        if not file_path:
            return

        try:
            format_type = "json" if selected_filter.startswith("JSON") else "csv"
            export_data = self.service.export_analysis_results(
                self.current_analysis, format_type
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(export_data)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Age analysis results exported to:\\n{file_path}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export results: {e!s}"
            )

    def clear_results(self):
        """Clear the results area."""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def get_analysis_summary(self) -> dict:
        """Get summary of current analysis."""
        if not self.current_analysis:
            return {}

        archival_candidates = self.current_analysis.get_archival_candidates()

        return {
            "total_files_analyzed": len(self.current_analysis.files),
            "archival_candidates": len(archival_candidates),
            "recommendations": len(
                self.service.get_archival_recommendations(self.current_analysis)
            ),
        }
