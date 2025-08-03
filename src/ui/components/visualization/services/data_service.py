#!/usr/bin/env python3
# File: src/ui/components/visualization/services/data_service.py

from datetime import datetime, timedelta
from typing import Any

from ....themes.styles import FILE_COLORS
from ..models.chart_data import (
    ChartDataTransformer,
    ChartMetadata,
    DirectoryNode,
    FileAgeData,
    FileDistributionData,
    FileTypeData,
    TopFilesData,
)


class VisualizationDataService:
    """
    Service class for transforming file system data into chart-ready formats.
    Handles data aggregation, filtering, and preparation for visualization components.
    """

    def __init__(self):
        self.current_files = []
        self.current_path = ""
        self.metadata = None

    def update_data(self, file_list: list[dict[str, Any]], directory_path: str = ""):
        """
        Update the service with new file data.

        Args:
            file_list: List of file dictionaries from file scanner
            directory_path: Path of the scanned directory
        """
        self.current_files = file_list
        self.current_path = directory_path
        self.metadata = self._create_metadata()

    def get_file_type_data(self) -> list[FileTypeData]:
        """Get file type distribution data for pie charts."""
        if not self.current_files:
            return []

        type_data = ChartDataTransformer.files_to_type_data(self.current_files)

        # Apply theme colors to file types
        color_map = FILE_COLORS
        for item in type_data:
            item.color = color_map.get(
                item.type, color_map.get("OTHER", "#bdc3c7")
            ).name()

        return type_data

    def get_directory_hierarchy(self) -> DirectoryNode | None:
        """Get directory hierarchy for treemap and sunburst charts."""
        if not self.current_files:
            return None

        return ChartDataTransformer.files_to_directory_hierarchy(
            self.current_files, self.current_path
        )

    def get_file_size_distribution(self) -> FileDistributionData:
        """Get file size distribution data for bar charts."""
        from src.utils.logger import logger

        if not self.current_files:
            logger.debug("get_file_size_distribution: No files to analyze")
            return FileDistributionData([], [], [], [])

        logger.debug(f"get_file_size_distribution: Processing {len(self.current_files)} files")

        # Define size ranges (in bytes)
        ranges = [
            (0, 1024, "0-1KB"),
            (1024, 1024 * 1024, "1KB-1MB"),
            (1024 * 1024, 100 * 1024 * 1024, "1MB-100MB"),
            (100 * 1024 * 1024, 1024 * 1024 * 1024, "100MB-1GB"),
            (1024 * 1024 * 1024, float("inf"), "1GB+"),
        ]

        # Count files in each range
        range_counts = [0] * len(ranges)
        range_sizes = [0] * len(ranges)

        for file in self.current_files:
            file_size = file["size"]
            for i, (min_size, max_size, _) in enumerate(ranges):
                if min_size <= file_size < max_size:
                    range_counts[i] += 1
                    range_sizes[i] += file_size
                    break

        # Calculate percentages
        total_files = len(self.current_files)
        percentages = [
            count / total_files * 100 if total_files > 0 else 0
            for count in range_counts
        ]

        total_size_files = sum(range_counts)
        logger.debug(f"Size distribution: {total_size_files} files categorized")
        logger.debug(f"Size distribution counts: {range_counts}")

        return FileDistributionData(
            size_ranges=[r[2] for r in ranges],
            file_counts=range_counts,
            total_sizes=range_sizes,
            percentages=percentages,
        )

    def get_top_files(self, limit: int = 20) -> list[TopFilesData]:
        """Get the largest files."""
        if not self.current_files:
            return []

        return ChartDataTransformer.files_to_top_files(self.current_files, limit)

    def get_file_age_distribution(self) -> FileAgeData:
        """Get file age distribution data."""
        from src.utils.logger import logger

        if not self.current_files:
            logger.debug("get_file_age_distribution: No files to analyze")
            return FileAgeData([], [], [], [])

        logger.debug(f"get_file_age_distribution: Processing {len(self.current_files)} files")
        now = datetime.now()

        # Define age ranges
        ranges = [
            (timedelta(0), timedelta(days=1), "Today"),
            (timedelta(days=1), timedelta(days=7), "This Week"),
            (timedelta(days=7), timedelta(days=30), "This Month"),
            (timedelta(days=30), timedelta(days=90), "Last 3 Months"),
            (timedelta(days=90), timedelta(days=365), "This Year"),
            (timedelta(days=365), timedelta(days=365 * 10), "Older"),
        ]

        # Count files in each age range
        range_counts = [0] * len(ranges)
        range_sizes = [0] * len(ranges)
        processed_files = 0
        error_files = 0

        for file in self.current_files:
            try:
                file_modified = file["modified"]

                # Validate that we have a datetime object
                if not isinstance(file_modified, datetime):
                    logger.warning(f"File age analysis: Invalid datetime type for file {file.get('name', 'unknown')}: {type(file_modified)}")
                    error_files += 1
                    continue

                age = now - file_modified
                processed_files += 1

                for i, (min_age, max_age, _) in enumerate(ranges):
                    if min_age <= age < max_age:
                        range_counts[i] += 1
                        range_sizes[i] += file["size"]
                        break

            except Exception as e:
                logger.error(f"Error processing file age for {file.get('name', 'unknown')}: {e}")
                error_files += 1

        # Calculate percentages
        total_files = len(self.current_files)
        percentages = [
            count / total_files * 100 if total_files > 0 else 0
            for count in range_counts
        ]

        total_age_files = sum(range_counts)
        logger.debug(f"File age distribution: {processed_files} processed, {error_files} errors, {total_age_files} categorized")
        logger.debug(f"Age distribution counts: {range_counts}")

        return FileAgeData(
            age_ranges=[r[2] for r in ranges],
            file_counts=range_counts,
            total_sizes=range_sizes,
            percentages=percentages,
        )

    def get_metadata(self) -> ChartMetadata:
        """Get metadata for the current dataset."""
        return self.metadata if self.metadata else ChartMetadata("No Data")

    def filter_by_file_type(self, file_type: str) -> list[dict[str, Any]]:
        """Filter current files by file type."""
        return [f for f in self.current_files if f["type"] == file_type]

    def filter_by_directory(self, directory_path: str) -> list[dict[str, Any]]:
        """Filter current files by directory path."""
        return [f for f in self.current_files if f["path"].startswith(directory_path)]

    def filter_by_size_range(
        self, min_size: int, max_size: int
    ) -> list[dict[str, Any]]:
        """Filter current files by size range."""
        return [f for f in self.current_files if min_size <= f["size"] < max_size]

    def _create_metadata(self) -> ChartMetadata:
        """Create metadata for the current dataset."""
        from src.utils.file_utils import format_size

        total_size = sum(file["size"] for file in self.current_files)

        return ChartMetadata(
            title="File System Analysis",
            subtitle=f"Directory: {self.current_path}" if self.current_path else None,
            directory_path=self.current_path,
            scan_date=datetime.now(),
            total_files=len(self.current_files),
            total_size=total_size,
            total_size_formatted=format_size(total_size),
        )
