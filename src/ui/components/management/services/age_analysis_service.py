#!/usr/bin/env python3
# File: src/ui/components/management/services/age_analysis_service.py

from collections import defaultdict
from datetime import datetime

from ..models.management_data import FileAgeAnalysis, FileAgeCategory, FileInfo


class FileAgeAnalysisService:
    """
    Service for analyzing file ages and generating archival recommendations.
    Provides age categorization, archival suggestions, and cleanup guidance.
    """

    def __init__(self):
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """Set callback function for progress updates."""
        self.progress_callback = callback

    def analyze_file_ages(self, files: list[dict]) -> FileAgeAnalysis:
        """
        Analyze files for age distribution and archival recommendations.

        Args:
            files: List of file dictionaries from scanner

        Returns:
            FileAgeAnalysis object with results
        """
        # Convert to FileInfo objects
        file_infos = [self._dict_to_fileinfo(file_dict) for file_dict in files]
        len(file_infos)

        if self.progress_callback:
            self.progress_callback("Analyzing file ages...", 25)

        # Create analysis object
        analysis = FileAgeAnalysis(files=file_infos)

        if self.progress_callback:
            self.progress_callback("Categorizing by age...", 50)

        if self.progress_callback:
            self.progress_callback("Generating recommendations...", 75)

        if self.progress_callback:
            self.progress_callback("Age analysis complete", 100)

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

    def get_age_distribution_stats(
        self, analysis: FileAgeAnalysis
    ) -> dict[FileAgeCategory, dict]:
        """
        Get detailed age distribution statistics.

        Returns:
            Dictionary with category statistics including count, total size, percentage
        """
        age_groups = analysis.get_files_by_age()
        total_files = len(analysis.files)
        total_size = sum(f.size for f in analysis.files)

        distribution = {}
        for category in FileAgeCategory:
            category_files = age_groups.get(category, [])
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
                "description": self._get_category_description(category),
                "color": self._get_category_color(category),
            }

        return distribution

    def _get_category_description(self, category: FileAgeCategory) -> str:
        """Get human-friendly description for age category."""
        descriptions = {
            FileAgeCategory.RECENT: "Modified within the last 7 days",
            FileAgeCategory.ACTIVE: "Modified 1 week to 1 month ago",
            FileAgeCategory.CURRENT: "Modified 1-6 months ago",
            FileAgeCategory.STALE: "Modified 6 months to 1 year ago",
            FileAgeCategory.ARCHIVE: "Modified 1-3 years ago",
            FileAgeCategory.OLD: "Modified more than 3 years ago",
        }
        return descriptions.get(category, "Unknown age category")

    def _get_category_color(self, category: FileAgeCategory) -> str:
        """Get color code for age category visualization."""
        colors = {
            FileAgeCategory.RECENT: "#10B981",  # Green - fresh
            FileAgeCategory.ACTIVE: "#F59E0B",  # Yellow - active
            FileAgeCategory.CURRENT: "#3B82F6",  # Blue - current
            FileAgeCategory.STALE: "#F97316",  # Orange - stale
            FileAgeCategory.ARCHIVE: "#EF4444",  # Red - archive
            FileAgeCategory.OLD: "#7C2D12",  # Dark red - old
        }
        return colors.get(category, "#6B7280")

    def get_archival_recommendations(
        self, analysis: FileAgeAnalysis, min_age_days: int = 365, min_size_mb: int = 10
    ) -> list[dict]:
        """
        Generate detailed archival recommendations.

        Args:
            analysis: FileAgeAnalysis object
            min_age_days: Minimum age in days for archival consideration
            min_size_mb: Minimum size in MB for priority recommendations

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        age_groups = analysis.get_files_by_age()
        min_size_bytes = min_size_mb * 1024 * 1024

        # Analyze archive category (1-3 years)
        archive_files = age_groups.get(FileAgeCategory.ARCHIVE, [])
        if archive_files:
            large_archive = [f for f in archive_files if f.size >= min_size_bytes]
            sum(f.size for f in archive_files)

            from src.utils.file_utils import format_size

            if large_archive:
                recommendations.append(
                    {
                        "type": "archive_large_files",
                        "priority": "high",
                        "title": "Large Files Ready for Archival",
                        "description": f"{len(large_archive)} large files ({format_size(sum(f.size for f in large_archive))}) unused for 1-3 years",
                        "action": "Consider moving to archive storage or compression",
                        "file_count": len(large_archive),
                        "size": sum(f.size for f in large_archive),
                        "category": FileAgeCategory.ARCHIVE,
                        "files": large_archive[:10],  # Top 10 for preview
                    }
                )

            if len(archive_files) > len(large_archive):
                small_archive = [f for f in archive_files if f.size < min_size_bytes]
                recommendations.append(
                    {
                        "type": "archive_small_files",
                        "priority": "medium",
                        "title": "Small Files for Bulk Archival",
                        "description": f"{len(small_archive)} smaller files ({format_size(sum(f.size for f in small_archive))}) unused for 1-3 years",
                        "action": "Consider bulk archival or cleanup",
                        "file_count": len(small_archive),
                        "size": sum(f.size for f in small_archive),
                        "category": FileAgeCategory.ARCHIVE,
                        "files": small_archive[:10],
                    }
                )

        # Analyze old category (3+ years)
        old_files = age_groups.get(FileAgeCategory.OLD, [])
        if old_files:
            large_old = [f for f in old_files if f.size >= min_size_bytes]
            sum(f.size for f in old_files)

            if large_old:
                recommendations.append(
                    {
                        "type": "old_large_files",
                        "priority": "high",
                        "title": "Very Old Large Files",
                        "description": f"{len(large_old)} large files ({format_size(sum(f.size for f in large_old))}) unused for 3+ years",
                        "action": "High priority for archival or deletion",
                        "file_count": len(large_old),
                        "size": sum(f.size for f in large_old),
                        "category": FileAgeCategory.OLD,
                        "files": large_old[:10],
                    }
                )

            if len(old_files) > len(large_old):
                small_old = [f for f in old_files if f.size < min_size_bytes]
                recommendations.append(
                    {
                        "type": "old_small_files",
                        "priority": "medium",
                        "title": "Very Old Small Files",
                        "description": f"{len(small_old)} smaller files ({format_size(sum(f.size for f in small_old))}) unused for 3+ years",
                        "action": "Consider deletion or bulk archival",
                        "file_count": len(small_old),
                        "size": sum(f.size for f in small_old),
                        "category": FileAgeCategory.OLD,
                        "files": small_old[:10],
                    }
                )

        # Analyze by file type for additional recommendations
        type_recommendations = self._analyze_by_file_type(analysis)
        recommendations.extend(type_recommendations)

        return recommendations

    def _analyze_by_file_type(self, analysis: FileAgeAnalysis) -> list[dict]:
        """Analyze archival candidates by file type."""
        recommendations = []
        archival_candidates = analysis.get_archival_candidates()

        # Group by file type
        type_groups = defaultdict(list)
        for file in archival_candidates:
            type_groups[file.file_type].append(file)

        # Identify file types with significant archival potential
        for file_type, files in type_groups.items():
            if len(files) >= 5:  # At least 5 files of this type
                total_size = sum(f.size for f in files)
                if total_size >= 50 * 1024 * 1024:  # At least 50MB total
                    from src.utils.file_utils import format_size

                    recommendations.append(
                        {
                            "type": "file_type_archival",
                            "priority": "medium",
                            "title": f"Old {file_type.upper()} Files",
                            "description": f"{len(files)} {file_type} files ({format_size(total_size)}) ready for archival",
                            "action": f"Review {file_type} files for archival or cleanup",
                            "file_count": len(files),
                            "size": total_size,
                            "file_type": file_type,
                            "files": sorted(files, key=lambda f: f.size, reverse=True)[
                                :5
                            ],
                        }
                    )

        return recommendations

    def get_cleanup_candidates(
        self,
        analysis: FileAgeAnalysis,
        include_stale: bool = True,
        min_size_mb: int = 1,
    ) -> list[FileInfo]:
        """
        Get files that are candidates for cleanup based on age.

        Args:
            analysis: FileAgeAnalysis object
            include_stale: Whether to include stale files (6mo-1yr old)
            min_size_mb: Minimum size in MB for inclusion

        Returns:
            List of FileInfo objects that are cleanup candidates
        """
        candidates = []
        age_groups = analysis.get_files_by_age()
        min_size_bytes = min_size_mb * 1024 * 1024

        # Always include archive and old files
        target_categories = [FileAgeCategory.ARCHIVE, FileAgeCategory.OLD]
        if include_stale:
            target_categories.append(FileAgeCategory.STALE)

        for category in target_categories:
            category_files = age_groups.get(category, [])
            for file in category_files:
                if file.size >= min_size_bytes:
                    candidates.append(file)

        # Sort by age (oldest first) then by size (largest first)
        candidates.sort(key=lambda f: (f.modified, -f.size))

        return candidates

    def export_analysis_results(
        self, analysis: FileAgeAnalysis, format_type: str = "csv"
    ) -> str:
        """
        Export age analysis results to a formatted string.

        Args:
            analysis: FileAgeAnalysis object
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

    def _export_to_csv(self, analysis: FileAgeAnalysis) -> str:
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
                "Age Category",
                "Last Modified",
                "File Type",
                "Days Old",
            ]
        )

        # Data rows
        for file in analysis.files:
            days_old = (datetime.now() - file.modified).days
            writer.writerow(
                [
                    file.name,
                    file.path,
                    file.size,
                    format_size(file.size),
                    file.age_category.value,
                    file.modified.strftime("%Y-%m-%d %H:%M:%S"),
                    file.file_type,
                    days_old,
                ]
            )

        return output.getvalue()

    def _export_to_json(self, analysis: FileAgeAnalysis) -> str:
        """Export analysis to JSON format."""
        import json

        from src.utils.file_utils import format_size

        # Get age distribution
        distribution = self.get_age_distribution_stats(analysis)

        data = {
            "analysis_date": datetime.now().isoformat(),
            "total_files": len(analysis.files),
            "age_distribution": {},
            "archival_candidates": len(analysis.get_archival_candidates()),
            "files": [],
        }

        # Add age distribution summary
        for category, stats in distribution.items():
            data["age_distribution"][category.value] = {
                "count": stats["count"],
                "total_size": stats["total_size"],
                "percentage": stats["percentage"],
                "description": stats["description"],
            }

        # Add file details
        for file in analysis.files:
            days_old = (datetime.now() - file.modified).days
            data["files"].append(
                {
                    "name": file.name,
                    "path": file.path,
                    "size": file.size,
                    "size_formatted": format_size(file.size),
                    "age_category": file.age_category.value,
                    "last_modified": file.modified.isoformat(),
                    "file_type": file.file_type,
                    "days_old": days_old,
                }
            )

        return json.dumps(data, indent=2)
