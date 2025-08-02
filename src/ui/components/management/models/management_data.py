#!/usr/bin/env python3
# File: src/ui/components/management/models/management_data.py

import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
from enum import Enum
from pathlib import Path

class DuplicateConfidence(Enum):
    """Confidence levels for duplicate detection."""
    HIGH = "high"        # Content hash match
    MEDIUM = "medium"    # Size + name match
    LOW = "low"          # Size match only

class FileAgeCategory(Enum):
    """File age categorization for archival recommendations."""
    RECENT = "recent"           # 0-7 days
    ACTIVE = "active"           # 1 week - 1 month  
    CURRENT = "current"         # 1-6 months
    STALE = "stale"            # 6 months - 1 year
    ARCHIVE = "archive"         # 1-3 years
    OLD = "old"                # 3+ years

class FileSizeCategory(Enum):
    """File size categories for large file analysis."""
    SMALL = "small"        # < 1MB
    MEDIUM = "medium"      # 1MB - 100MB
    LARGE = "large"        # 100MB - 1GB
    HUGE = "huge"          # 1GB - 10GB
    MASSIVE = "massive"    # > 10GB

@dataclass
class FileInfo:
    """Enhanced file information for management operations."""
    name: str
    path: str
    size: int
    modified: datetime
    file_type: str
    
    # Computed properties
    hash_sha256: Optional[str] = None
    hash_partial: Optional[str] = None  # First 1KB hash for quick comparison
    size_category: Optional[FileSizeCategory] = None
    age_category: Optional[FileAgeCategory] = None
    
    def __post_init__(self):
        """Calculate derived properties."""
        self.size_category = self._calculate_size_category()
        self.age_category = self._calculate_age_category()
    
    def _calculate_size_category(self) -> FileSizeCategory:
        """Determine size category based on file size."""
        if self.size < 1024 * 1024:  # < 1MB
            return FileSizeCategory.SMALL
        elif self.size < 100 * 1024 * 1024:  # < 100MB
            return FileSizeCategory.MEDIUM
        elif self.size < 1024 * 1024 * 1024:  # < 1GB
            return FileSizeCategory.LARGE
        elif self.size < 10 * 1024 * 1024 * 1024:  # < 10GB
            return FileSizeCategory.HUGE
        else:
            return FileSizeCategory.MASSIVE
    
    def _calculate_age_category(self) -> FileAgeCategory:
        """Determine age category based on modification date."""
        now = datetime.now()
        age = now - self.modified
        
        if age.days <= 7:
            return FileAgeCategory.RECENT
        elif age.days <= 30:
            return FileAgeCategory.ACTIVE
        elif age.days <= 180:  # 6 months
            return FileAgeCategory.CURRENT
        elif age.days <= 365:  # 1 year
            return FileAgeCategory.STALE
        elif age.days <= 1095:  # 3 years
            return FileAgeCategory.ARCHIVE
        else:
            return FileAgeCategory.OLD
    
    def calculate_hash(self, hash_type: str = "full") -> str:
        """Calculate file hash for duplicate detection."""
        try:
            hasher = hashlib.sha256()
            
            with open(self.path, 'rb') as f:
                if hash_type == "partial":
                    # Read first 1KB for quick comparison
                    data = f.read(1024)
                    hasher.update(data)
                    self.hash_partial = hasher.hexdigest()
                    return self.hash_partial
                else:
                    # Read full file in chunks
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                    self.hash_sha256 = hasher.hexdigest()
                    return self.hash_sha256
                    
        except (IOError, PermissionError):
            return ""

@dataclass  
class DuplicateGroup:
    """Group of duplicate files with analysis information."""
    files: List[FileInfo]
    confidence: DuplicateConfidence
    total_size: int = 0
    potential_savings: int = 0  # Size that could be saved by removing duplicates
    hash_key: str = ""
    
    def __post_init__(self):
        """Calculate derived properties."""
        self.total_size = sum(file.size for file in self.files)
        self.potential_savings = self.total_size - max(file.size for file in self.files) if self.files else 0
        
        # Use hash from first file as group key
        if self.files and self.files[0].hash_sha256:
            self.hash_key = self.files[0].hash_sha256
    
    def get_recommended_keeper(self) -> Optional[FileInfo]:
        """Get the recommended file to keep (newest, largest)."""
        if not self.files:
            return None
            
        # Prefer newer files, then larger files
        return max(self.files, key=lambda f: (f.modified, f.size))
    
    def get_files_to_remove(self) -> List[FileInfo]:
        """Get files recommended for removal."""
        keeper = self.get_recommended_keeper()
        if not keeper:
            return []
        
        return [f for f in self.files if f.path != keeper.path]

@dataclass
class LargeFileAnalysis:
    """Analysis results for large files."""
    files: List[FileInfo]
    total_size: int = 0
    size_threshold: int = 100 * 1024 * 1024  # 100MB default
    
    def __post_init__(self):
        """Calculate total size."""
        self.total_size = sum(file.size for file in self.files)
    
    def get_files_by_category(self) -> Dict[FileSizeCategory, List[FileInfo]]:
        """Group files by size category."""
        categories = {}
        for category in FileSizeCategory:
            categories[category] = [f for f in self.files if f.size_category == category]
        return categories
    
    def get_cleanup_recommendations(self) -> List[str]:
        """Generate cleanup recommendations."""
        recommendations = []
        
        # Analyze by file type
        type_sizes = {}
        for file in self.files:
            type_sizes[file.file_type] = type_sizes.get(file.file_type, 0) + file.size
        
        # Find largest file types
        sorted_types = sorted(type_sizes.items(), key=lambda x: x[1], reverse=True)
        
        for file_type, size in sorted_types[:3]:  # Top 3 types
            from src.utils.file_utils import format_size
            recommendations.append(f"Consider reviewing {file_type} files ({format_size(size)} total)")
        
        return recommendations

@dataclass
class FileAgeAnalysis:
    """Analysis results for file age distribution."""
    files: List[FileInfo]
    
    def get_files_by_age(self) -> Dict[FileAgeCategory, List[FileInfo]]:
        """Group files by age category."""
        categories = {}
        for category in FileAgeCategory:
            categories[category] = [f for f in self.files if f.age_category == category]
        return categories
    
    def get_archival_candidates(self) -> List[FileInfo]:
        """Get files that are candidates for archival."""
        return [f for f in self.files 
                if f.age_category in [FileAgeCategory.ARCHIVE, FileAgeCategory.OLD]]
    
    def get_size_by_age(self) -> Dict[FileAgeCategory, int]:
        """Get total size for each age category."""
        age_groups = self.get_files_by_age()
        return {category: sum(f.size for f in files) 
                for category, files in age_groups.items()}
    
    def get_archival_recommendations(self) -> List[str]:
        """Generate archival recommendations."""
        recommendations = []
        age_sizes = self.get_size_by_age()
        
        archive_size = age_sizes.get(FileAgeCategory.ARCHIVE, 0)
        old_size = age_sizes.get(FileAgeCategory.OLD, 0)
        
        if archive_size > 0:
            from src.utils.file_utils import format_size
            archive_count = len(self.get_files_by_age().get(FileAgeCategory.ARCHIVE, []))
            recommendations.append(
                f"Consider archiving {archive_count} files from 1-3 years ago ({format_size(archive_size)})"
            )
        
        if old_size > 0:
            from src.utils.file_utils import format_size
            old_count = len(self.get_files_by_age().get(FileAgeCategory.OLD, []))
            recommendations.append(
                f"Consider archiving {old_count} files older than 3 years ({format_size(old_size)})"
            )
        
        return recommendations

@dataclass
class ManagementSummary:
    """Overall summary of management analysis."""
    duplicate_groups: List[DuplicateGroup] = field(default_factory=list)
    large_files: Optional[LargeFileAnalysis] = None
    age_analysis: Optional[FileAgeAnalysis] = None
    
    total_files_analyzed: int = 0
    total_size_analyzed: int = 0
    potential_space_savings: int = 0
    
    def __post_init__(self):
        """Calculate summary statistics."""
        # Calculate potential space savings from duplicates
        self.potential_space_savings = sum(group.potential_savings for group in self.duplicate_groups)
    
    def get_top_recommendations(self) -> List[str]:
        """Get top recommendations across all analysis types."""
        recommendations = []
        
        # Duplicate recommendations
        if self.duplicate_groups:
            total_duplicate_savings = sum(group.potential_savings for group in self.duplicate_groups)
            duplicate_count = sum(len(group.files) - 1 for group in self.duplicate_groups)
            if total_duplicate_savings > 0:
                from src.utils.file_utils import format_size
                recommendations.append(
                    f"Remove {duplicate_count} duplicate files to save {format_size(total_duplicate_savings)}"
                )
        
        # Large file recommendations
        if self.large_files:
            recommendations.extend(self.large_files.get_cleanup_recommendations())
        
        # Age-based recommendations  
        if self.age_analysis:
            recommendations.extend(self.age_analysis.get_archival_recommendations())
        
        return recommendations[:5]  # Top 5 recommendations