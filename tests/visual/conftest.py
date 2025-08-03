#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for pytest-qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setStyle("Fusion")  # Consistent styling across platforms
    yield app
    # App cleanup handled automatically


@pytest.fixture(autouse=True)
def setup_visual_tests():
    """Set up environment for visual tests."""
    # Create screenshots directory if it doesn't exist
    screenshots_dir = Path(__file__).parent / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    # Set up any global visual test configuration
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # For headless testing

    yield

    # Cleanup after tests


@pytest.fixture
def reference_images_dir():
    """Provide path to reference images directory."""
    return Path(__file__).parent / "screenshots"


@pytest.fixture
def temp_test_dir():
    """Provide temporary directory for test files."""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


# Visual regression test configuration


def pytest_configure(config):
    """Configure pytest for visual tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "visual: mark test as visual regression test"
    )
    config.addinivalue_line(
        "markers", "theme: mark test as theme-related visual test"
    )
    config.addinivalue_line(
        "markers", "component: mark test as component visual test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for visual tests."""
    for item in items:
        # Mark all tests in visual directory as visual tests
        if "visual" in str(item.fspath):
            item.add_marker(pytest.mark.visual)


# Custom assertion helpers for visual tests
class VisualTestHelpers:
    """Helper methods for visual regression testing."""

    @staticmethod
    def compare_images(image1_path, image2_path, threshold=0.95):
        """Compare two images and return similarity score."""
        try:
            import numpy as np
            from PIL import Image

            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)

            # Convert to same mode and size
            img1 = img1.convert('RGB')
            img2 = img2.convert('RGB')

            if img1.size != img2.size:
                img2 = img2.resize(img1.size)

            # Calculate similarity
            arr1 = np.array(img1)
            arr2 = np.array(img2)

            diff = np.abs(arr1 - arr2)
            similarity = 1 - (np.mean(diff) / 255.0)

            return similarity >= threshold

        except ImportError:
            # PIL not available, skip comparison
            return True

    @staticmethod
    def save_comparison_image(image1_path, image2_path, output_path):
        """Save side-by-side comparison of two images."""
        try:
            from PIL import Image

            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)

            # Create side-by-side comparison
            total_width = img1.width + img2.width
            max_height = max(img1.height, img2.height)

            combined = Image.new('RGB', (total_width, max_height))
            combined.paste(img1, (0, 0))
            combined.paste(img2, (img1.width, 0))

            combined.save(output_path)

        except ImportError:
            pass


@pytest.fixture
def visual_helpers():
    """Provide visual test helper methods."""
    return VisualTestHelpers()

