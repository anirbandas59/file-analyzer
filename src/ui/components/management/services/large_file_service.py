#!/usr/bin/env python3
# File: src/ui/components/management/services/large_file_service.py

import os
from datetime import datetime

from ..models.management_data import FileInfo, FileSizeCategory, LargeFileAnalysis


class LargeFileAnalysisService:
    """
    Service for analyzing large files and generating cleanup recommendations.
    Provides size categorization, threshold analysis, and cleanup suggestions.
    """

    def __init__(self):
        self.progress_callback = None
        self.size_threshold = 100 * 1024 * 1024  # 100MB default

    def set_progress_callback(self, callback):
        """Set callback function for progress updates."""
        self.progress_callback = callback

    def set_size_threshold(self, threshold_mb: int):
        """Set the size threshold for large file identification (in MB)."""
        self.size_threshold = threshold_mb * 1024 * 1024

    def analyze_large_files(
        self, files: list[dict], sort_by: str = "size", sort_ascending: bool = False
    ) -> LargeFileAnalysis:
        """
        Analyze files for large file identification and cleanup recommendations.

        Args:
            files: List of file dictionaries from scanner
            sort_by: Sort criteria ("size", "name", "path", "modified", "type")
            sort_ascending: Sort direction

        Returns:
            LargeFileAnalysis object with results
        """
        # Convert to FileInfo objects
        file_infos = [self._dict_to_fileinfo(file_dict) for file_dict in files]
        len(file_infos)

        if self.progress_callback:
            self.progress_callback("Analyzing file sizes...", 10)

        # Filter files above threshold
        large_files = [f for f in file_infos if f.size >= self.size_threshold]

        if self.progress_callback:
            self.progress_callback("Categorizing files by size...", 30)

        # Sort files based on criteria
        if sort_by == "size":
            large_files.sort(key=lambda f: f.size, reverse=not sort_ascending)
        elif sort_by == "name":
            large_files.sort(key=lambda f: f.name.lower(), reverse=not sort_ascending)
        elif sort_by == "path":
            large_files.sort(key=lambda f: f.path.lower(), reverse=not sort_ascending)
        elif sort_by == "modified":
            large_files.sort(key=lambda f: f.modified, reverse=not sort_ascending)
        elif sort_by == "type":
            large_files.sort(
                key=lambda f: f.file_type.lower(), reverse=not sort_ascending
            )

        if self.progress_callback:
            self.progress_callback("Generating recommendations...", 60)

        # Create analysis object
        analysis = LargeFileAnalysis(
            files=large_files, size_threshold=self.size_threshold
        )

        if self.progress_callback:
            self.progress_callback("Analysis complete", 100)

        return analysis

    def _dict_to_fileinfo(self, file_dict: dict) -> FileInfo:
        """Convert file dictionary to FileInfo object."""
        return FileInfo(
            name=file_dict["name"],
            path=file_dict["path"],
            size=file_dict["size"],
            modified=file_dict["modified"],
            file_type=file_dict["type"],
        )

    def get_size_distribution(
        self, files: list[FileInfo]
    ) -> dict[FileSizeCategory, dict]:
        """
        Get detailed size distribution statistics.

        Returns:
            Dictionary with category statistics including count, total size, percentage
        """
        # Group files by size category
        categories = {}
        for category in FileSizeCategory:
            categories[category] = []

        for file in files:
            categories[file.size_category].append(file)

        # Calculate statistics
        total_files = len(files)
        total_size = sum(f.size for f in files)

        distribution = {}
        for category, category_files in categories.items():
            category_size = sum(f.size for f in category_files)
            distribution[category] = {
                "count": len(category_files),
                "total_size": category_size,
                "percentage": (len(category_files) / total_files * 100)
                if total_files > 0
                else 0,
                "size_percentage": (category_size / total_size * 100)
                if total_size > 0
                else 0,
                "files": category_files,
            }

        return distribution

    def get_cleanup_candidates(
        self, files: list[FileInfo], consider_age: bool = True, min_age_days: int = 365
    ) -> list[FileInfo]:
        """
        Get files that are candidates for cleanup based on size and optionally age.

        Args:
            files: List of files to analyze
            consider_age: Whether to factor in file age
            min_age_days: Minimum age in days for cleanup consideration

        Returns:
            List of FileInfo objects that are cleanup candidates
        """
        candidates = []

        for file in files:
            # Check if file is large enough
            if file.size < self.size_threshold:
                continue

            # Check age if required
            if consider_age:
                age_days = (datetime.now() - file.modified).days
                if age_days < min_age_days:
                    continue

            candidates.append(file)

        return candidates

    def generate_detailed_recommendations(
        self, analysis: LargeFileAnalysis
    ) -> list[dict]:
        """
        Generate detailed cleanup recommendations with action items.

        Returns:
            List of recommendation dictionaries with details and suggested actions
        """
        recommendations = []

        if not analysis.files:
            return recommendations

        # Analyze by file type
        type_analysis = self._analyze_by_file_type(analysis.files)
        for file_type, data in type_analysis.items():
            if data["total_size"] > self.size_threshold:
                from src.utils.file_utils import format_size

                recommendations.append(
                    {
                        "type": "file_type_cleanup",
                        "priority": "high"
                        if data["total_size"] > 1024 * 1024 * 1024
                        else "medium",  # >1GB
                        "title": f"Large {file_type.upper()} Files",
                        "description": f"{data['count']} {file_type} files using {format_size(data['total_size'])}",
                        "action": "Review and consider compressing or archiving",
                        "file_count": data["count"],
                        "size": data["total_size"],
                    }
                )

        # Analyze by directory
        dir_analysis = self._analyze_by_directory(analysis.files)
        top_dirs = sorted(
            dir_analysis.items(), key=lambda x: x[1]["total_size"], reverse=True
        )[:3]

        for directory, data in top_dirs:
            if data["total_size"] > self.size_threshold:
                from src.utils.file_utils import format_size

                recommendations.append(
                    {
                        "type": "directory_cleanup",
                        "priority": "medium",
                        "title": f"Large Directory: {os.path.basename(directory)}",
                        "description": f"{data['count']} files using {format_size(data['total_size'])}",
                        "action": "Review directory contents for cleanup opportunities",
                        "file_count": data["count"],
                        "size": data["total_size"],
                        "path": directory,
                    }
                )

        # Very large individual files
        huge_files = [
            f
            for f in analysis.files
            if f.size_category in [FileSizeCategory.HUGE, FileSizeCategory.MASSIVE]
        ]
        if huge_files:
            total_huge_size = sum(f.size for f in huge_files)
            from src.utils.file_utils import format_size

            recommendations.append(
                {
                    "type": "individual_large_files",
                    "priority": "high",
                    "title": "Very Large Individual Files",
                    "description": f"{len(huge_files)} files larger than 1GB ({format_size(total_huge_size)} total)",
                    "action": "Consider compression, archiving, or removal",
                    "file_count": len(huge_files),
                    "size": total_huge_size,
                }
            )

        return recommendations

    def _analyze_by_file_type(self, files: list[FileInfo]) -> dict[str, dict]:
        """Analyze files grouped by file type."""
        type_data = {}

        for file in files:
            file_type = file.file_type
            if file_type not in type_data:
                type_data[file_type] = {"count": 0, "total_size": 0, "files": []}

            type_data[file_type]["count"] += 1
            type_data[file_type]["total_size"] += file.size
            type_data[file_type]["files"].append(file)

        return type_data

    def _analyze_by_directory(self, files: list[FileInfo]) -> dict[str, dict]:
        """Analyze files grouped by directory."""
        dir_data = {}

        for file in files:
            directory = os.path.dirname(file.path)
            if directory not in dir_data:
                dir_data[directory] = {"count": 0, "total_size": 0, "files": []}

            dir_data[directory]["count"] += 1
            dir_data[directory]["total_size"] += file.size
            dir_data[directory]["files"].append(file)

        return dir_data

    def export_analysis_results(
        self, analysis: LargeFileAnalysis, format_type: str = "csv"
    ) -> str:
        """
        Export analysis results to a formatted string.

        Args:
            analysis: LargeFileAnalysis object
            format_type: Export format ("csv", "json")

        Returns:
            Formatted string ready for file export
        """
        if format_type == "csv":
            return self._export_to_csv(analysis)
        elif format_type == "json":
            return self._export_to_json(analysis)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def _export_to_csv(self, analysis: LargeFileAnalysis) -> str:
        """Export analysis to CSV format."""
        import csv
        from io import StringIO

        from src.utils.file_utils import format_size

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "File Name",
                "Path",
                "Size (Bytes)",
                "Size (Formatted)",
                "Size Category",
                "Last Modified",
                "File Type",
            ]
        )

        # Data rows
        for file in analysis.files:
            writer.writerow(
                [
                    file.name,
                    file.path,
                    file.size,
                    format_size(file.size),
                    file.size_category.value,
                    file.modified.strftime("%Y-%m-%d %H:%M:%S"),
                    file.file_type,
                ]
            )

        return output.getvalue()

    def _export_to_json(self, analysis: LargeFileAnalysis) -> str:
        """Export analysis to JSON format."""
        import json

        from src.utils.file_utils import format_size

        data = {
            "analysis_date": datetime.now().isoformat(),
            "size_threshold": analysis.size_threshold,
            "total_files": len(analysis.files),
            "total_size": analysis.total_size,
            "files": [],
        }

        for file in analysis.files:
            data["files"].append(
                {
                    "name": file.name,
                    "path": file.path,
                    "size": file.size,
                    "size_formatted": format_size(file.size),
                    "size_category": file.size_category.value,
                    "last_modified": file.modified.isoformat(),
                    "file_type": file.file_type,
                }
            )

        return json.dumps(data, indent=2)
