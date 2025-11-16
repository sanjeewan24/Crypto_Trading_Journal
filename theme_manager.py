# theme_manager.py
"""
Professional Theme Manager for Trading Journal
- Dark/Light theme toggle
- Rich fonts and colors
- Emoji support
- Non-intrusive styling
"""

from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
import json
import os


class ThemeManager:
    """Manages application themes with dark/light mode toggle"""
    
    def __init__(self):
        self.current_theme = "dark"  # Default theme
        self.config_file = "theme_config.json"
        self.load_theme_preference()
        
    def load_theme_preference(self):
        """Load saved theme preference"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get('theme', 'dark')
            except:
                self.current_theme = "dark"
    
    def save_theme_preference(self):
        """Save theme preference"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'theme': self.current_theme}, f)
        except:
            pass
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.save_theme_preference()
        return self.current_theme
    
    def get_stylesheet(self):
        """Get complete stylesheet for current theme"""
        if self.current_theme == "dark":
            return self.get_dark_theme()
        else:
            return self.get_light_theme()
    
    def get_dark_theme(self):
        """Professional dark theme stylesheet"""
        return """
        /* ==================== DARK THEME ==================== */
        
        /* Main Window */
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 13px;
        }
        
        /* Labels */
        QLabel {
            color: #e0e0e0 !important;
            font-size: 13px;
            padding: 2px;
            background-color: transparent;
        }
        
        QLabel[class="header"] {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            padding: 10px;
        }
        
        QLabel[class="subheader"] {
            font-size: 16px;
            font-weight: 600;
            color: #90CAF9;
            padding: 5px;
        }
        
        /* Input Fields */
        QLineEdit, QTextEdit {
            background-color: #2d2d2d;
            border: 2px solid #3d3d3d;
            border-radius: 6px;
            padding: 8px;
            color: #e0e0e0;
            font-size: 13px;
            selection-background-color: #4CAF50;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #4CAF50;
            background-color: #333333;
        }
        
        QLineEdit:hover, QTextEdit:hover {
            border: 2px solid #555555;
        }
        
        /* Read-only fields */
        QLineEdit[readOnly="true"] {
            background-color: #252525;
            color: #b0b0b0;
            border: 2px solid #3d3d3d;
        }
        
        /* Dropdowns */
        QComboBox {
            background-color: #2d2d2d;
            border: 2px solid #3d3d3d;
            border-radius: 6px;
            padding: 8px;
            color: #e0e0e0;
            font-size: 13px;
        }
        
        QComboBox:hover {
            border: 2px solid #555555;
        }
        
        QComboBox:focus {
            border: 2px solid #4CAF50;
        }
        
        QComboBox::drop-down {
            border: none;
            padding-right: 10px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #e0e0e0;
            margin-right: 5px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            border: 2px solid #4CAF50;
            selection-background-color: #4CAF50;
            color: #e0e0e0;
            padding: 5px;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 600;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #45a049;
        }
        
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        
        /* Secondary Buttons */
        QPushButton[class="secondary"] {
            background-color: #2196F3;
        }
        
        QPushButton[class="secondary"]:hover {
            background-color: #1976D2;
        }
        
        /* Danger Buttons */
        QPushButton[class="danger"] {
            background-color: #f44336;
        }
        
        QPushButton[class="danger"]:hover {
            background-color: #d32f2f;
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
            background-color: #1e1e1e;
            border-radius: 6px;
            margin-top: -1px;  /* Overlap with tabs */
        }
        
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #e0e0e0;
            padding: 12px 30px;
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            min-width: 100px;
            letter-spacing: 0.5px;
        }
        
        QTabBar::tab:selected {
            background-color: #4CAF50;
            color: white;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #3d3d3d;
        }
        
        /* List Widgets */
        QListWidget {
            background-color: #2d2d2d;
            border: 2px solid #3d3d3d;
            border-radius: 6px;
            padding: 5px;
            color: #e0e0e0;
        }
        
        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
            margin: 2px;
        }
        
        QListWidget::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        
        QListWidget::item:hover:!selected {
            background-color: #3d3d3d;
        }
        
        /* Frames */
        QFrame {
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #4CAF50;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #45a049;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #4CAF50;
            border-radius: 6px;
            min-width: 20px;
        }
        
        /* Scroll Areas */
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        
        /* Message Boxes */
        QMessageBox {
            background-color: #2d2d2d;
        }
        
        QMessageBox QLabel {
            color: #e0e0e0;
        }
        
        /* Tooltips */
        QToolTip {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #4CAF50;
            padding: 5px;
            border-radius: 4px;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        
        QMenuBar::item:selected {
            background-color: #4CAF50;
        }
        
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
        }
        
        QMenu::item:selected {
            background-color: #4CAF50;
        }
        """
    
    def get_light_theme(self):
        """Professional light theme stylesheet"""
        return """
        /* ==================== LIGHT THEME ==================== */
        
        /* Main Window */
        QWidget {
            background-color: #f5f5f5;
            color: #212121;
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 13px;
        }
        
        /* Labels */
        QLabel {
            color: #212121 !important;
            font-size: 13px;
            padding: 2px;
            background-color: transparent;
        }
        
        QLabel[class="header"] {
            font-size: 24px;
            font-weight: bold;
            color: #2E7D32;
            padding: 10px;
        }
        
        QLabel[class="subheader"] {
            font-size: 16px;
            font-weight: 600;
            color: #1976D2;
            padding: 5px;
        }
        
        /* Input Fields */
        QLineEdit, QTextEdit {
            background-color: white;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            padding: 8px;
            color: #212121;
            font-size: 13px;
            selection-background-color: #4CAF50;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #4CAF50;
            background-color: #fafafa;
        }
        
        QLineEdit:hover, QTextEdit:hover {
            border: 2px solid #bdbdbd;
        }
        
        /* Read-only fields */
        QLineEdit[readOnly="true"] {
            background-color: #f0f0f0;
            color: #666666;
            border: 2px solid #d0d0d0;
        }
        
        /* Dropdowns */
        QComboBox {
            background-color: white;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            padding: 8px;
            color: #212121;
            font-size: 13px;
        }
        
        QComboBox:hover {
            border: 2px solid #bdbdbd;
        }
        
        QComboBox:focus {
            border: 2px solid #4CAF50;
        }
        
        QComboBox::drop-down {
            border: none;
            padding-right: 10px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #212121;
            margin-right: 5px;
        }
        
        QComboBox QAbstractItemView {
            background-color: white;
            border: 2px solid #4CAF50;
            selection-background-color: #4CAF50;
            color: #212121;
            padding: 5px;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 600;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #45a049;
        }
        
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #9e9e9e;
        }
        
        /* Secondary Buttons */
        QPushButton[class="secondary"] {
            background-color: #2196F3;
        }
        
        QPushButton[class="secondary"]:hover {
            background-color: #1976D2;
        }
        
        /* Danger Buttons */
        QPushButton[class="danger"] {
            background-color: #f44336;
        }
        
        QPushButton[class="danger"]:hover {
            background-color: #d32f2f;
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background-color: white;
            border-radius: 6px;
            margin-top: -1px;  /* Overlap with tabs */
        }
        
        QTabBar::tab {
            background-color: #fafafa;
            color: #212121;
            padding: 12px 30px;
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            min-width: 100px;
            letter-spacing: 0.5px;
        }
        
        QTabBar::tab:selected {
            background-color: #4CAF50;
            color: white;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #e0e0e0;
        }
        
        /* List Widgets */
        QListWidget {
            background-color: white;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            padding: 5px;
            color: #212121;
        }
        
        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
            margin: 2px;
        }
        
        QListWidget::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        
        QListWidget::item:hover:!selected {
            background-color: #f5f5f5;
        }
        
        /* Frames */
        QFrame {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            background-color: #fafafa;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #4CAF50;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #45a049;
        }
        
        QScrollBar:horizontal {
            background-color: #fafafa;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #4CAF50;
            border-radius: 6px;
            min-width: 20px;
        }
        
        /* Scroll Areas */
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        
        /* Message Boxes */
        QMessageBox {
            background-color: white;
        }
        
        QMessageBox QLabel {
            color: #212121;
        }
        
        /* Tooltips */
        QToolTip {
            background-color: #212121;
            color: white;
            border: 1px solid #4CAF50;
            padding: 5px;
            border-radius: 4px;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: white;
            color: #212121;
        }
        
        QMenuBar::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        
        QMenu {
            background-color: white;
            color: #212121;
            border: 1px solid #e0e0e0;
        }
        
        QMenu::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        """
    
    def create_toggle_button(self, parent):
        """Create a beautiful theme toggle button with emoji"""
        button = QPushButton(parent)
        button.setFixedSize(50, 50)
        button.setToolTip("Toggle Dark/Light Theme")
        
        # Set initial emoji based on current theme
        self.update_button_icon(button)
        
        # Custom styling for toggle button
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #4CAF50;
                border-radius: 25px;
                font-size: 24px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.1);
                border: 2px solid #45a049;
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.2);
            }
        """)
        
        return button
    
    def update_button_icon(self, button):
        """Update button emoji based on current theme"""
        if self.current_theme == "dark":
            button.setText("🌙")  # Moon for dark mode
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #4CAF50;
                    border-radius: 25px;
                    font-size: 24px;
                    padding: 5px;
                    color: #FFD700;  /* Gold color for moon */
                }
                QPushButton:hover {
                    background-color: rgba(76, 175, 80, 0.1);
                    border: 2px solid #45a049;
                }
                QPushButton:pressed {
                    background-color: rgba(76, 175, 80, 0.2);
                }
            """)
        else:
            button.setText("🔆")  # Bright sun symbol (more visible)
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #FF9800;
                    border-radius: 25px;
                    font-size: 24px;
                    padding: 5px;
                    color: #FF6F00;  /* Orange color for sun */
                }
                QPushButton:hover {
                    background-color: rgba(255, 152, 0, 0.1);
                    border: 2px solid #F57C00;
                }
                QPushButton:pressed {
                    background-color: rgba(255, 152, 0, 0.2);
                }
            """)
    
    def apply_theme(self, app, toggle_button=None):
        """Apply current theme to the application"""
        stylesheet = self.get_stylesheet()
        app.setStyleSheet(stylesheet)
        
        if toggle_button:
            self.update_button_icon(toggle_button)


# Bonus: Rich font helper
class FontManager:
    """Manage custom fonts for the application"""
    
    @staticmethod
    def get_header_font():
        """Get font for headers"""
        font = QFont("Segoe UI", 24, QFont.Bold)
        return font
    
    @staticmethod
    def get_subheader_font():
        """Get font for subheaders"""
        font = QFont("Segoe UI", 16, QFont.DemiBold)
        return font
    
    @staticmethod
    def get_body_font():
        """Get font for body text"""
        font = QFont("Segoe UI", 13)
        return font
    
    @staticmethod
    def get_monospace_font():
        """Get monospace font for numbers"""
        font = QFont("Consolas", 13)
        if not font.exactMatch():
            font = QFont("Courier New", 13)
        return font


# Emoji library for consistent use
class EmojiLib:
    """Centralized emoji library"""
    
    # Profile & User
    USER = "👤"
    PROFILE = "👥"
    AVATAR = "🎭"
    
    # Money & Trading
    MONEY = "💰"
    DOLLAR = "💵"
    CHART_UP = "📈"
    CHART_DOWN = "📉"
    CHART = "📊"
    TROPHY = "🏆"
    
    # Actions
    ADD = "➕"
    REMOVE = "➖"
    EDIT = "✏️"
    DELETE = "🗑️"
    SAVE = "💾"
    REFRESH = "🔄"
    SEARCH = "🔍"
    FILTER = "🔬"
    
    # Status
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    CHECKMARK = "✓"
    
    # Trading
    LONG = "🟢"
    SHORT = "🔴"
    TARGET = "🎯"
    STOP_LOSS = "🛑"
    ENTRY = "👉"
    LEVERAGE = "🌊"
    RISK = "⚠️"
    
    # Time
    CLOCK = "🕐"
    CALENDAR = "📅"
    TIMER = "⏱️"
    
    # Documents
    DOCUMENT = "📄"
    FOLDER = "📁"
    SCREENSHOT = "📸"
    NOTES = "📝"
    
    # Theme
    MOON = "🌙"
    SUN = "☀️"
    STAR = "⭐"