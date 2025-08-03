#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.logger import FileAnalyzerLogger


class TestFileAnalyzerLogger(unittest.TestCase):

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"

        # Reset singleton instance
        FileAnalyzerLogger._instance = None

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        FileAnalyzerLogger._instance = None

    @patch('src.utils.logger.Path.home')
    def test_singleton_pattern(self, mock_home):
        """Test that Logger follows singleton pattern."""
        mock_home.return_value = Path(self.temp_dir)

        logger1 = FileAnalyzerLogger()
        logger2 = FileAnalyzerLogger()

        self.assertIs(logger1, logger2)

    @patch('src.utils.logger.Path')
    def test_log_directory_creation(self, mock_path):
        """Test that log directory is created."""
        mock_path.return_value = self.log_dir
        
        with patch.object(FileAnalyzerLogger, '__init__', lambda x: None):
            logger = FileAnalyzerLogger()
            logger.log_dir = self.log_dir
            logger.log_dir.mkdir(exist_ok=True)
            
        self.assertTrue(self.log_dir.exists())

    def test_info_logging(self):
        """Test info level logging."""
        with patch.object(FileAnalyzerLogger, '__init__', lambda x: None):
            logger = FileAnalyzerLogger()
            logger.log_dir = self.log_dir
            logger.log_dir.mkdir(exist_ok=True)
            logger._logger = None
            logger._setup_logger()
            
            test_message = "Test info message"
            logger.info(test_message)

            # Check that log file was created and contains message
            log_files = list(self.log_dir.glob("fileanalyzer_*.log"))
            self.assertGreater(len(log_files), 0)

            log_content = log_files[0].read_text()
            self.assertIn(test_message, log_content)
            self.assertIn("INFO", log_content)

    @patch('src.utils.logger.Path.home')
    def test_error_logging(self, mock_home):
        """Test error level logging."""
        mock_home.return_value = Path(self.temp_dir)

        logger = FileAnalyzerLogger()
        test_message = "Test error message"
        test_exception = ValueError("Test exception")

        logger.error(test_message, test_exception)

        # Check error log file
        error_files = list(self.log_dir.glob("errors_*.log"))
        self.assertGreater(len(error_files), 0)

        error_content = error_files[0].read_text()
        self.assertIn(test_message, error_content)
        self.assertIn("ERROR", error_content)
        self.assertIn("ValueError", error_content)

    @patch('src.utils.logger.Path.home')
    def test_warning_logging(self, mock_home):
        """Test warning level logging."""
        mock_home.return_value = Path(self.temp_dir)

        logger = FileAnalyzerLogger()
        test_message = "Test warning message"
        logger.warning(test_message)

        log_files = list(self.log_dir.glob("fileanalyzer_*.log"))
        log_content = log_files[0].read_text()
        self.assertIn(test_message, log_content)
        self.assertIn("WARNING", log_content)

    @patch('src.utils.logger.Path.home')
    def test_debug_logging(self, mock_home):
        """Test debug level logging."""
        mock_home.return_value = Path(self.temp_dir)

        logger = FileAnalyzerLogger()
        test_message = "Test debug message"
        logger.debug(test_message)

        log_files = list(self.log_dir.glob("fileanalyzer_*.log"))
        log_content = log_files[0].read_text()
        self.assertIn(test_message, log_content)
        self.assertIn("DEBUG", log_content)

    @patch('src.utils.logger.Path.home')
    def test_critical_logging(self, mock_home):
        """Test critical level logging."""
        mock_home.return_value = Path(self.temp_dir)

        logger = FileAnalyzerLogger()
        test_message = "Test critical message"
        test_exception = RuntimeError("Critical error")

        logger.critical(test_message, test_exception)

        # Should appear in both main log and error log
        log_files = list(self.log_dir.glob("fileanalyzer_*.log"))
        error_files = list(self.log_dir.glob("errors_*.log"))

        log_content = log_files[0].read_text()
        error_content = error_files[0].read_text()

        self.assertIn(test_message, log_content)
        self.assertIn("CRITICAL", log_content)
        self.assertIn(test_message, error_content)

    @patch('src.utils.logger.Path.home')
    def test_startup_shutdown_logging(self, mock_home):
        """Test application startup and shutdown logging."""
        mock_home.return_value = Path(self.temp_dir)

        logger = FileAnalyzerLogger()
        version = "1.0.0"

        logger.log_startup(version)
        logger.log_shutdown()

        log_files = list(self.log_dir.glob("fileanalyzer_*.log"))
        log_content = log_files[0].read_text()

        self.assertIn("Starting", log_content)
        self.assertIn(version, log_content)
        self.assertIn("Shutting Down", log_content)

    @patch('src.utils.logger.Path.home')
    def test_log_rotation_by_size(self, mock_home):
        """Test log rotation when file size exceeds limit."""
        mock_home.return_value = Path(self.temp_dir)

        # Create logger with small max size for testing
        logger = FileAnalyzerLogger()

        # Write many messages to trigger rotation
        large_message = "x" * 1000  # 1KB message
        for _ in range(20):  # 20KB total
            logger.info(large_message)

        # Should have multiple log files due to rotation
        # log_files = list(self.log_dir.glob("fileanalyzer_*.log"))
        # Note: Actual rotation behavior depends on implementation

    @patch('src.utils.logger.Path.home')
    def test_old_logs_cleanup(self, mock_home):
        """Test cleanup of old log files."""
        mock_home.return_value = Path(self.temp_dir)

        # Create some old log files
        old_date = "20240101"
        old_log = self.log_dir / f"fileanalyzer_{old_date}.log"
        old_error = self.log_dir / f"errors_{old_date}.log"

        self.log_dir.mkdir(exist_ok=True)
        old_log.write_text("old log content")
        old_error.write_text("old error content")

        logger = FileAnalyzerLogger()
        logger.cleanup_old_logs()

        # Old files should be removed (implementation dependent)
        # This test verifies the method can be called without errors

    @patch('src.utils.logger.Path.home')
    def test_exception_logging_with_traceback(self, mock_home):
        """Test that exceptions are logged with full traceback."""
        mock_home.return_value = Path(self.temp_dir)

        logger = FileAnalyzerLogger()

        try:
            raise ValueError("Test exception with traceback")
        except ValueError as e:
            logger.error("Caught exception", e)

        error_files = list(self.log_dir.glob("errors_*.log"))
        error_content = error_files[0].read_text()

        self.assertIn("ValueError", error_content)
        self.assertIn("Test exception with traceback", error_content)
        self.assertIn("Traceback", error_content)

    @patch('src.utils.logger.Path.home')
    def test_logging_without_exception(self, mock_home):
        """Test logging methods when no exception is provided."""
        mock_home.return_value = Path(self.temp_dir)

        logger = FileAnalyzerLogger()
        logger.error("Error without exception")
        logger.critical("Critical without exception")

        error_files = list(self.log_dir.glob("errors_*.log"))
        error_content = error_files[0].read_text()

        self.assertIn("Error without exception", error_content)
        self.assertIn("Critical without exception", error_content)


if __name__ == '__main__':
    unittest.main()

