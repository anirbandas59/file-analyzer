#!/usr/bin/env python3
# File: src/ui/components/management/tools/duplicate_finder.py

import os
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QPushButton, QFrame, QScrollArea,
                             QMessageBox, QSplitter, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ...card_widget import CardWidget, TitleCard, StatsCard
from ...modern_button import ModernButton
from ....themes.styles import ModernTheme, Typography, Spacing
from ..models.management_data import DuplicateGroup, DuplicateConfidence, FileInfo
from ..workers.analysis_workers import DuplicateAnalysisWorker

class DuplicateGroupWidget(CardWidget):
    """Widget for displaying and managing a single duplicate group."""
    
    files_selected = pyqtSignal(list, object)  # selected_files, group
    preview_requested = pyqtSignal(str)        # file_path
    
    def __init__(self, duplicate_group: DuplicateGroup, parent=None):
        super().__init__(parent)
        
        self.duplicate_group = duplicate_group
        self.file_checkboxes = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the duplicate group UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)
        
        # Header with group info
        self.setup_header(layout)
        
        # File list
        self.setup_file_list(layout)
        
        # Action buttons
        self.setup_actions(layout)
        
    def setup_header(self, layout):
        """Setup the group header with statistics."""
        header_layout = QHBoxLayout()
        
        # Group info
        confidence_color = {
            DuplicateConfidence.HIGH: ModernTheme.SUCCESS.name(),
            DuplicateConfidence.MEDIUM: ModernTheme.WARNING.name(),
            DuplicateConfidence.LOW: ModernTheme.ERROR.name()
        }
        
        confidence_label = QLabel(f"Confidence: {self.duplicate_group.confidence.value.title()}")
        confidence_label.setStyleSheet(f"""
        QLabel {{
            color: {confidence_color.get(self.duplicate_group.confidence, ModernTheme.DARK_GRAY.name())};
            font-weight: {Typography.WEIGHT_BOLD};
            font-size: {Typography.FONT_MD};
            background: transparent;
            border: none;
        }}
        """)
        
        # Space savings info
        from src.utils.file_utils import format_size
        savings_text = f"Potential savings: {format_size(self.duplicate_group.potential_savings)}"
        savings_label = QLabel(savings_text)
        savings_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
            background: transparent;
            border: none;
        }}
        """)
        
        header_layout.addWidget(confidence_label)
        header_layout.addStretch()
        header_layout.addWidget(savings_label)
        
        layout.addLayout(header_layout)
        
    def setup_file_list(self, layout):
        """Setup the file list with checkboxes."""
        files_frame = QFrame()
        files_frame.setFrameShape(QFrame.Shape.StyledPanel)
        files_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {ModernTheme.LIGHT_GRAY.name()};
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: 4px;
        }}
        """)
        
        files_layout = QVBoxLayout(files_frame)
        files_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        
        # Get recommended keeper
        recommended_keeper = self.duplicate_group.get_recommended_keeper()
        
        for file in self.duplicate_group.files:
            file_widget = self.create_file_widget(file, file == recommended_keeper)
            files_layout.addWidget(file_widget)
            
        layout.addWidget(files_frame)
        
    def create_file_widget(self, file: FileInfo, is_recommended_keeper: bool):
        """Create a widget for a single file in the duplicate group."""
        file_widget = QWidget()
        file_layout = QHBoxLayout(file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        # Checkbox for selection
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.on_file_selection_changed)
        
        # Pre-select files for removal (not the recommended keeper)
        if not is_recommended_keeper:
            checkbox.setChecked(True)
        
        self.file_checkboxes[file.path] = checkbox
        
        # File info
        file_info_layout = QVBoxLayout()
        file_info_layout.setSpacing(2)
        
        # File name and recommended badge
        name_layout = QHBoxLayout()
        name_label = QLabel(file.name)
        name_label.setStyleSheet(f"""
        QLabel {{
            font-weight: {Typography.WEIGHT_MEDIUM};
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background: transparent;
            border: none;
        }}
        """)
        
        name_layout.addWidget(name_label)
        
        if is_recommended_keeper:
            recommended_label = QLabel("RECOMMENDED KEEPER")
            recommended_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.SUCCESS.name()};
                color: {ModernTheme.WHITE.name()};
                padding: 2px 6px;
                border-radius: 3px;
                font-size: {Typography.FONT_XS};
                font-weight: {Typography.WEIGHT_BOLD};
            }}
            """)
            name_layout.addWidget(recommended_label)
            
        name_layout.addStretch()
        file_info_layout.addLayout(name_layout)
        
        # File details
        from src.utils.file_utils import format_size
        details_text = f"{file.path} • {format_size(file.size)} • {file.modified.strftime('%Y-%m-%d %H:%M')}"
        details_label = QLabel(details_text)
        details_label.setStyleSheet(f"""
        QLabel {{
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
            background: transparent;
            border: none;
        }}
        """)
        file_info_layout.addWidget(details_label)
        
        # Preview button
        preview_button = ModernButton("Preview", "secondary")
        preview_button.setMaximumWidth(80)
        preview_button.clicked.connect(lambda: self.preview_requested.emit(file.path))
        
        file_layout.addWidget(checkbox)
        file_layout.addLayout(file_info_layout, 1)
        file_layout.addWidget(preview_button)
        
        return file_widget
        
    def setup_actions(self, layout):
        """Setup action buttons."""
        actions_layout = QHBoxLayout()
        
        # Select all/none buttons
        select_all_btn = ModernButton("Select All", "secondary")
        select_all_btn.clicked.connect(self.select_all_files)
        
        select_none_btn = ModernButton("Select None", "secondary")
        select_none_btn.clicked.connect(self.select_no_files)
        
        # Remove selected button
        remove_btn = ModernButton("Remove Selected", "danger")
        remove_btn.clicked.connect(self.remove_selected_files)
        
        actions_layout.addWidget(select_all_btn)
        actions_layout.addWidget(select_none_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(remove_btn)
        
        layout.addLayout(actions_layout)
        
    def on_file_selection_changed(self):
        """Handle file selection changes."""
        selected_files = self.get_selected_files()
        self.files_selected.emit(selected_files, self.duplicate_group)
        
    def get_selected_files(self) -> List[FileInfo]:
        """Get list of selected files."""
        selected_files = []
        for file in self.duplicate_group.files:
            checkbox = self.file_checkboxes.get(file.path)
            if checkbox and checkbox.isChecked():
                selected_files.append(file)
        return selected_files
        
    def select_all_files(self):
        """Select all files in the group."""
        for checkbox in self.file_checkboxes.values():
            checkbox.setChecked(True)
            
    def select_no_files(self):
        """Deselect all files in the group."""
        for checkbox in self.file_checkboxes.values():
            checkbox.setChecked(False)
            
    def remove_selected_files(self):
        """Remove selected files (with confirmation)."""
        selected_files = self.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "No Selection", "Please select files to remove.")
            return
            
        # Confirmation dialog
        file_list = "\\n".join([f"• {file.name}" for file in selected_files[:5]])
        if len(selected_files) > 5:
            file_list += f"\\n... and {len(selected_files) - 5} more files"
            
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete these {len(selected_files)} files?\\n\\n{file_list}\\n\\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_files(selected_files)
            
    def delete_files(self, files: List[FileInfo]):
        """Delete the specified files."""
        success_count = 0
        failed_files = []
        
        for file in files:
            try:
                os.remove(file.path)
                success_count += 1
                
                # Remove from UI
                checkbox = self.file_checkboxes.get(file.path)
                if checkbox:
                    checkbox.parent().setVisible(False)
                    del self.file_checkboxes[file.path]
                    
            except Exception as e:
                failed_files.append(f"{file.name}: {str(e)}")
        
        # Show results
        if success_count > 0:
            QMessageBox.information(self, "Success", f"Successfully deleted {success_count} files.")
            
        if failed_files:
            error_message = "\\n".join(failed_files)
            QMessageBox.warning(self, "Some Deletions Failed", f"Failed to delete:\\n{error_message}")

class DuplicateFinderTool(QWidget):
    """Main duplicate file finder and management tool."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_files = []
        self.duplicate_groups = []
        self.analysis_worker = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the duplicate finder UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.MD)
        
        # Header
        self.setup_header(layout)
        
        # Controls
        self.setup_controls(layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results area
        self.setup_results_area(layout)
        
    def setup_header(self, layout):
        """Setup the tool header."""
        header_card = TitleCard("Duplicate File Finder", "Find and manage duplicate files to free up disk space")
        layout.addWidget(header_card)
        
    def setup_controls(self, layout):
        """Setup analysis controls."""
        controls_card = CardWidget()
        controls_layout = QVBoxLayout(controls_card)
        
        # Analysis options
        options_layout = QHBoxLayout()
        
        self.use_content_hash = QCheckBox("Content-based detection (slower, more accurate)")
        self.use_content_hash.setChecked(True)
        
        self.use_heuristics = QCheckBox("Quick heuristic detection (faster, less accurate)")
        self.use_heuristics.setChecked(True)
        
        options_layout.addWidget(self.use_content_hash)
        options_layout.addWidget(self.use_heuristics)
        options_layout.addStretch()
        
        # Action buttons
        self.start_button = ModernButton("Start Analysis", "primary")
        self.start_button.clicked.connect(self.start_analysis)
        
        self.cancel_button = ModernButton("Cancel", "secondary")
        self.cancel_button.clicked.connect(self.cancel_analysis)
        self.cancel_button.setVisible(False)
        
        options_layout.addWidget(self.start_button)
        options_layout.addWidget(self.cancel_button)
        
        controls_layout.addLayout(options_layout)
        layout.addWidget(controls_card)
        
    def setup_results_area(self, layout):
        """Setup the results display area."""
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_area.setVisible(False)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(Spacing.MD)
        
        self.results_area.setWidget(self.results_widget)
        layout.addWidget(self.results_area, 1)  # Take remaining space
        
    def update_files(self, files: List[Dict]):
        """Update the files to analyze."""
        self.current_files = files
        self.start_button.setEnabled(len(files) > 0)
        
    def start_analysis(self):
        """Start duplicate file analysis."""
        if not self.current_files:
            QMessageBox.information(self, "No Files", "Please scan a directory first.")
            return
            
        # Disable controls and show progress
        self.start_button.setVisible(False)
        self.cancel_button.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Clear previous results
        self.clear_results()
        
        # Start analysis worker
        self.analysis_worker = DuplicateAnalysisWorker(
            self.current_files,
            self.use_content_hash.isChecked(),
            self.use_heuristics.isChecked()
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
        
    def on_analysis_completed(self, duplicate_groups: List[DuplicateGroup]):
        """Handle completed analysis."""
        self.duplicate_groups = duplicate_groups
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
        
    def display_results(self):
        """Display analysis results."""
        self.clear_results()
        
        if not self.duplicate_groups:
            # No duplicates found
            no_results_label = QLabel("No duplicate files found!")
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
            
            # Show duplicate groups
            for group in self.duplicate_groups:
                group_widget = DuplicateGroupWidget(group)
                group_widget.files_selected.connect(self.on_files_selected)
                group_widget.preview_requested.connect(self.on_preview_requested)
                self.results_layout.addWidget(group_widget)
        
        self.results_area.setVisible(True)
        
    def add_summary_stats(self):
        """Add summary statistics card."""
        total_files = sum(len(group.files) for group in self.duplicate_groups)
        total_savings = sum(group.potential_savings for group in self.duplicate_groups)
        
        from src.utils.file_utils import format_size
        
        summary_card = CardWidget()
        summary_layout = QHBoxLayout(summary_card)
        
        groups_stat = StatsCard("Duplicate Groups", str(len(self.duplicate_groups)))
        files_stat = StatsCard("Total Files", str(total_files))
        savings_stat = StatsCard("Potential Savings", format_size(total_savings))
        
        summary_layout.addWidget(groups_stat)
        summary_layout.addWidget(files_stat)
        summary_layout.addWidget(savings_stat)
        
        self.results_layout.addWidget(summary_card)
        
    def clear_results(self):
        """Clear the results area."""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
                
    def on_files_selected(self, selected_files: List[FileInfo], group: DuplicateGroup):
        """Handle file selection in a duplicate group."""
        # Could be used for batch operations across groups
        pass
        
    def on_preview_requested(self, file_path: str):
        """Handle file preview request."""
        # Simple preview - could be enhanced with actual preview window
        QMessageBox.information(self, "File Preview", f"File: {file_path}\\n\\nPreview functionality will be enhanced in future versions.")
        
    def get_analysis_summary(self) -> Dict:
        """Get summary of current analysis."""
        if not self.duplicate_groups:
            return {}
            
        total_files = sum(len(group.files) for group in self.duplicate_groups)
        total_savings = sum(group.potential_savings for group in self.duplicate_groups)
        
        return {
            'duplicate_groups': len(self.duplicate_groups),
            'total_files': total_files,
            'potential_savings': total_savings,
            'high_confidence_groups': len([g for g in self.duplicate_groups if g.confidence == DuplicateConfidence.HIGH])
        }