#!/usr/bin/env python3
# File: src/ui/themes/theme_manager.py

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from .styles import BorderRadius, DarkTheme, ModernTheme, Spacing, Typography


class ThemeManager(QObject):
    """
    Central theme manager for the File Analyzer application.
    Handles theme switching, stylesheet management, and theme-related utilities.
    """

    # Signal emitted when theme changes
    theme_changed = pyqtSignal(str)  # theme_name

    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.themes_dir = Path(__file__).parent

    def apply_theme(self, theme_name="light"):
        """
        Apply a theme to the application.

        Args:
            theme_name: Name of the theme to apply ("light" or "dark")
        """
        app = QApplication.instance()
        if not app:
            return

        # Load the appropriate stylesheet
        stylesheet = self.get_stylesheet(theme_name)
        app.setStyleSheet(stylesheet)

        # Update current theme
        self.current_theme = theme_name
        self.theme_changed.emit(theme_name)

    def get_stylesheet(self, theme_name="light"):
        """
        Get the complete stylesheet for the specified theme.

        Args:
            theme_name: Name of the theme

        Returns:
            Complete CSS stylesheet as string
        """
        if theme_name == "dark":
            return self._get_dark_stylesheet()
        else:
            return self._get_light_stylesheet()

    def _get_light_stylesheet(self):
        """Generate the light theme stylesheet."""
        return f"""
        /* Main Application Window */
        QMainWindow {{
            background-color: {ModernTheme.BACKGROUND.name()};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            font-family: {Typography.MAIN_FONT};
            font-size: {Typography.FONT_MD};
        }}

        /* Panels and Containers */
        QWidget {{
            background-color: {ModernTheme.PANEL_BACKGROUND.name()};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            border-radius: {BorderRadius.SM};
        }}

        QFrame {{
            background-color: {ModernTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: {BorderRadius.MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {ModernTheme.MEDIUM_GRAY.name()};
            width: 2px;
            height: 2px;
        }}

        QSplitter::handle:hover {{
            background-color: {ModernTheme.PRIMARY.name()};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {ModernTheme.PRIMARY.name()};
            color: {ModernTheme.WHITE.name()};
            border: none;
            border-radius: {BorderRadius.SM};
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            font-size: {Typography.FONT_MD};
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {ModernTheme.PRIMARY_DARK.name()};
        }}

        QPushButton:pressed {{
            background-color: {ModernTheme.PRIMARY_DARK.name()};
            padding-top: {Spacing.SM + 1}px;
        }}

        QPushButton:disabled {{
            background-color: {ModernTheme.MEDIUM_GRAY.name()};
            color: {ModernTheme.DARK_GRAY.name()};
        }}

        /* Labels */
        QLabel {{
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background-color: transparent;
            border: none;
        }}

        /* Title Cards and Headers */
        QLabel[class=\"title\"] {{
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            font-weight: {Typography.WEIGHT_BOLD};
            background-color: transparent;
        }}

        QLabel[class=\"subtitle\"] {{
            color: {ModernTheme.DARK_GRAY.name()};
            background-color: transparent;
        }}

        /* Main Title */
        QLabel#main_title {{
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background-color: transparent;
        }}

        /* Card Widget Containers */
        CardWidget {{
            background-color: {ModernTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {ModernTheme.BORDER.name()};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            border-radius: 8px;
        }}

        TitleCard {{
            background-color: {ModernTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {ModernTheme.BORDER.name()};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            border-radius: 8px;
        }}

        /* Separator Lines */
        QFrame#separator {{
            background-color: {ModernTheme.MEDIUM_GRAY.name()};
            border: none;
            max-height: 1px;
        }}

        /* Input Fields */
        QLineEdit {{
            background-color: {ModernTheme.WHITE.name()};
            border: 1px solid {ModernTheme.MEDIUM_GRAY.name()};
            border-radius: {BorderRadius.SM};
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-size: {Typography.FONT_MD};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
        }}

        QLineEdit:focus {{
            border: 2px solid {ModernTheme.PRIMARY.name()};
            padding: {Spacing.SM - 1}px {Spacing.MD - 1}px;
        }}

        QLineEdit::placeholder {{
            color: {ModernTheme.DARK_GRAY.name()};
        }}

        /* Tree View */
        QTreeView {{
            background-color: {ModernTheme.WHITE.name()};
            border: 1px solid {ModernTheme.MEDIUM_GRAY.name()};
            border-radius: {BorderRadius.MD};
            selection-background-color: {ModernTheme.PRIMARY.name()};
            outline: none;
            color: {ModernTheme.VERY_DARK_GRAY.name()};
        }}

        QTreeView::item {{
            padding: {Spacing.XS}px {Spacing.SM}px;
            border: none;
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            background-color: {ModernTheme.WHITE.name()};
        }}

        QTreeView::item:hover {{
            background-color: {ModernTheme.PRIMARY_LIGHT.name()};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
        }}

        QTreeView::item:selected {{
            background-color: {ModernTheme.PRIMARY.name()};
            color: {ModernTheme.WHITE.name()};
        }}

        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: none;
        }}

        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {{
            border-image: none;
            image: none;
        }}

        /* Table View */
        QTableView {{
            background-color: {ModernTheme.WHITE.name()};
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: {BorderRadius.MD};
            gridline-color: {ModernTheme.MEDIUM_GRAY.name()};
            selection-background-color: {ModernTheme.FILE_ROW_SELECTED.name()};
            outline: none;
            alternate-background-color: {ModernTheme.FILE_ROW_BACKGROUND.name()};
        }}

        QTableView::item {{
            padding: {Spacing.SM}px;
            border: none;
            background-color: {ModernTheme.FILE_ROW_BACKGROUND.name()};
            color: {ModernTheme.FILE_ROW_TEXT.name()};
            min-height: 24px;
        }}

        QTableView::item:hover {{
            background-color: {ModernTheme.FILE_ROW_HOVER.name()};
            color: {ModernTheme.FILE_ROW_TEXT.name()};
        }}

        QTableView::item:selected {{
            background-color: {ModernTheme.FILE_ROW_SELECTED.name()};
            color: {ModernTheme.WHITE.name()};
        }}

        QTableView::item:alternate {{
            background-color: {ModernTheme.FILE_ROW_BACKGROUND.name()};
        }}

        /* Header Views */
        QHeaderView::section {{
            background-color: {ModernTheme.LIGHT_GRAY.name()};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            padding: {Spacing.MD}px {Spacing.SM}px;
            font-weight: {Typography.WEIGHT_BOLD};
            font-size: {Typography.FONT_MD};
            border: none;
            border-bottom: 1px solid {ModernTheme.MEDIUM_GRAY.name()};
        }}

        QHeaderView::section:hover {{
            background-color: {ModernTheme.MEDIUM_GRAY.name()};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            background-color: {ModernTheme.WHITE.name()};
            border: 1px solid {ModernTheme.BORDER.name()};
            border-radius: {BorderRadius.MD};
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: {ModernTheme.LIGHT_GRAY.name()};
            color: {ModernTheme.DARK_GRAY.name()};
            padding: {Spacing.SM}px {Spacing.MD}px;
            margin-right: 2px;
            border-top-left-radius: {BorderRadius.SM};
            border-top-right-radius: {BorderRadius.SM};
        }}

        QTabBar::tab:selected {{
            background-color: {ModernTheme.WHITE.name()};
            color: {ModernTheme.VERY_DARK_GRAY.name()};
            font-weight: {Typography.WEIGHT_MEDIUM};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {ModernTheme.HOVER.name()};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {ModernTheme.LIGHT_GRAY.name()};
            border-top: 1px solid {ModernTheme.BORDER.name()};
            color: {ModernTheme.DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
        }}

        /* Scroll Bars */
        QScrollBar:vertical {{
            background: {ModernTheme.LIGHT_GRAY.name()};
            width: 12px;
            border-radius: {BorderRadius.SM};
        }}

        QScrollBar::handle:vertical {{
            background: {ModernTheme.MEDIUM_GRAY.name()};
            border-radius: {BorderRadius.SM};
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {ModernTheme.PRIMARY.name()};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}

        QScrollBar:horizontal {{
            background: {ModernTheme.LIGHT_GRAY.name()};
            height: 12px;
            border-radius: {BorderRadius.SM};
        }}

        QScrollBar::handle:horizontal {{
            background: {ModernTheme.MEDIUM_GRAY.name()};
            border-radius: {BorderRadius.SM};
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {ModernTheme.PRIMARY.name()};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
        }}
        """

    def _get_dark_stylesheet(self):
        """Generate the dark theme stylesheet."""
        return f"""
        /* Main Application Window */
        QMainWindow {{
            background-color: {DarkTheme.BACKGROUND.name()};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            font-family: {Typography.MAIN_FONT};
            font-size: {Typography.FONT_MD};
        }}

        /* Panels and Containers */
        QWidget {{
            background-color: {DarkTheme.PANEL_BACKGROUND.name()};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            border: none;
        }}

        QFrame {{
            background-color: {DarkTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {DarkTheme.BORDER.name()};
            border-radius: {BorderRadius.MD};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
        }}

        /* Card Widget Containers for better contrast */
        CardWidget {{
            background-color: {DarkTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {DarkTheme.BORDER.name()};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            border-radius: 8px;
        }}

        TitleCard {{
            background-color: {DarkTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {DarkTheme.BORDER.name()};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            border-radius: 8px;
        }}

        /* Separator Lines */
        QFrame#separator {{
            background-color: {DarkTheme.MEDIUM_GRAY.name()};
            border: none;
            max-height: 1px;
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {DarkTheme.BORDER.name()};
            background-color: {DarkTheme.PANEL_BACKGROUND.name()};
            border-radius: {BorderRadius.MD};
        }}

        QTabBar::tab {{
            background-color: {DarkTheme.LIGHT_GRAY.name()};
            color: {DarkTheme.DARK_GRAY.name()};
            padding: {Spacing.SM}px {Spacing.LG}px;
            margin-right: 2px;
            border-top-left-radius: {BorderRadius.MD};
            border-top-right-radius: {BorderRadius.MD};
            font-size: {Typography.FONT_MD};
            font-weight: {Typography.WEIGHT_MEDIUM};
        }}

        QTabBar::tab:selected {{
            background-color: {DarkTheme.PRIMARY.name()};
            color: {DarkTheme.WHITE.name()};
            font-weight: {Typography.WEIGHT_BOLD};
        }}

        QTabBar::tab:hover {{
            background-color: {DarkTheme.PRIMARY_LIGHT.name()};
            color: {DarkTheme.WHITE.name()};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {DarkTheme.PRIMARY.name()};
            color: {DarkTheme.WHITE.name()};
            border: none;
            border-radius: {BorderRadius.SM};
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            font-size: {Typography.FONT_MD};
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {DarkTheme.PRIMARY_DARK.name()};
        }}

        QPushButton:pressed {{
            background-color: {DarkTheme.PRIMARY_DARK.name()};
            padding-top: {Spacing.SM + 1}px;
        }}

        QPushButton:disabled {{
            background-color: {DarkTheme.MEDIUM_GRAY.name()};
            color: {DarkTheme.DARK_GRAY.name()};
        }}

        /* Labels */
        QLabel {{
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            background-color: transparent;
            border: none;
        }}

        /* Title Cards and Headers */
        QLabel[class=\"title\"] {{
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            font-weight: {Typography.WEIGHT_BOLD};
            background-color: transparent;
        }}

        QLabel[class=\"subtitle\"] {{
            color: {DarkTheme.DARK_GRAY.name()};
            background-color: transparent;
        }}

        /* Directories and File Distribution Labels */
        CardWidget QLabel {{
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            background-color: transparent;
        }}

        TitleCard QLabel {{
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            background-color: transparent;
        }}

        /* Main Title */
        QLabel#main_title {{
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            background-color: transparent;
        }}

        /* Input Fields */
        QLineEdit {{
            background-color: {DarkTheme.LIGHT_GRAY.name()};
            border: 1px solid {DarkTheme.MEDIUM_GRAY.name()};
            border-radius: {BorderRadius.SM};
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-size: {Typography.FONT_MD};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
        }}

        QLineEdit:focus {{
            border: 2px solid {DarkTheme.PRIMARY.name()};
            padding: {Spacing.SM - 1}px {Spacing.MD - 1}px;
        }}

        QLineEdit::placeholder {{
            color: {DarkTheme.DARK_GRAY.name()};
        }}

        /* Tree View */
        QTreeView {{
            background-color: {DarkTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {DarkTheme.BORDER.name()};
            border-radius: {BorderRadius.MD};
            selection-background-color: {DarkTheme.PRIMARY.name()};
            outline: none;
            color: {DarkTheme.VERY_DARK_GRAY.name()};
        }}

        QTreeView::item {{
            padding: {Spacing.SM}px;
            border: none;
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            background-color: {DarkTheme.PANEL_BACKGROUND.name()};
        }}

        QTreeView::item:hover {{
            background-color: {DarkTheme.HOVER.name()};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
        }}

        QTreeView::item:selected {{
            background-color: {DarkTheme.PRIMARY.name()};
            color: {DarkTheme.WHITE.name()};
        }}

        QTreeView::branch:has-siblings:!adjoins-item {{
            border-image: none;
            image: none;
        }}

        QTreeView::branch:has-siblings:adjoins-item {{
            border-image: none;
            image: none;
        }}

        QTreeView::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: none;
            image: none;
        }}

        /* Table View */
        QTableView {{
            background-color: {DarkTheme.PANEL_BACKGROUND.name()};
            border: 1px solid {DarkTheme.BORDER.name()};
            border-radius: {BorderRadius.MD};
            gridline-color: {DarkTheme.MEDIUM_GRAY.name()};
            selection-background-color: {DarkTheme.FILE_ROW_SELECTED.name()};
            outline: none;
            alternate-background-color: {DarkTheme.FILE_ROW_BACKGROUND.name()};
        }}

        QTableView::item {{
            padding: {Spacing.SM}px;
            border: none;
            background-color: {DarkTheme.FILE_ROW_BACKGROUND.name()};
            color: {DarkTheme.FILE_ROW_TEXT.name()};
            min-height: 24px;
        }}

        QTableView::item:hover {{
            background-color: {DarkTheme.FILE_ROW_HOVER.name()};
            color: {DarkTheme.FILE_ROW_TEXT.name()};
        }}

        QTableView::item:selected {{
            background-color: {DarkTheme.FILE_ROW_SELECTED.name()};
            color: {DarkTheme.WHITE.name()};
        }}

        QTableView::item:alternate {{
            background-color: {DarkTheme.FILE_ROW_BACKGROUND.name()};
        }}

        /* Header Views */
        QHeaderView::section {{
            background-color: {DarkTheme.LIGHT_GRAY.name()};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            padding: {Spacing.MD}px {Spacing.SM}px;
            font-weight: {Typography.WEIGHT_BOLD};
            font-size: {Typography.FONT_MD};
            border: none;
            border-bottom: 1px solid {DarkTheme.MEDIUM_GRAY.name()};
        }}

        QHeaderView::section:hover {{
            background-color: {DarkTheme.MEDIUM_GRAY.name()};
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {DarkTheme.MEDIUM_GRAY.name()};
        }}

        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        QSplitter::handle:vertical {{
            height: 2px;
        }}

        /* Progress Bar */
        QProgressBar {{
            background-color: {DarkTheme.LIGHT_GRAY.name()};
            border: 1px solid {DarkTheme.BORDER.name()};
            border-radius: {BorderRadius.SM};
            text-align: center;
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            font-size: {Typography.FONT_SM};
        }}

        QProgressBar::chunk {{
            background-color: {DarkTheme.PRIMARY.name()};
            border-radius: {BorderRadius.SM};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {DarkTheme.LIGHT_GRAY.name()};
            color: {DarkTheme.VERY_DARK_GRAY.name()};
            border-top: 1px solid {DarkTheme.BORDER.name()};
            font-size: {Typography.FONT_SM};
        }}

        /* Scroll Bars */
        QScrollBar:vertical {{
            background: {DarkTheme.LIGHT_GRAY.name()};
            width: 15px;
            border-radius: {BorderRadius.SM};
        }}

        QScrollBar::handle:vertical {{
            background: {DarkTheme.MEDIUM_GRAY.name()};
            border-radius: {BorderRadius.SM};
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {DarkTheme.PRIMARY.name()};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}

        QScrollBar:horizontal {{
            background: {DarkTheme.LIGHT_GRAY.name()};
            height: 15px;
            border-radius: {BorderRadius.SM};
        }}

        QScrollBar::handle:horizontal {{
            background: {DarkTheme.MEDIUM_GRAY.name()};
            border-radius: {BorderRadius.SM};
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {DarkTheme.PRIMARY.name()};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
        }}
        """

    def get_color(self, color_name):
        """
        Get a color from the current theme.

        Args:
            color_name: Name of the color (e.g., "PRIMARY", "BACKGROUND")

        Returns:
            QColor object
        """
        theme_class = DarkTheme if self.current_theme == "dark" else ModernTheme
        return getattr(theme_class, color_name, theme_class.PRIMARY)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def get_current_theme(self):
        """Get the current theme name."""
        return self.current_theme


# Global theme manager instance
theme_manager = ThemeManager()
