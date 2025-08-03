#!/usr/bin/env python3
# File: src/ui/components/visualization/models/chart_data.py

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class FileTypeData:
    """Data structure for file type aggregation in pie charts."""

    type: str  # File extension (e.g., "PDF", "TXT")
    total_size: int  # Total bytes for this file type
    file_count: int  # Number of files of this type
    percentage: float  # Percentage of total size
    color: str  # Hex color for this file type


@dataclass
class DirectoryNode:
    """Hierarchical data structure for treemap and sunburst charts."""

    name: str  # Directory or file name
    path: str  # Full file system path
    total_size: int  # Size including all subdirectories
    file_count: int  # Number of files (direct + subdirectories)
    children: list["DirectoryNode"]  # Subdirectories and files
    depth: int  # Hierarchy level (0 = root)
    is_file: bool = False  # True if this is a file, False if directory
    file_type: str | None = None  # File extension if is_file=True
    modified: datetime | None = None  # Last modified date


@dataclass
class FileDistributionData:
    """Data for file size distribution charts."""

    size_ranges: list[str]  # ["0-1KB", "1KB-1MB", "1MB-100MB", etc.]
    file_counts: list[int]  # Number of files in each range
    total_sizes: list[int]  # Total size in bytes for each range
    percentages: list[float]  # Percentage of total count for each range


@dataclass
class TopFilesData:
    """Data for largest files chart."""

    file_name: str
    file_path: str
    size: int
    size_formatted: str  # Human-readable size (e.g., "15.2 MB")
    file_type: str
    modified: datetime


@dataclass
class FileAgeData:
    """Data for file age analysis."""

    age_ranges: list[str]  # ["Today", "This Week", "This Month", etc.]
    file_counts: list[int]  # Number of files in each age range
    total_sizes: list[int]  # Total size for each age range
    percentages: list[float]  # Percentage of total for each range


@dataclass
class ChartMetadata:
    """Metadata for chart exports and display."""

    title: str
    subtitle: str | None = None
    directory_path: str = ""
    scan_date: datetime = None
    total_files: int = 0
    total_size: int = 0
    total_size_formatted: str = ""

    def __post_init__(self):
        if self.scan_date is None:
            self.scan_date = datetime.now()


class ChartDataTransformer:
    """Utility class for transforming file list data into chart-ready formats."""

    @staticmethod
    def files_to_type_data(file_list: list[dict[str, Any]]) -> list[FileTypeData]:
        """Transform file list into file type aggregation data."""
        type_aggregation = {}
        total_size = sum(file["size"] for file in file_list)

        for file in file_list:
            file_type = file["type"]
            if file_type not in type_aggregation:
                type_aggregation[file_type] = {"total_size": 0, "file_count": 0}

            type_aggregation[file_type]["total_size"] += file["size"]
            type_aggregation[file_type]["file_count"] += 1

        # Convert to FileTypeData objects
        result = []
        for file_type, data in type_aggregation.items():
            percentage = (
                (data["total_size"] / total_size * 100) if total_size > 0 else 0
            )

            result.append(
                FileTypeData(
                    type=file_type,
                    total_size=data["total_size"],
                    file_count=data["file_count"],
                    percentage=percentage,
                    color="#3498db",  # Will be set by theme manager
                )
            )

        # Sort by size descending
        result.sort(key=lambda x: x.total_size, reverse=True)
        return result

    @staticmethod
    def files_to_directory_hierarchy(
        file_list: list[dict[str, Any]], root_path: str = ""
    ) -> DirectoryNode:
        """Transform file list into hierarchical directory structure."""
        # Create root node
        root = DirectoryNode(
            name="Root",
            path=root_path,
            total_size=0,
            file_count=0,
            children=[],
            depth=0,
        )

        # Build directory tree
        directory_map = {root_path: root}

        for file in file_list:
            file_path = file["path"]
            # Split path into components
            path_parts = file_path.replace(root_path, "").strip("/\\").split("/")

            current_node = root
            current_path = root_path

            # Navigate/create directory structure
            for i, part in enumerate(path_parts[:-1]):  # Exclude filename
                current_path = f"{current_path}/{part}".replace("//", "/")

                if current_path not in directory_map:
                    # Create new directory node
                    dir_node = DirectoryNode(
                        name=part,
                        path=current_path,
                        total_size=0,
                        file_count=0,
                        children=[],
                        depth=i + 1,
                    )
                    current_node.children.append(dir_node)
                    directory_map[current_path] = dir_node

                current_node = directory_map[current_path]

            # Add file node
            file_node = DirectoryNode(
                name=path_parts[-1],
                path=file_path,
                total_size=file["size"],
                file_count=1,
                children=[],
                depth=len(path_parts),
                is_file=True,
                file_type=file["type"],
                modified=file["modified"],
            )
            current_node.children.append(file_node)

        # Calculate directory sizes (bottom-up)
        ChartDataTransformer._calculate_directory_sizes(root)

        return root

    @staticmethod
    def _calculate_directory_sizes(node: DirectoryNode) -> None:
        """Recursively calculate directory sizes and file counts."""
        for child in node.children:
            if not child.is_file:
                ChartDataTransformer._calculate_directory_sizes(child)

            node.total_size += child.total_size
            node.file_count += child.file_count

    @staticmethod
    def files_to_top_files(
        file_list: list[dict[str, Any]], limit: int = 20
    ) -> list[TopFilesData]:
        """Get the largest files from the file list."""
        from src.utils.file_utils import format_size

        # Sort by size descending and take top N
        sorted_files = sorted(file_list, key=lambda x: x["size"], reverse=True)[:limit]

        result = []
        for file in sorted_files:
            result.append(
                TopFilesData(
                    file_name=file["name"],
                    file_path=file["path"],
                    size=file["size"],
                    size_formatted=format_size(file["size"]),
                    file_type=file["type"],
                    modified=file["modified"],
                )
            )

        return result
