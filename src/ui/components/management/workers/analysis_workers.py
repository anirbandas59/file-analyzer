#!/usr/bin/env python3
# File: src/ui/components/management/workers/analysis_workers.py

import time
from typing import List, Dict, Optional
from PyQt6.QtCore import QThread, pyqtSignal, QMutex

from ..services.duplicate_service import DuplicateDetectionService
from ..models.management_data import DuplicateGroup, LargeFileAnalysis, FileAgeAnalysis, FileInfo, FileSizeCategory

class DuplicateAnalysisWorker(QThread):
    """
    Background worker for duplicate file detection.
    Runs in a separate thread to keep UI responsive during analysis.
    """
    
    # Signals for communication with UI
    progress_updated = pyqtSignal(str, int)  # message, percentage
    analysis_completed = pyqtSignal(list)    # duplicate_groups
    analysis_failed = pyqtSignal(str)        # error_message
    
    def __init__(self, files: List[Dict], use_content_hash: bool = True, use_heuristics: bool = True):
        super().__init__()
        self.files = files
        self.use_content_hash = use_content_hash
        self.use_heuristics = use_heuristics
        self.service = DuplicateDetectionService()
        self.is_cancelled = False
        self.mutex = QMutex()
        
    def run(self):
        """Main thread execution method."""
        try:
            # Set up progress callback
            self.service.set_progress_callback(self._progress_callback)
            
            self.progress_updated.emit("Starting duplicate analysis...", 0)
            
            # Perform duplicate detection
            duplicate_groups = self.service.find_duplicates(
                self.files, 
                self.use_content_hash, 
                self.use_heuristics
            )
            
            # Check if cancelled
            self.mutex.lock()
            cancelled = self.is_cancelled
            self.mutex.unlock()
            
            if not cancelled:
                self.analysis_completed.emit(duplicate_groups)
            
        except Exception as e:
            self.analysis_failed.emit(f"Duplicate analysis failed: {str(e)}")
    
    def _progress_callback(self, message: str, percentage: int):
        """Callback for progress updates from the service."""
        # Check if cancelled before emitting progress
        self.mutex.lock()
        cancelled = self.is_cancelled
        self.mutex.unlock()
        
        if not cancelled:
            self.progress_updated.emit(message, percentage)
    
    def cancel(self):
        """Cancel the analysis operation."""
        self.mutex.lock()
        self.is_cancelled = True
        self.mutex.unlock()

class LargeFileAnalysisWorker(QThread):
    """
    Background worker for large file analysis.
    """
    
    progress_updated = pyqtSignal(str, int)
    analysis_completed = pyqtSignal(object)  # LargeFileAnalysis
    analysis_failed = pyqtSignal(str)
    
    def __init__(self, files: List[Dict], size_threshold: int = 100 * 1024 * 1024):
        super().__init__()
        self.files = files
        self.size_threshold = size_threshold
        self.is_cancelled = False
        self.mutex = QMutex()
    
    def run(self):
        """Analyze large files."""
        try:
            self.progress_updated.emit("Analyzing file sizes...", 0)
            
            # Convert to FileInfo objects
            file_infos = []
            total_files = len(self.files)
            
            for i, file_dict in enumerate(self.files):
                # Check if cancelled
                self.mutex.lock()
                cancelled = self.is_cancelled
                self.mutex.unlock()
                
                if cancelled:
                    return
                
                file_info = FileInfo(
                    name=file_dict['name'],
                    path=file_dict['path'],
                    size=file_dict['size'],
                    modified=file_dict['modified'],
                    file_type=file_dict['type']
                )
                
                # Only include files above threshold
                if file_info.size >= self.size_threshold:
                    file_infos.append(file_info)
                
                # Update progress
                progress = int((i / total_files) * 100)
                self.progress_updated.emit(f"Processed {i+1}/{total_files} files", progress)
            
            # Sort by size (largest first)
            file_infos.sort(key=lambda f: f.size, reverse=True)
            
            # Create analysis result
            analysis = LargeFileAnalysis(
                files=file_infos,
                size_threshold=self.size_threshold
            )
            
            self.progress_updated.emit("Large file analysis complete", 100)
            self.analysis_completed.emit(analysis)
            
        except Exception as e:
            self.analysis_failed.emit(f"Large file analysis failed: {str(e)}")
    
    def cancel(self):
        """Cancel the analysis."""
        self.mutex.lock()
        self.is_cancelled = True
        self.mutex.unlock()

class FileAgeAnalysisWorker(QThread):
    """
    Background worker for file age analysis.
    """
    
    progress_updated = pyqtSignal(str, int)
    analysis_completed = pyqtSignal(object)  # FileAgeAnalysis
    analysis_failed = pyqtSignal(str)
    
    def __init__(self, files: List[Dict]):
        super().__init__()
        self.files = files
        self.is_cancelled = False
        self.mutex = QMutex()
    
    def run(self):
        """Analyze file ages."""
        try:
            self.progress_updated.emit("Analyzing file ages...", 0)
            
            # Convert to FileInfo objects
            file_infos = []
            total_files = len(self.files)
            
            for i, file_dict in enumerate(self.files):
                # Check if cancelled
                self.mutex.lock()
                cancelled = self.is_cancelled
                self.mutex.unlock()
                
                if cancelled:
                    return
                
                file_info = FileInfo(
                    name=file_dict['name'],
                    path=file_dict['path'],
                    size=file_dict['size'],
                    modified=file_dict['modified'],
                    file_type=file_dict['type']
                )
                file_infos.append(file_info)
                
                # Update progress
                progress = int((i / total_files) * 100)
                self.progress_updated.emit(f"Processed {i+1}/{total_files} files", progress)
            
            # Create analysis result
            analysis = FileAgeAnalysis(files=file_infos)
            
            self.progress_updated.emit("File age analysis complete", 100)
            self.analysis_completed.emit(analysis)
            
        except Exception as e:
            self.analysis_failed.emit(f"File age analysis failed: {str(e)}")
    
    def cancel(self):
        """Cancel the analysis."""
        self.mutex.lock()
        self.is_cancelled = True
        self.mutex.unlock()

class BatchAnalysisWorker(QThread):
    """
    Worker that runs all analysis types in sequence.
    """
    
    progress_updated = pyqtSignal(str, int)
    duplicate_analysis_completed = pyqtSignal(list)
    large_file_analysis_completed = pyqtSignal(object)
    age_analysis_completed = pyqtSignal(object)
    all_analysis_completed = pyqtSignal()
    analysis_failed = pyqtSignal(str)
    
    def __init__(self, files: List[Dict], 
                 run_duplicates: bool = True,
                 run_large_files: bool = True, 
                 run_age_analysis: bool = True,
                 size_threshold: int = 100 * 1024 * 1024):
        super().__init__()
        self.files = files
        self.run_duplicates = run_duplicates
        self.run_large_files = run_large_files
        self.run_age_analysis = run_age_analysis
        self.size_threshold = size_threshold
        self.is_cancelled = False
        self.mutex = QMutex()
    
    def run(self):
        """Run all enabled analyses in sequence."""
        try:
            total_steps = sum([self.run_duplicates, self.run_large_files, self.run_age_analysis])
            current_step = 0
            
            # Duplicate analysis
            if self.run_duplicates and not self._is_cancelled():
                self.progress_updated.emit("Running duplicate analysis...", 
                                         int((current_step / total_steps) * 100))
                
                service = DuplicateDetectionService()
                service.set_progress_callback(self._duplicate_progress_callback)
                duplicate_groups = service.find_duplicates(self.files)
                
                if not self._is_cancelled():
                    self.duplicate_analysis_completed.emit(duplicate_groups)
                    current_step += 1
            
            # Large file analysis
            if self.run_large_files and not self._is_cancelled():
                self.progress_updated.emit("Running large file analysis...", 
                                         int((current_step / total_steps) * 100))
                
                file_infos = [self._dict_to_fileinfo(f) for f in self.files]
                large_files = [f for f in file_infos if f.size >= self.size_threshold]
                large_files.sort(key=lambda f: f.size, reverse=True)
                
                analysis = LargeFileAnalysis(files=large_files, size_threshold=self.size_threshold)
                
                if not self._is_cancelled():
                    self.large_file_analysis_completed.emit(analysis)
                    current_step += 1
            
            # Age analysis
            if self.run_age_analysis and not self._is_cancelled():
                self.progress_updated.emit("Running file age analysis...", 
                                         int((current_step / total_steps) * 100))
                
                file_infos = [self._dict_to_fileinfo(f) for f in self.files]
                analysis = FileAgeAnalysis(files=file_infos)
                
                if not self._is_cancelled():
                    self.age_analysis_completed.emit(analysis)
                    current_step += 1
            
            if not self._is_cancelled():
                self.progress_updated.emit("All analyses complete", 100)
                self.all_analysis_completed.emit()
                
        except Exception as e:
            self.analysis_failed.emit(f"Batch analysis failed: {str(e)}")
    
    def _dict_to_fileinfo(self, file_dict: Dict) -> FileInfo:
        """Convert file dictionary to FileInfo object."""
        return FileInfo(
            name=file_dict['name'],
            path=file_dict['path'],
            size=file_dict['size'],
            modified=file_dict['modified'],
            file_type=file_dict['type']
        )
    
    def _duplicate_progress_callback(self, message: str, percentage: int):
        """Progress callback for duplicate analysis."""
        if not self._is_cancelled():
            # Scale progress for the duplicate analysis portion
            scaled_progress = int(percentage * 0.33)  # Assuming duplicates is 1/3 of total work
            self.progress_updated.emit(f"Duplicates: {message}", scaled_progress)
    
    def _is_cancelled(self) -> bool:
        """Check if the operation has been cancelled."""
        self.mutex.lock()
        cancelled = self.is_cancelled
        self.mutex.unlock()
        return cancelled
    
    def cancel(self):
        """Cancel all analyses."""
        self.mutex.lock()
        self.is_cancelled = True
        self.mutex.unlock()