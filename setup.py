#!/usr/bin/env python3
# File: setup.py

from setuptools import find_packages, setup

# Get version from src/__init__.py
with open('src/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'").strip('"')
            break

setup(
    name="file-system-analyzer",
    version=version,
    description="A desktop application for visualizing and analyzing file system data",
    author="Anirban Das",
    author_email="anirbandas59@outlook.com",
    url="https://github.com/yourusername/file-system-analyzer",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Desktop Environment",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "file-analyzer=src.main:main",
        ],
    },
    python_requires=">=3.8",
)
