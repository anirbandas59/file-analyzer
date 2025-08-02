#!/usr/bin/env python3
# File: setup.py

from setuptools import find_packages, setup


# Read the long description from README.md
def read_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "A comprehensive desktop application for smart file management and analysis."


# Get version from src/__init__.py
def get_version():
    try:
        with open("src/__init__.py", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip("'").strip('"')
    except FileNotFoundError:
        pass
    return "1.0.0"


version = get_version()

setup(
    name="fileanalyzer",
    version=version,
    description="Smart File Management - Large File Analyzer, File Age Analyzer, Duplicate Finder, and Archival Recommendations.",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="FileAnalyzer Development Team",
    author_email="contact@fileanalyzer.dev",
    url="https://github.com/fileanalyzer/FileAnalyzer",
    project_urls={
        "Bug Reports": "https://github.com/fileanalyzer/FileAnalyzer/issues",
        "Source": "https://github.com/fileanalyzer/FileAnalyzer",
        "Documentation": "https://github.com/fileanalyzer/FileAnalyzer/wiki",
    },
    packages=find_packages(),
    package_data={
        "src": ["**/*.py"],
        "src.ui": ["**/*.py"],
        "src.ui.themes": ["**/*.py"],
        "src.ui.components": ["**/*.py"],
        "src.utils": ["**/*.py"],
    },
    include_package_data=True,
    install_requires=[
        "PyQt6==6.9.1",
        "PyQt6-Qt6==6.9.1", 
        "PyQt6-sip==13.10.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "pytest-cov>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Desktop Environment :: File Managers",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "fileanalyzer=src.main:main",
            "file-analyzer=src.main:main",
        ],
        "gui_scripts": [
            "fileanalyzer-gui=src.main:main",
        ],
    },
    python_requires=">=3.10",
    keywords=[
        "file management",
        "large file analyzer",
        "file age analyzer",
        "duplicate finder",
        "disk cleanup",
        "archival",
        "file organization",
        "storage optimization",
    ],
    zip_safe=False,
)
