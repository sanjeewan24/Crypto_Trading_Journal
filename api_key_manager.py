"""
API Key Manager
Manages Gemini API keys per profile with testing functionality
"""

import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QListWidget, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import google.generativeai as genai


class APIKeyTester(QThread):
    """Background thread for testing API keys"""
    test_complete = pyqtSignal(bool, str)
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
    
    def run(self):
        try:
            genai.configure(api_key=self.api_key)
            # ✅ Updated to use gemini-flash-latest (stable with free tier support)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content("Test connection. Reply with 'OK'")
            
            if response.text:
                self.test_complete.emit(True, f"✅ API key is valid and working!\n\nModel: gemini-flash-latest\nResponse: {response.text[:50]}")
            else:
                self.test_complete.emit(False, "❌ Invalid response from API")
        except Exception as e:
            self.test_complete.emit(False, f"❌ API key test failed: {str(e)}")



class APIKeyManager:
    """Manages API keys storage and retrieval"""
    
    def __init__(self, config_file='api_keys.json'):
        self.config_file = config_file
        self.keys = self.load_keys()
    
    def load_keys(self):
        """Load API keys from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_keys(self):
        """Save API keys to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.keys, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving API keys: {e}")
            return False
    
    def set_api_key(self, profile_id, api_key):
        """Set API key for a profile"""
        self.keys[str(profile_id)] = api_key
        return self.save_keys()
    
    def get_api_key(self, profile_id):
        """Get API key for a profile"""
        return self.keys.get(str(profile_id))
    
    def remove_api_key(self, profile_id):
        """Remove API key for a profile"""
        if str(profile_id) in self.keys:
            del self.keys[str(profile_id)]
            return self.save_keys()
        return False


class APIKeyDialog(QDialog):
    """Dialog for managing API keys"""
    
    def __init__(self, profile_manager, current_profile_id, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.current_profile_id = current_profile_id
        self.api_manager = APIKeyManager()
        self.test_thread = None
        
        self.setWindowTitle("🔑 API Key Management")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🤖 Gemini API Key Configuration")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            color: #4CAF50;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Profile selector
        profile_frame = QFrame()
        profile_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 10px;
                background-color: rgba(76, 175, 80, 0.1);
            }
        """)
        profile_layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Select Profile:"))
        self.profile_list = QListWidget()
        self.profile_list.itemClicked.connect(self.load_profile_api_key)
        self.refresh_profile_list()
        profile_layout.addWidget(self.profile_list)
        
        profile_frame.setLayout(profile_layout)
        layout.addWidget(profile_frame)
        
        # API Key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("🔑 API Key:"))
        self.api_key_entry = QLineEdit()
        self.api_key_entry.setEchoMode(QLineEdit.Password)
        self.api_key_entry.setPlaceholderText("Enter your Gemini API key")
        key_layout.addWidget(self.api_key_entry)
        layout.addLayout(key_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Key")
        save_btn.clicked.connect(self.save_api_key)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        test_btn = QPushButton("🧪 Test Key")
        test_btn.clicked.connect(self.test_api_key)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        remove_btn = QPushButton("🗑️ Remove Key")
        remove_btn.clicked.connect(self.remove_api_key)
        remove_btn.setProperty("class", "danger")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(test_btn)
        button_layout.addWidget(remove_btn)
        layout.addLayout(button_layout)
        
        # Log output
        layout.addWidget(QLabel("📋 Log:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Info section
        info_label = QLabel("""
        <b>ℹ️ How to get your Gemini API key:</b><br>
        1. Visit <a href="https://aistudio.google.com/app/apikey">Google AI Studio</a><br>
        2. Click "Create API Key"<br>
        3. Copy the key and paste it here<br>
        <br>
        <b>✨ Free Tier includes:</b><br>
        • 15 requests per minute<br>
        • 250,000 tokens/minute<br>
        • Image analysis support
        """)
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            background-color: transparent;
            color: #e0e0e0;
            padding: 10px;
            border: 1px solid #4CAF50;
            border-radius: 5px;
        """)

        layout.addWidget(info_label)
        
        self.setLayout(layout)
        self.add_log("🔧 API Key Manager initialized")
    
    def refresh_profile_list(self):
        """Refresh the list of profiles"""
        self.profile_list.clear()
        for profile in self.profile_manager.get_all_profiles():
            has_key = "🔑" if self.api_manager.get_api_key(profile['id']) else "⚪"
            item_text = f"{has_key} {profile['username']} (ID: {profile['id']})"
            self.profile_list.addItem(item_text)
    
    def load_profile_api_key(self):
        """Load API key for selected profile"""
        if self.profile_list.currentRow() < 0:
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        api_key = self.api_manager.get_api_key(profile['id'])
        
        if api_key:
            self.api_key_entry.setText(api_key)
            self.add_log(f"✅ Loaded API key for {profile['username']}")
        else:
            self.api_key_entry.clear()
            self.add_log(f"ℹ️ No API key found for {profile['username']}")
    
    def save_api_key(self):
        """Save API key for selected profile"""
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "No Profile", "Please select a profile first")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        api_key = self.api_key_entry.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Empty Key", "Please enter an API key")
            return
        
        if self.api_manager.set_api_key(profile['id'], api_key):
            self.add_log(f"✅ API key saved for {profile['username']}")
            QMessageBox.information(self, "Success", "API key saved successfully!")
            self.refresh_profile_list()
        else:
            self.add_log(f"❌ Failed to save API key")
            QMessageBox.critical(self, "Error", "Failed to save API key")
    
    def test_api_key(self):
        """Test API key validity"""
        api_key = self.api_key_entry.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Empty Key", "Please enter an API key to test")
            return
        
        self.add_log("🧪 Testing API key...")
        
        self.test_thread = APIKeyTester(api_key)
        self.test_thread.test_complete.connect(self.handle_test_result)
        self.test_thread.start()
    
    def handle_test_result(self, success, message):
        """Handle API key test result"""
        self.add_log(message)
        if success:
            QMessageBox.information(self, "Test Successful", message)
        else:
            QMessageBox.warning(self, "Test Failed", message)
    
    def remove_api_key(self):
        """Remove API key for selected profile"""
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "No Profile", "Please select a profile first")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        
        confirm = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove API key for {profile['username']}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            if self.api_manager.remove_api_key(profile['id']):
                self.add_log(f"🗑️ API key removed for {profile['username']}")
                self.api_key_entry.clear()
                self.refresh_profile_list()
                QMessageBox.information(self, "Success", "API key removed")
            else:
                self.add_log(f"❌ Failed to remove API key")
    
    def add_log(self, message):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
