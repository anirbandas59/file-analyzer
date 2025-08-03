#!/usr/bin/env python3
# File: src/ui/components/management/tools/large_file_analyzer.py

import os
import platform
import subprocess

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
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
from ...card_widget import CardWidget, StatsCard, TitleCard
from ...modern_button import ModernButton
from ..models.management_data import FileInfo, FileSizeCategory, LargeFileAnalysis
from ..services.large_file_service import LargeFileAnalysisService
from ..workers.analysis_workers import LargeFileAnalysisWorker


class LargeFileItemWidget(CardWidget):
    """Widget for displaying a single large file with actions."""

    file_action_requested = pyqtSignal(str, str)  # action, file_path

    def __init__(self, file_info: FileInfo, rank: int, parent=None):
        super().__init__(parent)

        self.file_info = file_info
        self.rank = rank
        self.setup_ui()

    def setup_ui(self):
        """Setup the file item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        layout.setSpacing(Spacing.MD)

        # Rank badge
        rank_label = QLabel(f"#{self.rank}")
        rank_label.setStyleSheet(f"""
        QLabel {{
            background-color: {ModernTheme.PRIMARY.name()};
            color: {ModernTheme.WHITE.name()};
            padding: 4px 8px;
            border-radius: 12px;
            font-size: {Typography.FONT_SM};
            font-weight: {Typography.WEIGHT_BOLD};
            min-width: 24px;
            max-width: 40px;
        }}
        """)
        rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # File info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # File name and size
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

        from src.utils.file_utils import format_size

        size_label = QLabel(format_size(self.file_info.size))
        size_label.setStyleSheet(f"""
        QLabel {{
            background-color: {self._get_size_category_color()};
            color: {ModernTheme.WHITE.name()};
            padding: 2px 8px;
            border-radius: 4px;
            font-size: {Typography.FONT_SM};
            font-weight: {Typography.WEIGHT_BOLD};
        }}
        """)

        name_layout.addWidget(name_label)
        name_layout.addStretch()
        name_layout.addWidget(size_label)

        # File details
        details_text = f"{self.file_info.path} • {self.file_info.file_type.upper()} • Modified: {self.file_info.modified.strftime('%Y-%m-%d')}"
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

        open_btn = ModernButton("Open Location", "secondary")
        open_btn.setMaximumWidth(120)
        open_btn.clicked.connect(
            lambda: self.file_action_requested.emit(
                "open_location", self.file_info.path
            )
        )

        delete_btn = ModernButton("Delete", "danger")
        delete_btn.setMaximumWidth(80)
        delete_btn.clicked.connect(
            lambda: self.file_action_requested.emit("delete", self.file_info.path)
        )

        actions_layout.addWidget(open_btn)
        actions_layout.addWidget(delete_btn)

        # Assemble layout
        layout.addWidget(rank_label)
        layout.addLayout(info_layout, 1)
        layout.addLayout(actions_layout)

    def _get_size_category_color(self) -> str:
        """Get color based on file size category."""
        colors = {
            FileSizeCategory.SMALL: ModernTheme.SUCCESS.name(),
            FileSizeCategory.MEDIUM: ModernTheme.WARNING.name(),
            FileSizeCategory.LARGE: ModernTheme.ERROR.name(),
            FileSizeCategory.HUGE: ModernTheme.ERROR.name(),
            FileSizeCategory.MASSIVE: ModernTheme.ERROR.name(),
        }
        return colors.get(self.file_info.size_category, ModernTheme.DARK_GRAY.name())


class LargeFileAnalyzerTool(QWidget):
    """Main large file analyzer and management tool."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_files = []
        self.current_analysis = None
        self.analysis_worker = None
        self.service = LargeFileAnalysisService()

        self.setup_ui()

    def setup_ui(self):
        """Setup the large file analyzer UI."""
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
            "Large File Analyzer",
            "Identify and manage the largest files consuming disk space",
        )
        layout.addWidget(header_card)

    def setup_configuration(self, layout):
        """Setup configuration controls."""
        config_card = CardWidget()
        config_layout = QVBoxLayout(config_card)

        # Configuration options
        options_layout = QHBoxLayout()

        # Size threshold
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Size threshold (MB):")
        threshold_label.setStyleSheet(f"""
        QLabel {{
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(1, 10000)
        self.threshold_spinbox.setValue(100)
        self.threshold_spinbox.setSuffix(" MB")
        self.threshold_spinbox.setStyleSheet(f"""
        QSpinBox {{
            padding: 6px;
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: 4px;
            font-size: {Typography.FONT_MD};
            background: {ModernTheme.WHITE.name()};
        }}
        """)

        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_spinbox)

        # Sort options
        sort_layout = QHBoxLayout()
        sort_label = QLabel("Sort by:")
        sort_label.setStyleSheet(f"""
        QLabel {{
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(
            [
                "Size (Largest First)",
                "Size (Smallest First)",
                "Name",
                "Path",
                "Date Modified",
                "File Type",
            ]
        )
        self.sort_combo.setStyleSheet(f"""
        QComboBox {{
            padding: 6px;
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: 4px;
            font-size: {Typography.FONT_MD};
            background: {ModernTheme.WHITE.name()};
            min-width: 150px;
        }}
        """)

        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)

        # Analysis options
        self.include_age_checkbox = QCheckBox("Consider file age in recommendations")
        self.include_age_checkbox.setChecked(True)
        self.include_age_checkbox.setStyleSheet(f"""
        QCheckBox {{
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
        }}
        """)

        options_layout.addLayout(threshold_layout)
        options_layout.addLayout(sort_layout)
        options_layout.addWidget(self.include_age_checkbox)
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
        """Start large file analysis."""
        if not self.current_files:
            QMessageBox.information(self, "No Files", "Please scan a directory first.")
            return

        # Get configuration
        threshold_mb = self.threshold_spinbox.value()
        threshold_bytes = threshold_mb * 1024 * 1024

        # Disable controls and show progress
        self.start_button.setVisible(False)
        self.cancel_button.setVisible(True)
        self.export_button.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Clear previous results
        self.clear_results()

        # Start analysis worker
        self.analysis_worker = LargeFileAnalysisWorker(
            self.current_files, threshold_bytes
        )

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

    def on_analysis_completed(self, analysis: LargeFileAnalysis):
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

        if self.current_analysis and self.current_analysis.files:
            self.export_button.setVisible(True)

    def display_results(self):
        """Display analysis results."""
        self.clear_results()

        if not self.current_analysis or not self.current_analysis.files:
            # No large files found
            no_results_label = QLabel("No large files found above the threshold!")
            no_results_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.SUCCESS.name()};
                font-size: {Typography.FONT_LG};
                font-weight: {Typography.WEIGHT_BOLD};
                padding: {Spacing.XL}px;
                text-align: center;
                background: transparent;
                border: none;
            }}
            """)
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(no_results_label)
        else:
            # Show summary statistics
            self.add_summary_stats()

            # Show recommendations
            self.add_recommendations()

            # Show large files
            self.add_large_files_list()

        self.results_area.setVisible(True)

    def add_summary_stats(self):
        """Add summary statistics card."""
        if not self.current_analysis:
            return

        from src.utils.file_utils import format_size

        total_size = sum(f.size for f in self.current_analysis.files)
        avg_size = (
            total_size // len(self.current_analysis.files)
            if self.current_analysis.files
            else 0
        )

        summary_card = CardWidget()
        summary_layout = QHBoxLayout(summary_card)

        files_stat = StatsCard(
            "Large Files Found", str(len(self.current_analysis.files))
        )
        total_size_stat = StatsCard("Total Size", format_size(total_size))
        avg_size_stat = StatsCard("Average Size", format_size(avg_size))
        threshold_stat = StatsCard(
            "Size Threshold", format_size(self.current_analysis.size_threshold)
        )

        summary_layout.addWidget(files_stat)
        summary_layout.addWidget(total_size_stat)
        summary_layout.addWidget(avg_size_stat)
        summary_layout.addWidget(threshold_stat)

        self.results_layout.addWidget(summary_card)

    def add_recommendations(self):
        """Add cleanup recommendations."""
        if not self.current_analysis:
            return

        recommendations = self.service.generate_detailed_recommendations(
            self.current_analysis
        )

        if recommendations:
            rec_card = TitleCard(
                "Cleanup Recommendations", "Suggested actions to optimize disk space"
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

    def add_large_files_list(self):
        """Add the list of large files."""
        if not self.current_analysis or not self.current_analysis.files:
            return

        files_card = TitleCard(
            "Large Files", f"Files larger than {self.threshold_spinbox.value()} MB"
        )
        files_content = QWidget()
        files_layout = QVBoxLayout(files_content)

        # Sort files based on current selection
        sorted_files = self._sort_files(self.current_analysis.files)

        for i, file_info in enumerate(sorted_files[:50], 1):  # Show top 50
            file_widget = LargeFileItemWidget(file_info, i)
            file_widget.file_action_requested.connect(self.handle_file_action)
            files_layout.addWidget(file_widget)

        if len(self.current_analysis.files) > 50:
            more_label = QLabel(
                f"... and {len(self.current_analysis.files) - 50} more files"
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
            files_layout.addWidget(more_label)

        files_card.add_content_widget(files_content)
        self.results_layout.addWidget(files_card)

    def _sort_files(self, files: list[FileInfo]) -> list[FileInfo]:
        """Sort files based on current selection."""
        sort_option = self.sort_combo.currentText()

        if sort_option == "Size (Largest First)":
            return sorted(files, key=lambda f: f.size, reverse=True)
        elif sort_option == "Size (Smallest First)":
            return sorted(files, key=lambda f: f.size)
        elif sort_option == "Name":
            return sorted(files, key=lambda f: f.name.lower())
        elif sort_option == "Path":
            return sorted(files, key=lambda f: f.path.lower())
        elif sort_option == "Date Modified":
            return sorted(files, key=lambda f: f.modified, reverse=True)
        elif sort_option == "File Type":
            return sorted(files, key=lambda f: f.file_type.lower())
        else:
            return files

    def handle_file_action(self, action: str, file_path: str):
        """Handle file action requests."""
        if action == "open_location":
            self.open_file_location(file_path)
        elif action == "delete":
            self.delete_file(file_path)

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

    def delete_file(self, file_path: str):
        """Delete file with confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete this file?\n\n{file_path}\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(file_path)
                QMessageBox.information(self, "Success", "File deleted successfully.")

                # Refresh the analysis by removing the file from current results
                if self.current_analysis:
                    self.current_analysis.files = [
                        f for f in self.current_analysis.files if f.path != file_path
                    ]
                    self.display_results()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete file: {e!s}")

    def export_results(self):
        """Export analysis results to file."""
        if not self.current_analysis:
            return

        # Get export format and file path
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Large File Analysis",
            "large_file_analysis.csv",
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
                self, "Export Successful", f"Analysis results exported to:\n{file_path}"
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

        total_size = sum(f.size for f in self.current_analysis.files)

        return {
            "large_files_count": len(self.current_analysis.files),
            "total_large_file_size": total_size,
            "threshold_mb": self.threshold_spinbox.value(),
            "recommendations": len(
                self.service.generate_detailed_recommendations(self.current_analysis)
            ),
        }
