#!/usr/bin/env python3
# File: src/main.py

import sys
import atexit

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.themes.theme_manager import theme_manager
from src.utils.logger import logger
from src.utils.settings import settings


def main():
    """
    Main entry point for the File Analyzer application.
    Initializes the Qt application and main window.
    """
    try:
        # Initialize logging and settings
        logger.log_startup("1.0.0")
        logger.info("Initializing File Analyzer application")
        
        # Register shutdown handler
        atexit.register(shutdown_handler)
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("File Analyzer")
        app.setStyle("Fusion")
        logger.info("Qt application initialized")

        # Load theme from settings
        saved_theme = settings.get_theme()
        theme_manager.apply_theme(saved_theme)
        logger.info(f"Applied theme: {saved_theme}")

        # Create and configure main window
        main_window = MainWindow()
        
        # Restore window geometry from settings
        geometry = settings.get_window_geometry()
        main_window.resize(geometry["width"], geometry["height"])
        main_window.move(geometry["x"], geometry["y"])
        
        if geometry["maximized"]:
            main_window.showMaximized()
        else:
            main_window.show()
            
        logger.info(f"Main window created and shown: {geometry}")

        # Setup application exit handler
        def on_app_exit():
            logger.info("Application exit requested")
            # Save window geometry
            if not main_window.isMaximized():
                geo = main_window.geometry()
                settings.set_window_geometry(
                    geo.width(), geo.height(), 
                    geo.x(), geo.y(), 
                    main_window.isMaximized()
                )
            else:
                settings.set("window.maximized", True)
            
            logger.log_shutdown()
        
        app.aboutToQuit.connect(on_app_exit)

        # Start the application event loop
        logger.info("Starting application event loop")
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical("Fatal error during application startup", e)
        sys.exit(1)


def shutdown_handler():
    """Handle application shutdown cleanup."""
    try:
        logger.info("Application shutdown handler called")
        # Cleanup old logs
        logger.cleanup_old_logs()
        # Cleanup old settings
        settings.cleanup_old_settings()
    except Exception as e:
        print(f"Error during shutdown: {e}")


if __name__ == "__main__":
    main()
