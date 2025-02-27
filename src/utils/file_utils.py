#!/usr/bin/env python3
# File: src/utils/file_utils.py

import math
import mimetypes
import os
import time
from datetime import datetime
from pathlib import Path


def format_size(size_bytes):
    """
    Format a file size in bytes to a human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.23 MB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = int(math.floor(math.log(max(size_bytes, 1), 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    # Format the value - if it's bytes (i=0), show as integer
    if i == 0:
        return f"{int(s)} {size_names[i]}"
    else:
        return f"{s} {size_names[i]}"


def get_file_type(file_path):
    """
    Get the file type/extension from a path.

    Args:
        file_path: Path to the file

    Returns:
        File type string (e.g., "PDF", "TXT")
    """
    # Initialize mimetypes if not already done
    if not mimetypes.inited:
        mimetypes.init()

    # Get the extension
    _, ext = os.path.splitext(file_path)

    # If we have an extension, return it in uppercase without the dot
    if ext:
        return ext[1:].upper()

    # Try to guess the mime type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type.split('/')[1].upper()

    return "FILE"


def scan_directory(directory_path, recursive=False):
    """
    Scan a directory for files.

    Args:
        directory_path: Path to the directory to scan
        recursive: Whether to scan subdirectories

    Returns:
        Tuple of (file_list, total_size) where file_list is a list of dictionaries 
        with file information and total_size is the sum of all file sizes
    """
    file_list = []
    total_size = 0

    try:
        # List all files in the directory
        items = os.listdir(directory_path)

        for item in items:
            item_path = os.path.join(directory_path, item)

            # Skip if it's a directory and we're not recursing
            if os.path.isdir(item_path) and not recursive:
                continue

            # If it's a file, add it to our list
            if os.path.isfile(item_path):
                try:
                    # Get file stats
                    stats = os.stat(item_path)
                    size = stats.st_size
                    modified = datetime.fromtimestamp(stats.st_mtime)

                    # Add to the list
                    file_list.append({
                        'name': item,
                        'path': item_path,
                        'size': size,
                        'modified': modified,
                        'type': get_file_type(item_path)
                    })

                    total_size += size
                except (PermissionError, FileNotFoundError):
                    # Skip files we can't access
                    continue

            # If it's a directory and we're recursing, process it
            elif os.path.isdir(item_path) and recursive:
                try:
                    sub_files, sub_size = scan_directory(
                        item_path, recursive=True)
                    file_list.extend(sub_files)
                    total_size += sub_size
                except (PermissionError, FileNotFoundError):
                    # Skip directories we can't access
                    continue

    except (PermissionError, FileNotFoundError):
        # Return empty list if we can't access the directory
        return [], 0

    return file_list, total_size


def get_directory_size(directory_path):
    """
    Calculate the total size of a directory.

    Args:
        directory_path: Path to the directory

    Returns:
        Total size in bytes
    """
    _, total_size = scan_directory(directory_path, recursive=True)
    return total_size
