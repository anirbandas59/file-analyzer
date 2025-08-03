#!/usr/bin/env python3
# File: src/utils/settings.py

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .logger import logger


class SettingsManager:
    """
    Manages application settings persistence.

    Features:
    - JSON-based configuration storage
    - Default values for all settings
    - Recent directories tracking
    - Theme preferences
    - Window geometry persistence
    - Automatic backup and recovery
    """

    _instance: Optional['SettingsManager'] = None

    def __new__(cls) -> 'SettingsManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True

        # Setup paths
        self.config_dir = Path.home() / ".fileanalyzer"
        self.config_dir.mkdir(exist_ok=True)

        self.settings_file = self.config_dir / "settings.json"
        self.backup_file = self.config_dir / "settings_backup.json"

        # Default settings
        self._defaults = {
            "version": "1.0.0",
            "theme": "light",
            "last_directory": str(Path.home()),
            "recent_directories": [],
            "max_recent_directories": 10,
            "window": {
                "width": 1024,
                "height": 768,
                "maximized": False,
                "x": 100,
                "y": 100
            },
            "scan": {
                "include_hidden": False,
                "follow_symlinks": False,
                "max_file_size_mb": 1000,
                "timeout_seconds": 30
            },
            "display": {
                "show_file_extensions": True,
                "date_format": "%Y-%m-%d %H:%M:%S",
                "size_format": "auto"
            },
            "performance": {
                "cache_enabled": True,
                "max_cache_size_mb": 100,
                "background_scanning": True
            },
            "logging": {
                "level": "INFO",
                "keep_logs_days": 30,
                "console_output": True
            },
            "last_updated": datetime.now().isoformat()
        }

        # Load settings
        self._settings = self._load_settings()
        logger.info(f"Settings loaded from: {self.settings_file}")

    def _load_settings(self) -> dict[str, Any]:
        """Load settings from file with fallback to defaults."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, encoding='utf-8') as f:
                    loaded = json.load(f)

                # Merge with defaults to handle new settings
                settings = self._defaults.copy()
                self._deep_update(settings, loaded)

                logger.info("Settings loaded successfully")
                return settings

        except Exception as e:
            logger.error("Failed to load settings, trying backup", e)

            # Try backup file
            try:
                if self.backup_file.exists():
                    with open(self.backup_file, encoding='utf-8') as f:
                        loaded = json.load(f)

                    settings = self._defaults.copy()
                    self._deep_update(settings, loaded)

                    logger.warning("Settings restored from backup")
                    return settings

            except Exception as backup_e:
                logger.error("Failed to load backup settings", backup_e)

        logger.info("Using default settings")
        return self._defaults.copy()

    def _deep_update(self, base_dict: dict, update_dict: dict):
        """Recursively update nested dictionary."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def save(self) -> bool:
        """Save current settings to file."""
        try:
            # Create backup of current settings
            if self.settings_file.exists():
                with open(self.settings_file, encoding='utf-8') as src:
                    with open(self.backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())

            # Update timestamp
            self._settings["last_updated"] = datetime.now().isoformat()

            # Save new settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)

            logger.debug("Settings saved successfully")
            return True

        except Exception as e:
            logger.error("Failed to save settings", e)
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value using dot notation (e.g., 'window.width')."""
        keys = key.split('.')
        value = self._settings

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> bool:
        """Set setting value using dot notation."""
        keys = key.split('.')
        current = self._settings

        try:
            # Navigate to parent
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]

            # Set value
            current[keys[-1]] = value

            logger.debug(f"Setting updated: {key} = {value}")
            return True

        except Exception as e:
            logger.error(f"Failed to set setting {key}", e)
            return False

    def get_theme(self) -> str:
        """Get current theme."""
        return self.get("theme", "light")

    def set_theme(self, theme: str):
        """Set current theme."""
        if theme in ["light", "dark"]:
            self.set("theme", theme)
            self.save()
            logger.info(f"Theme changed to: {theme}")

    def get_recent_directories(self) -> list[str]:
        """Get list of recent directories."""
        return self.get("recent_directories", [])

    def add_recent_directory(self, path: str):
        """Add directory to recent list."""
        recent = self.get_recent_directories()
        path = str(Path(path).resolve())

        # Remove if already exists
        if path in recent:
            recent.remove(path)

        # Add to beginning
        recent.insert(0, path)

        # Limit size
        max_recent = self.get("max_recent_directories", 10)
        recent = recent[:max_recent]

        self.set("recent_directories", recent)
        self.save()

        logger.debug(f"Added recent directory: {path}")

    def get_last_directory(self) -> str:
        """Get last used directory."""
        return self.get("last_directory", str(Path.home()))

    def set_last_directory(self, path: str):
        """Set last used directory."""
        path = str(Path(path).resolve())
        self.set("last_directory", path)
        self.save()

    def get_window_geometry(self) -> dict[str, Any]:
        """Get window geometry settings."""
        return self.get("window", {
            "width": 1024,
            "height": 768,
            "maximized": False,
            "x": 100,
            "y": 100
        })

    def set_window_geometry(self, width: int, height: int, x: int, y: int,
                           maximized: bool = False):
        """Set window geometry."""
        geometry = {
            "width": width,
            "height": height,
            "x": x,
            "y": y,
            "maximized": maximized
        }

        self.set("window", geometry)
        self.save()

        logger.debug(f"Window geometry saved: {geometry}")

    def get_scan_settings(self) -> dict[str, Any]:
        """Get scan configuration."""
        return self.get("scan", {
            "include_hidden": False,
            "follow_symlinks": False,
            "max_file_size_mb": 1000,
            "timeout_seconds": 30
        })

    def set_scan_setting(self, key: str, value: Any):
        """Set specific scan setting."""
        self.set(f"scan.{key}", value)
        self.save()

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self._settings = self._defaults.copy()
        self.save()
        logger.info("Settings reset to defaults")

    def export_settings(self, file_path: str) -> bool:
        """Export settings to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)

            logger.info(f"Settings exported to: {file_path}")
            return True

        except Exception as e:
            logger.error("Failed to export settings", e)
            return False

    def import_settings(self, file_path: str) -> bool:
        """Import settings from file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                imported = json.load(f)

            # Validate and merge
            if isinstance(imported, dict):
                self._deep_update(self._settings, imported)
                self.save()

                logger.info(f"Settings imported from: {file_path}")
                return True

        except Exception as e:
            logger.error("Failed to import settings", e)

        return False

    def get_all_settings(self) -> dict[str, Any]:
        """Get all settings as dictionary."""
        return self._settings.copy()

    def cleanup_old_settings(self):
        """Remove old backup files."""
        try:
            backup_files = list(self.config_dir.glob("settings_backup_*.json"))

            # Keep only the most recent 5 backups
            if len(backup_files) > 5:
                backup_files.sort(key=lambda f: f.stat().st_mtime)
                for old_backup in backup_files[:-5]:
                    old_backup.unlink()

                logger.debug(f"Cleaned up {len(backup_files) - 5} old setting backups")

        except Exception as e:
            logger.error("Failed to cleanup old settings", e)


# Global settings instance
settings = SettingsManager()
