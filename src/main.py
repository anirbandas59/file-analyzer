#!/usr/bin/env python3
# File: src/main.py

import sys

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main():
    """
    Main entry point for the File Analyzer application.
    Initializes the Qt application and main window.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("File Analyzer")
    app.setStyle("Fusion")

    # Create and show the main window
    main_window = MainWindow()
    main_window.resize(1024, 768)
    main_window.show()

    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
