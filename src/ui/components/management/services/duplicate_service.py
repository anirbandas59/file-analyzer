#!/usr/bin/env python3
# File: src/ui/components/management/services/duplicate_service.py

from collections import defaultdict

from ..models.management_data import DuplicateConfidence, DuplicateGroup, FileInfo


class DuplicateDetectionService:
    """
    Service for detecting duplicate files using multiple strategies.
    Implements both heuristic and content-based duplicate detection.
    """

    def __init__(self):
        self.hash_cache = {}  # Cache for calculated hashes
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """Set callback function for progress updates."""
        self.progress_callback = callback

    def find_duplicates(
        self,
        files: list[dict],
        use_content_hash: bool = True,
        use_heuristics: bool = True,
    ) -> list[DuplicateGroup]:
        """
        Find duplicate files using multiple detection strategies.

        Args:
            files: List of file dictionaries from scanner
            use_content_hash: Whether to use content-based hash comparison
            use_heuristics: Whether to use heuristic comparison (size + name)

        Returns:
            List of DuplicateGroup objects
        """
        # Convert to FileInfo objects
        file_infos = [self._dict_to_fileinfo(file_dict) for file_dict in files]

        duplicate_groups = []

        if use_heuristics:
            # First pass: Heuristic detection
            heuristic_groups = self._find_heuristic_duplicates(file_infos)
            duplicate_groups.extend(heuristic_groups)

        if use_content_hash:
            # Second pass: Content-based detection
            hash_groups = self._find_hash_duplicates(file_infos)
            duplicate_groups.extend(hash_groups)

        # Remove duplicates and merge overlapping groups
        return self._merge_duplicate_groups(duplicate_groups)

    def _dict_to_fileinfo(self, file_dict: dict) -> FileInfo:
        """Convert file dictionary to FileInfo object."""
        return FileInfo(
            name=file_dict["name"],
            path=file_dict["path"],
            size=file_dict["size"],
            modified=file_dict["modified"],
            file_type=file_dict["type"],
        )

    def _find_heuristic_duplicates(self, files: list[FileInfo]) -> list[DuplicateGroup]:
        """Find duplicates using heuristic methods (size + name patterns)."""
        duplicate_groups = []

        # Group by size first (quick filter)
        size_groups = defaultdict(list)
        for file in files:
            size_groups[file.size].append(file)

        # Analyze each size group
        for size, file_list in size_groups.items():
            if len(file_list) < 2:
                continue  # No duplicates possible

            # Group by exact filename
            name_groups = defaultdict(list)
            for file in file_list:
                name_groups[file.name].append(file)

            # Create duplicate groups for exact name matches
            for name, name_file_list in name_groups.items():
                if len(name_file_list) >= 2:
                    confidence = DuplicateConfidence.MEDIUM
                    duplicate_groups.append(
                        DuplicateGroup(files=name_file_list, confidence=confidence)
                    )

        return duplicate_groups

    def _find_hash_duplicates(self, files: list[FileInfo]) -> list[DuplicateGroup]:
        """Find duplicates using content hash comparison."""
        duplicate_groups = []
        total_files = len(files)

        # Step 1: Quick partial hash for pre-filtering
        partial_hash_groups = defaultdict(list)

        for i, file in enumerate(files):
            if self.progress_callback:
                self.progress_callback(
                    f"Quick scan: {file.name}", int((i / total_files) * 50)
                )

            # Calculate partial hash (first 1KB)
            try:
                partial_hash = file.calculate_hash("partial")
                if partial_hash:
                    partial_hash_groups[partial_hash].append(file)
            except Exception:
                # Skip files that can't be read
                continue

        # Step 2: Full hash verification for potential duplicates
        hash_groups = defaultdict(list)
        files_to_hash = []

        # Collect files that have matching partial hashes
        for partial_hash, file_list in partial_hash_groups.items():
            if len(file_list) >= 2:
                files_to_hash.extend(file_list)

        # Calculate full hashes for potential duplicates
        for i, file in enumerate(files_to_hash):
            if self.progress_callback:
                self.progress_callback(
                    f"Deep scan: {file.name}", 50 + int((i / len(files_to_hash)) * 50)
                )

            try:
                # Check cache first
                cache_key = f"{file.path}:{file.size}:{file.modified.timestamp()}"

                if cache_key in self.hash_cache:
                    full_hash = self.hash_cache[cache_key]
                else:
                    full_hash = file.calculate_hash("full")
                    self.hash_cache[cache_key] = full_hash

                if full_hash:
                    hash_groups[full_hash].append(file)

            except Exception:
                # Skip files that can't be hashed
                continue

        # Create duplicate groups for files with matching hashes
        for hash_value, file_list in hash_groups.items():
            if len(file_list) >= 2:
                duplicate_groups.append(
                    DuplicateGroup(
                        files=file_list,
                        confidence=DuplicateConfidence.HIGH,
                        hash_key=hash_value,
                    )
                )

        if self.progress_callback:
            self.progress_callback("Duplicate scan complete", 100)

        return duplicate_groups

    def _merge_duplicate_groups(
        self, groups: list[DuplicateGroup]
    ) -> list[DuplicateGroup]:
        """Merge overlapping duplicate groups and remove duplicates."""
        if not groups:
            return []

        # Create a mapping of file paths to groups
        file_to_groups = defaultdict(list)
        for group in groups:
            for file in group.files:
                file_to_groups[file.path].append(group)

        # Find groups that share files (overlapping groups)
        merged_groups = []
        processed_group_ids = set()

        for group in groups:
            if id(group) in processed_group_ids:
                continue

            # Find all groups that share files with this group
            overlapping_groups = [group]
            overlapping_ids = {id(group)}
            to_check = [group]

            while to_check:
                current_group = to_check.pop()
                for file in current_group.files:
                    for other_group in file_to_groups[file.path]:
                        if id(other_group) not in overlapping_ids:
                            overlapping_groups.append(other_group)
                            overlapping_ids.add(id(other_group))
                            to_check.append(other_group)

            # Merge overlapping groups
            all_files = []
            best_confidence = DuplicateConfidence.LOW
            hash_key = ""

            for og in overlapping_groups:
                all_files.extend(og.files)
                if og.confidence.value == DuplicateConfidence.HIGH.value:
                    best_confidence = DuplicateConfidence.HIGH
                    hash_key = og.hash_key
                elif (
                    og.confidence.value == DuplicateConfidence.MEDIUM.value
                    and best_confidence.value != DuplicateConfidence.HIGH.value
                ):
                    best_confidence = DuplicateConfidence.MEDIUM

                processed_group_ids.add(id(og))

            # Remove duplicate files (same path)
            unique_files = {}
            for file in all_files:
                unique_files[file.path] = file

            # Only create group if we have actual duplicates
            unique_file_list = list(unique_files.values())
            if len(unique_file_list) >= 2:
                merged_groups.append(
                    DuplicateGroup(
                        files=unique_file_list,
                        confidence=best_confidence,
                        hash_key=hash_key,
                    )
                )

        return merged_groups

    def calculate_space_savings(
        self, duplicate_groups: list[DuplicateGroup]
    ) -> tuple[int, int]:
        """
        Calculate potential space savings from removing duplicates.

        Returns:
            Tuple of (total_duplicate_size, potential_savings)
        """
        total_duplicate_size = 0
        potential_savings = 0

        for group in duplicate_groups:
            total_duplicate_size += group.total_size
            potential_savings += group.potential_savings

        return total_duplicate_size, potential_savings

    def get_duplicate_statistics(
        self, duplicate_groups: list[DuplicateGroup]
    ) -> dict[str, any]:
        """Get comprehensive statistics about duplicates."""
        if not duplicate_groups:
            return {
                "total_groups": 0,
                "total_files": 0,
                "total_size": 0,
                "potential_savings": 0,
                "confidence_breakdown": {},
            }

        total_files = sum(len(group.files) for group in duplicate_groups)
        total_size = sum(group.total_size for group in duplicate_groups)
        potential_savings = sum(group.potential_savings for group in duplicate_groups)

        # Confidence level breakdown
        confidence_breakdown = {
            DuplicateConfidence.HIGH.value: 0,
            DuplicateConfidence.MEDIUM.value: 0,
            DuplicateConfidence.LOW.value: 0,
        }

        for group in duplicate_groups:
            confidence_breakdown[group.confidence.value] += len(group.files)

        return {
            "total_groups": len(duplicate_groups),
            "total_files": total_files,
            "total_size": total_size,
            "potential_savings": potential_savings,
            "confidence_breakdown": confidence_breakdown,
        }
