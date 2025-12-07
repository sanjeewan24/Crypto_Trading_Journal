# journal.py
import sys
import os
import shutil
import datetime
import threading
import webbrowser
import hashlib
from io import StringIO
import json

# Charting imports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QTextEdit, QPushButton, QFileDialog, QTabWidget, QListWidget, QMessageBox, 
    QInputDialog, QFrame, QDialog, QGroupBox, QFormLayout, QScrollArea  # ✅ Added
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# Data handling
import pandas as pd

from theme_manager import ThemeManager, FontManager, EmojiLib

# ✅ AI INTEGRATION IMPORTS
try:
    from ai_analyzer import AIChartAnalyzer
    AI_ANALYZER_AVAILABLE = True
except ImportError:
    AI_ANALYZER_AVAILABLE = False
    print("⚠️ ai_analyzer.py not found. AI features disabled.")

try:
    from api_key_manager import APIKeyDialog
    API_KEY_MANAGER_AVAILABLE = True
except ImportError:
    API_KEY_MANAGER_AVAILABLE = False
    print("⚠️ api_key_manager.py not found. API key management disabled.")

# Try to import Flask-related modules


# Try to import Flask-related modules
try:
    from flask import Flask, request, jsonify, render_template_string, Response
    FLASK_AVAILABLE = True
except Exception:
    FLASK_AVAILABLE = False
    
# Settings helpers to persist editable capital across UI and Flask servers
SETTINGS_FILE = 'settings.json'

# Try to import Flask-related modules
try:
    from flask import Flask, request, jsonify, render_template_string, Response
    FLASK_AVAILABLE = True
except Exception:
    FLASK_AVAILABLE = False
    
# Settings helpers to persist editable capital across UI and Flask servers
SETTINGS_FILE = 'settings.json'

# ==================== ICON HELPER FUNCTIONS ====================
def create_app_icon():
    """Create a custom app icon programmatically"""
    from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor, QFont
    from PyQt5.QtCore import Qt
    
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(76, 175, 80))  # Green background
    
    painter = QPainter(pixmap)
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Arial", 32, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "TJ")
    painter.end()
    
    return QIcon(pixmap)

def set_window_icon(window):
    """Set custom icon for any window/dialog"""
    from PyQt5.QtGui import QIcon
    try:
        window.setWindowIcon(QIcon('app_icon.ico'))
    except:
        try:
            window.setWindowIcon(create_app_icon())
        except:
            pass  # Use default if both fail

# ==================== END ICON HELPERS ====================

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {'initial_balance': 5000.0}

def save_settings(data):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print("Error saving settings:", e)

def get_initial_balance():
    return float(load_settings().get('initial_balance', 5000.0))

def set_initial_balance(value):
    s = load_settings()
    s['initial_balance'] = float(value)
    save_settings(s)

# -------------------- EMBEDDED MATRIX APP (from matrix.py) --------------------
# Runs on port 5001 when requested.
def run_matrix_server(port=5001, profile_id=None, profile_balance=None, initial_balance=None):
    if not FLASK_AVAILABLE:
        return False, "Flask not installed"

    # guard: avoid re-creating multiple apps with same name in multiple threads
    app = Flask(f"matrix_app_{port}")

    def load_data():
        # ALWAYS use profile-specific trades file
        profile_trades_file = f"profiles/profile_{profile_id}/trades.xlsx" if profile_id else 'trades.xlsx'
        
        try:
            if not os.path.exists(profile_trades_file):
                # Return empty dataframe with proper columns
                return pd.DataFrame(columns=['Time', 'Pair', 'PnL', 'Status', 'Outcome', 'Trade Size', 'PnL %'])
            
            df = pd.read_excel(profile_trades_file)
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
            df['PnL'] = pd.to_numeric(df.get('PnL', pd.Series(dtype=float)), errors='coerce').fillna(0)
            df['PnL %'] = pd.to_numeric(df.get('PnL %', pd.Series(dtype=float)), errors='coerce').fillna(0)
            return df
        except Exception as e:
            print(f"Error loading trades: {e}")
            # Return empty dataframe with proper columns
            return pd.DataFrame(columns=['Time', 'Pair', 'PnL', 'Status', 'Outcome', 'Trade Size', 'PnL %'])

    def calculate_metrics(df):
        # CRITICAL: Use current balance for display, initial balance for % calculations
        current_balance = profile_balance if profile_balance is not None else 5000.0
        start_balance = initial_balance if initial_balance is not None else current_balance
        
        total_shares = 100
        metrics = {}
        
        # Handle empty dataframe
        if df.empty:
            metrics['Acc. Return Net $'] = 0
            metrics['Acc. Return Gross $'] = 0
            metrics['Account Balance'] = current_balance
            metrics['Daily Return $'] = 0
            metrics['Return on Winners'] = 0
            metrics['Return on Losers'] = 0
            metrics['Return $ on Long'] = 0
            metrics['Return $ on Short'] = 0
            metrics['Biggest Profit $'] = 0
            metrics['Biggest Loss $'] = 0
            metrics['Profit/Loss Ratio'] = 0
            metrics['Profit Factor'] = 0
            metrics['Trade $ Expectancy'] = 0
            metrics['Win %'] = 0
            metrics['Loss %'] = 0
            metrics['BE %'] = 0
            metrics['Open %'] = 0
            metrics['Acc. Return %'] = 0
            metrics['Biggest % Profit'] = 0
            metrics['Biggest % Loser'] = 0
            metrics['Return per Share'] = 0
            metrics['Kelly Criterion'] = 0
            metrics['Avg Return'] = 0
            metrics['Avg Return $'] = 0
            metrics['Return/Size'] = 0
            metrics['Avg $ on Winners'] = 0
            metrics['Avg $ on Losers'] = 0
            metrics['Avg Daily P&L'] = 0
            metrics['Avg Return %'] = 0
            metrics['Avg % Return'] = 0
            metrics['Avg % on Shorts'] = 0
            metrics['Avg % on Long'] = 0
            metrics['Avg % on Winners'] = 0
            metrics['Avg % on Losers'] = 0
            metrics['Trades'] = len(df)
            metrics['Total Winner'] = 0
            metrics['Total Open Trades'] = 0
            metrics['Tot. Closed Trades'] = 0
            metrics['Total Losers'] = 0
            metrics['Total BE'] = 0
            metrics['Max Consec. Loss'] = 0
            metrics['Max Consec. Win'] = 0
            metrics['PnL Std Dev'] = 0
            metrics['PnL Std Dev (W)'] = 0
            metrics['PnL Std Dev (L)'] = 0
            metrics['SQN'] = 0
            return metrics
        
        # CRITICAL: Only use CLOSED trades for PnL calculations
        closed_df = df[df['Status'] == 'Closed'] if 'Status' in df.columns else df
        
        metrics['Acc. Return Net $'] = closed_df['PnL'].sum() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        metrics['Acc. Return Gross $'] = closed_df['PnL'].abs().sum() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        
        # CRITICAL: Use actual current balance from profile
        metrics['Account Balance'] = current_balance
        
        today = datetime.datetime.now().date()
        daily_return = closed_df[closed_df['Time'].dt.date == today]['PnL'].sum() if 'PnL' in closed_df.columns and 'Time' in closed_df.columns and not closed_df.empty else 0
        metrics['Daily Return $'] = round(daily_return, 2)
        
        metrics['Return on Winners'] = closed_df[closed_df.get('Outcome', '') == 'Win']['PnL'].sum() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        metrics['Return on Losers'] = closed_df[closed_df.get('Outcome', '') == 'Loss']['PnL'].sum() if 'PnL' in closed_df.columns and not closed_df.empty else 0

        if 'Position Type' in closed_df.columns and not closed_df.empty:
            metrics['Return $ on Long'] = closed_df[closed_df['Position Type'] == 'Long Position']['PnL'].sum()
            metrics['Return $ on Short'] = closed_df[closed_df['Position Type'] == 'Short Position']['PnL'].sum()
        else:
            metrics['Return $ on Long'] = 0
            metrics['Return $ on Short'] = 0

        metrics['Biggest Profit $'] = closed_df[closed_df.get('PnL', 0) > 0].get('PnL', pd.Series(dtype=float)).max() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        metrics['Biggest Loss $'] = closed_df[closed_df.get('PnL', 0) < 0].get('PnL', pd.Series(dtype=float)).min() if 'PnL' in closed_df.columns and not closed_df.empty else 0

        if metrics.get('Return on Losers', 0) != 0:
            metrics['Profit/Loss Ratio'] = abs(metrics['Return on Winners']) / abs(metrics['Return on Losers'])
            metrics['Profit Factor'] = metrics['Return on Winners'] / abs(metrics['Return on Losers'])
        else:
            metrics['Profit/Loss Ratio'] = 0
            metrics['Profit Factor'] = 0

        # CRITICAL: Use CLOSED trades only for expectancy
        metrics['Trade $ Expectancy'] = closed_df['PnL'].mean() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        
        # Win/Loss % uses ALL trades (correct)
        metrics['Win %'] = (df['Outcome'] == 'Win').mean() * 100 if 'Outcome' in df.columns else 0
        metrics['Loss %'] = (df['Outcome'] == 'Loss').mean() * 100 if 'Outcome' in df.columns else 0
        metrics['BE %'] = (df['Outcome'] == 'Break Even').mean() * 100 if 'Outcome' in df.columns else 0
        metrics['Open %'] = (df['Status'] == 'Running').mean() * 100 if 'Status' in df.columns else 0
        
        # CRITICAL: Use INITIAL balance for % return calculation
        metrics['Acc. Return %'] = (metrics['Acc. Return Net $'] / start_balance) * 100 if start_balance else 0
        
        metrics['Biggest % Profit'] = closed_df[closed_df.get('PnL %', 0) > 0].get('PnL %', pd.Series(dtype=float)).max() if 'PnL %' in closed_df.columns and not closed_df.empty else 0
        metrics['Biggest % Loser'] = closed_df[closed_df.get('PnL %', 0) < 0].get('PnL %', pd.Series(dtype=float)).min() if 'PnL %' in closed_df.columns and not closed_df.empty else 0
        metrics['Return per Share'] = metrics['Acc. Return Net $'] / total_shares if total_shares != 0 else 0

        if metrics.get('Profit/Loss Ratio', 0) != 0:
            metrics['Kelly Criterion'] = (metrics['Win %'] / 100 * (metrics['Profit/Loss Ratio'] + 1) - 1) / metrics['Profit/Loss Ratio']
        else:
            metrics['Kelly Criterion'] = 0

        # Use closed trades for averages
        metrics['Avg Return'] = closed_df.get('PnL %', pd.Series(dtype=float)).mean() if 'PnL %' in closed_df.columns and not closed_df.empty else 0
        metrics['Avg Return $'] = closed_df.get('PnL', pd.Series(dtype=float)).mean() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        metrics['Return/Size'] = metrics['Acc. Return Net $'] / closed_df['Trade Size'].sum() if 'Trade Size' in closed_df.columns and not closed_df.empty and closed_df['Trade Size'].sum() != 0 else 0
        metrics['Avg $ on Winners'] = closed_df[closed_df.get('Outcome', '') == 'Win'].get('PnL', pd.Series(dtype=float)).mean() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        metrics['Avg $ on Losers'] = closed_df[closed_df.get('Outcome', '') == 'Loss'].get('PnL', pd.Series(dtype=float)).mean() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        metrics['Avg Daily P&L'] = daily_return
        metrics['Avg Return %'] = closed_df.get('PnL %', pd.Series(dtype=float)).mean() if 'PnL %' in closed_df.columns and not closed_df.empty else 0
        metrics['Avg % Return'] = closed_df.get('PnL %', pd.Series(dtype=float)).mean() if 'PnL %' in closed_df.columns and not closed_df.empty else 0

        if 'Position Type' in closed_df.columns and not closed_df.empty:
            metrics['Avg % on Shorts'] = closed_df[closed_df['Position Type'] == 'Short Position'].get('PnL %', pd.Series(dtype=float)).mean()
            metrics['Avg % on Long'] = closed_df[closed_df['Position Type'] == 'Long Position'].get('PnL %', pd.Series(dtype=float)).mean()
        else:
            metrics['Avg % on Shorts'] = 0
            metrics['Avg % on Long'] = 0

        metrics['Avg % on Winners'] = closed_df[closed_df.get('Outcome', '') == 'Win'].get('PnL %', pd.Series(dtype=float)).mean() if 'PnL %' in closed_df.columns and not closed_df.empty else 0
        metrics['Avg % on Losers'] = closed_df[closed_df.get('Outcome', '') == 'Loss'].get('PnL %', pd.Series(dtype=float)).mean() if 'PnL %' in closed_df.columns and not closed_df.empty else 0
        
        # Trade counts use ALL trades
        metrics['Trades'] = len(df)
        metrics['Total Winner'] = (df.get('Outcome', '') == 'Win').sum()
        metrics['Total Open Trades'] = (df.get('Status', '') == 'Running').sum()
        metrics['Tot. Closed Trades'] = (df.get('Status', '') == 'Closed').sum()
        metrics['Total Losers'] = (df.get('Outcome', '') == 'Loss').sum()
        metrics['Total BE'] = (df.get('Outcome', '') == 'Break Even').sum()
        
        try:
            metrics['Max Consec. Loss'] = closed_df['PnL'].lt(0).astype(int).cumsum().mul(closed_df['PnL'].lt(0)).diff().fillna(0).cummax().max() if 'PnL' in closed_df.columns and not closed_df.empty else 0
            metrics['Max Consec. Win'] = closed_df['PnL'].gt(0).astype(int).cumsum().mul(closed_df['PnL'].gt(0)).diff().fillna(0).cummax().max() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        except Exception:
            metrics['Max Consec. Loss'] = 0
            metrics['Max Consec. Win'] = 0
            
        metrics['PnL Std Dev'] = closed_df.get('PnL', pd.Series(dtype=float)).std() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        metrics['PnL Std Dev (W)'] = closed_df[closed_df.get('Outcome', '') == 'Win'].get('PnL', pd.Series(dtype=float)).std() if 'PnL' in closed_df.columns and not closed_df.empty else 0
        metrics['PnL Std Dev (L)'] = closed_df[closed_df.get('Outcome', '') == 'Loss'].get('PnL', pd.Series(dtype=float)).std() if 'PnL' in closed_df.columns and not closed_df.empty else 0

        pnl_std = metrics['PnL Std Dev'] if metrics['PnL Std Dev'] else 0
        metrics['SQN'] = (metrics['Avg Return $'] / pnl_std * (metrics['Trades'] ** 0.5)) if pnl_std != 0 else 0

        return metrics

    @app.route('/', methods=['GET', 'POST'])
    def index():
        try:
            df = load_data()
        except Exception as e:
            return f"<h2>Could not load trades:</h2><pre>{e}</pre>"

        filter_option = request.form.get('filter') if request.method == 'POST' else 'all'
        from datetime import datetime, timedelta
        if filter_option == 'last_7_days':
            start_date = datetime.now() - timedelta(days=7)
            df = df[df['Time'] >= start_date]
        elif filter_option == 'last_30_days':
            start_date = datetime.now() - timedelta(days=30)
            df = df[df['Time'] >= start_date]

        metrics = calculate_metrics(df)
        
        # Simple HTML rendering
        html_template = '''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>📈 Trade Metrics</title>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');
            body { background-color: #121212; color: #ffffff; font-family: 'Open Sans', sans-serif; margin: 0; padding: 0; }
            .header { display: flex; justify-content: space-around; align-items: center; padding: 20px; background-color: #1f1f1f; }
            .container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; padding: 20px; }
            .card { background-color: #1f1f1f; border: 1px solid #333; border-radius: 8px; padding: 20px; width: 220px; text-align: center; }
            </style>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
          </head>
          <body>
            <div class="header">
              <div><h1>💸 Account Balance</h1><p>${{ "%.2f"|format(metrics['Account Balance']) }}</p></div>
              <div><h1>📊 Total Trades</h1><p>{{ metrics['Trades'] }}</p></div>
              <div><h1>🏆 Win Rate</h1><p>{{ "%.2f"|format(metrics['Win %']) }}%</p></div>
            </div>
            <div style="display:flex; justify-content:center; margin-top:10px;">
              <form method="post" style="display:flex; gap:10px;">
                <select name="filter">
                  <option value="all">All Time</option>
                  <option value="last_7_days">Last 7 Days</option>
                  <option value="last_30_days">Last 30 Days</option>
                </select>
                <button type="submit">Apply</button>
              </form>
            </div>
            <div class="container">
              {% for key, value in metrics.items() %}
                <div class="card">
                  <h3>{{ key }}</h3>
                  <p>{{ "%.2f"|format(value) if value is number else value }}</p>
                </div>
              {% endfor %}
            </div>
            <div style="width:90%; margin: auto; max-width:1200px;">
              <canvas id="pnlChart"></canvas>
            </div>
            <script>
              var ctx = document.getElementById('pnlChart').getContext('2d');
              var pnlData = {{ df['PnL'].fillna(0).tolist() | tojson | safe if not df.empty else '[]' }};
              var pnlChart = new Chart(ctx, {
                type: 'line',
                data: {
                  labels: Array.from({length: pnlData.length}, (_, i) => i + 1),
                  datasets: [{
                    label: 'PnL Over Time 📈',
                    data: pnlData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    fill: false,
                  }]
                }
              });
            </script>
          </body>
        </html>
        '''
        return render_template_string(html_template, metrics=metrics, df=df)

    @app.route('/save_report', methods=['POST'])
    def save_report():
        try:
            df = load_data()
        except Exception as e:
            return f"Error loading data: {e}"
        
        filter_option = request.form.get('filter')
        from datetime import datetime, timedelta
        if filter_option == 'last_7_days':
            start_date = datetime.now() - timedelta(days=7)
            df = df[df['Time'] >= start_date]
        elif filter_option == 'last_30_days':
            start_date = datetime.now() - timedelta(days=30)
            df = df[df['Time'] >= start_date]
        
        metrics = calculate_metrics(df)
        report = StringIO()
        report.write("📊 Trade Metrics Report 📊\n")
        report.write("="*50 + "\n")
        for key, value in metrics.items():
            report.write(f"{key}: {value}\n")
        report.seek(0)
        return Response(report.getvalue(), mimetype='text/plain', headers={'Content-Disposition': 'attachment; filename=report.txt'})

    def _serve():
        try:
            app.run(port=port, debug=False, use_reloader=False)
        except Exception as e:
            print("Matrix server error:", e)

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    return True, f"http://127.0.0.1:{port}/"
# ==================== ENHANCED PROFILE MANAGER ====================

class EnhancedProfileManager:
    def __init__(self, file_path="profiles.json"):
        self.file_path = file_path
        self.profiles = []
        self._load_profiles()
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_profiles(self):
        """Load profiles from JSON file"""
        if not os.path.exists(self.file_path):
            # Create default primary profile
            self.profiles = [{
                "id": 1,
                "username": "admin",
                "password": self._hash_password("admin"),
                "balance": 10000.0,
                "is_active": True,
                "created_at": datetime.datetime.now().isoformat(),
                "last_login": datetime.datetime.now().isoformat(),
                "avatar_path": "",
                "color": "#4CAF50",
                "balance_history": [
                    {
                        "date": datetime.datetime.now().isoformat(),
                        "balance": 10000.0,
                        "action": "Initial Balance"
                    }
                ]
            }]
            self._save_profiles()
        else:
            with open(self.file_path, "r") as file:
                self.profiles = json.load(file)
    
    def _save_profiles(self):
        """Save profiles to JSON file"""
        with open(self.file_path, "w") as file:
            json.dump(self.profiles, file, indent=4)
    
    def create_profile(self, username, password, balance, avatar_path="", color="#2196F3"):
        """Create a new profile"""
        # Check if username exists
        if any(p["username"] == username for p in self.profiles):
            return False, "Username already exists"
        
        new_id = max([p["id"] for p in self.profiles], default=0) + 1
        
        new_profile = {
            "id": new_id,
            "username": username,
            "password": self._hash_password(password),
            "balance": balance,
            "is_active": False,
            "created_at": datetime.datetime.now().isoformat(),
            "last_login": None,
            "avatar_path": avatar_path,
            "color": color,
            "balance_history": [
                {
                    "date": datetime.datetime.now().isoformat(),
                    "balance": balance,
                    "action": "Initial Balance"
                }
            ]
        }
        
        self.profiles.append(new_profile)
        self._save_profiles()
        
        # Create profile-specific folders
        self._create_profile_folders(new_id)
        
        return True, "Profile created successfully"
    
    def _create_profile_folders(self, profile_id):
        """Create folders for profile data"""
        base_path = f"profiles/profile_{profile_id}"
        os.makedirs(f"{base_path}/screenshots", exist_ok=True)
        os.makedirs(f"{base_path}/exports", exist_ok=True)
    
    def verify_password(self, profile_id, password):
        """Verify profile password"""
        profile = self.get_profile_by_id(profile_id)
        if profile:
            return profile["password"] == self._hash_password(password)
        return False
    
    def switch_profile(self, profile_id, password):
        """Switch to a profile with password verification"""
        if not self.verify_password(profile_id, password):
            return False, "Incorrect password"
        
        # Deactivate all profiles
        for profile in self.profiles:
            profile["is_active"] = False
        
        # Activate selected profile
        profile = self.get_profile_by_id(profile_id)
        if profile:
            profile["is_active"] = True
            profile["last_login"] = datetime.datetime.now().isoformat()
            self._save_profiles()
            return True, "Profile switched successfully"
        
        return False, "Profile not found"
    
    def delete_profile(self, profile_id, password):
        """Delete a profile with password verification"""
        if not self.verify_password(profile_id, password):
            return False, "Incorrect password"
        
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return False, "Profile not found"
        
        # Don't allow deleting the last profile
        if len(self.profiles) == 1:
            return False, "Cannot delete the last profile"
        
        # If deleting active profile, activate another one
        was_active = profile["is_active"]
        
        # Remove profile
        self.profiles = [p for p in self.profiles if p["id"] != profile_id]
        
        # Activate first profile if deleted profile was active
        if was_active and self.profiles:
            self.profiles[0]["is_active"] = True
        
        self._save_profiles()
        
        # Delete profile folders
        profile_path = f"profiles/profile_{profile_id}"
        if os.path.exists(profile_path):
            shutil.rmtree(profile_path)
        
        return True, "Profile deleted successfully"
    
    def change_password(self, profile_id, old_password, new_password):
        """Change profile password"""
        if not self.verify_password(profile_id, old_password):
            return False, "Incorrect current password"
        
        profile = self.get_profile_by_id(profile_id)
        if profile:
            profile["password"] = self._hash_password(new_password)
            self._save_profiles()
            return True, "Password changed successfully"
        
        return False, "Profile not found"
    
    def update_balance(self, profile_id, new_balance, action="Manual Update"):
        """Update profile balance and log in history"""
        profile = self.get_profile_by_id(profile_id)
        if profile:
            profile["balance"] = new_balance
            profile["balance_history"].append({
                "date": datetime.datetime.now().isoformat(),
                "balance": new_balance,
                "action": action
            })
            self._save_profiles()
            return True
        return False
    
    def get_profile_by_id(self, profile_id):
        """Get profile by ID"""
        for profile in self.profiles:
            if profile["id"] == profile_id:
                return profile
        return None
    
    def get_active_profile(self):
        """Get currently active profile"""
        for profile in self.profiles:
            if profile.get("is_active", False):
                return profile
        # If no active profile, activate first one
        if self.profiles:
            self.profiles[0]["is_active"] = True
            self._save_profiles()
            return self.profiles[0]
        return None
    
    def get_all_profiles(self):
        """Get all profiles"""
        return self.profiles
    
    def clone_profile(self, source_id, new_username, password):
        """Clone an existing profile"""
        source = self.get_profile_by_id(source_id)
        if not source:
            return False, "Source profile not found"
        
        return self.create_profile(
            username=new_username,
            password=password,
            balance=source["balance"],
            avatar_path="",
            color=source["color"]
        )
    
    def export_profile(self, profile_id, export_path):
        """Export profile data to JSON"""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return False, "Profile not found"
        
        export_data = {
            "profile": profile,
            "trades_file": f"profiles/profile_{profile_id}/trades.xlsx",
            "export_date": datetime.datetime.now().isoformat()
        }
        
        try:
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=4)
            return True, "Profile exported successfully"
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def get_profile_stats(self, profile_id):
        """Get profile statistics"""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return None
        
        created = datetime.datetime.fromisoformat(profile["created_at"])
        last_login = profile.get("last_login")
        if last_login:
            last_login = datetime.datetime.fromisoformat(last_login)
        
        return {
            "username": profile["username"],
            "created_at": created.strftime("%Y-%m-%d %H:%M"),
            "last_login": last_login.strftime("%Y-%m-%d %H:%M") if last_login else "Never",
            "current_balance": profile["balance"],
            "initial_balance": profile["balance_history"][0]["balance"] if profile["balance_history"] else 0,
            "balance_changes": len(profile["balance_history"]),
            "days_active": (datetime.datetime.now() - created).days
        }

# ==================== PROFILE SELECTOR DIALOG (STARTUP) ====================

class ProfileSelectorDialog(QDialog):
    def __init__(self, profile_manager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.selected_profile = None
        self.setWindowTitle("Select Profile")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Set custom window icon ✅
        from PyQt5.QtGui import QIcon
        try:
            self.setWindowIcon(QIcon('app_icon.ico'))
        except:
            # Fallback to programmatic icon
            try:
                self.setWindowIcon(create_app_icon())
            except:
                pass  # Use default if both fail
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔐 Select Your Profile")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.setStyleSheet("""
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        
        for profile in self.profile_manager.get_all_profiles():
            item_text = f"👤 {profile['username']} | 💰 ${profile['balance']:.2f}"
            if profile.get("is_active"):
                item_text += " ⭐ (Last Active)"
            self.profile_list.addItem(item_text)
        
        layout.addWidget(self.profile_list)
        
        # Password input
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.returnPressed.connect(self.login)
        password_layout.addWidget(self.password_entry)
        layout.addLayout(password_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("🔓 Login")
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        button_layout.addWidget(login_btn)
        
        create_btn = QPushButton("➕ Create New Profile")
        create_btn.clicked.connect(self.create_profile)
        button_layout.addWidget(create_btn)
        
        manage_btn = QPushButton("⚙️ Manage Profiles")
        manage_btn.clicked.connect(self.manage_profiles)
        button_layout.addWidget(manage_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Auto-select last active profile
        for i, profile in enumerate(self.profile_manager.get_all_profiles()):
            if profile.get("is_active"):
                self.profile_list.setCurrentRow(i)
                break
    
    def login(self):
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile")
            return
        
        password = self.password_entry.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter password")
            return
        
        profile_index = self.profile_list.currentRow()
        profile = self.profile_manager.get_all_profiles()[profile_index]
        
        success, message = self.profile_manager.switch_profile(profile["id"], password)
        
        if success:
            self.selected_profile = profile
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", message)
            self.password_entry.clear()
    
    def create_profile(self):
        dialog = CreateProfileDialog(self.profile_manager, self)
        if dialog.exec_():
            self.refresh_list()
    
    def manage_profiles(self):
        dialog = EnhancedProfileDialog(self.profile_manager, self)
        dialog.exec_()
        self.refresh_list()
    
    def refresh_list(self):
        self.profile_list.clear()
        for profile in self.profile_manager.get_all_profiles():
            item_text = f"👤 {profile['username']} | 💰 ${profile['balance']:.2f}"
            if profile.get("is_active"):
                item_text += " ⭐"
            self.profile_list.addItem(item_text)


# ==================== CREATE PROFILE DIALOG ====================

class CreateProfileDialog(QDialog):
    def __init__(self, profile_manager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.setWindowTitle("Create New Profile")
        self.setMinimumWidth(400)
        
        # Set custom window icon ✅
        from PyQt5.QtGui import QIcon
        try:
            self.setWindowIcon(QIcon('app_icon.ico'))
        except:
            try:
                self.setWindowIcon(create_app_icon())
            except:
                pass
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.username_entry = QLineEdit()
        form.addRow("Username:", self.username_entry)
        
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self.password_entry)
        
        self.confirm_password_entry = QLineEdit()
        self.confirm_password_entry.setEchoMode(QLineEdit.Password)
        form.addRow("Confirm Password:", self.confirm_password_entry)
        
        self.balance_entry = QLineEdit()
        self.balance_entry.setText("10000.00")
        form.addRow("Initial Balance:", self.balance_entry)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Profile")
        create_btn.clicked.connect(self.create_profile)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_profile(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text()
        confirm_password = self.confirm_password_entry.text()
        balance_text = self.balance_entry.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        try:
            balance = float(balance_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid balance amount")
            return
        
        success, message = self.profile_manager.create_profile(username, password, balance)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)


# ==================== ENHANCED PROFILE MANAGEMENT DIALOG ====================

class EnhancedProfileDialog(QDialog):
    def __init__(self, profile_manager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.setWindowTitle("Profile Management")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        # Set custom window icon ✅
        from PyQt5.QtGui import QIcon
        try:
            self.setWindowIcon(QIcon('app_icon.ico'))
        except:
            try:
                self.setWindowIcon(create_app_icon())
            except:
                pass
        
        self.initUI()
    
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left side: Profile list
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("📋 All Profiles:"))
        
        self.profile_list = QListWidget()
        self.profile_list.itemClicked.connect(self.load_profile_details)
        self.refresh_profile_list()
        left_layout.addWidget(self.profile_list)
        
        # Action buttons
        action_layout = QVBoxLayout()
        
        switch_btn = QPushButton("🔄 Switch Profile")
        switch_btn.clicked.connect(self.switch_profile)
        action_layout.addWidget(switch_btn)
        
        delete_btn = QPushButton("🗑️ Delete Profile")
        delete_btn.clicked.connect(self.delete_profile)
        action_layout.addWidget(delete_btn)
        
        change_pwd_btn = QPushButton("🔑 Change Password")
        change_pwd_btn.clicked.connect(self.change_password)
        action_layout.addWidget(change_pwd_btn)
        
        clone_btn = QPushButton("📋 Clone Profile")
        clone_btn.clicked.connect(self.clone_profile)
        action_layout.addWidget(clone_btn)
        
                # Enhanced Export Button
        export_btn = QPushButton("📤 Export Profile")
        export_btn.clicked.connect(self.enhanced_export_profile)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        action_layout.addWidget(export_btn)
        
        # Import Profile Button
        import_btn = QPushButton("📥 Import Profile")
        import_btn.clicked.connect(self.import_profile)
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        action_layout.addWidget(import_btn)

        
        left_layout.addLayout(action_layout)
        
        # Right side: Profile details
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("📊 Profile Details:"))
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)
        
        # Balance management
        balance_group = QGroupBox("💰 Balance Management")
        balance_layout = QVBoxLayout()
        
        deposit_layout = QHBoxLayout()
        deposit_layout.addWidget(QLabel("Amount:"))
        self.amount_entry = QLineEdit()
        deposit_layout.addWidget(self.amount_entry)
        balance_layout.addLayout(deposit_layout)
        
        balance_btn_layout = QHBoxLayout()
        deposit_btn = QPushButton("➕ Deposit")
        deposit_btn.clicked.connect(lambda: self.adjust_balance("deposit"))
        balance_btn_layout.addWidget(deposit_btn)
        
        withdraw_btn = QPushButton("➖ Withdraw")
        withdraw_btn.clicked.connect(lambda: self.adjust_balance("withdraw"))
        balance_btn_layout.addWidget(withdraw_btn)
        
        reset_btn = QPushButton("🔄 Reset to Initial")
        reset_btn.clicked.connect(self.reset_balance)
        balance_btn_layout.addWidget(reset_btn)
        
        balance_layout.addLayout(balance_btn_layout)
        balance_group.setLayout(balance_layout)
        right_layout.addWidget(balance_group)
        
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        self.setLayout(main_layout)

    def enhanced_export_profile(self):
        """Export profile with all data (JSON + screenshots + trades + exports)"""
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile to export")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        
        # Choose destination folder
        export_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Export Destination Folder",
            os.path.expanduser("~/Desktop"),
            QFileDialog.ShowDirsOnly
        )
        
        if not export_folder:
            return
        
        try:
            # Create export folder structure
            profile_export_name = f"{profile['username']}_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            full_export_path = os.path.join(export_folder, profile_export_name)
            os.makedirs(full_export_path, exist_ok=True)
            
            # 1. Export profile JSON
            export_data = {
                'profile': profile,
                'export_date': datetime.datetime.now().isoformat(),
                'version': '2.0.0'
            }
            
            json_path = os.path.join(full_export_path, f"{profile['username']}_profile.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            
            # 2. Copy entire profile folder (screenshots, trades, exports)
            source_profile_path = f"profiles/profile_{profile['id']}"
            if os.path.exists(source_profile_path):
                dest_profile_path = os.path.join(full_export_path, "profile_data")
                shutil.copytree(source_profile_path, dest_profile_path, dirs_exist_ok=True)
            
            # Count files for report
            screenshot_count = 0
            if os.path.exists(source_profile_path):
                screenshots_path = os.path.join(source_profile_path, 'screenshots')
                if os.path.exists(screenshots_path):
                    screenshot_count = len([f for f in os.listdir(screenshots_path) if f.endswith('.png')])
            
            # 3. Create README file (with UTF-8 encoding)
            readme_path = os.path.join(full_export_path, "README.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"""Trading Journal Profile Export
================================

Profile: {profile['username']}
Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: 2.0.0

CONTENTS:
---------
> {profile['username']}_profile.json  - Profile data and settings
> profile_data/                       - Complete profile folder
  * trades.xlsx                       - Trading history
  * screenshots/                      - Chart screenshots
  * exports/                          - Previous exports

IMPORT INSTRUCTIONS:
--------------------
1. Open Trading Journal v2.0.0
2. Go to Profile Management (gear icon)
3. Click "Import Profile" button
4. Select the {profile['username']}_profile.json file
5. All data will be restored automatically

STATS:
------
Current Balance: ${profile['balance']:.2f}
Total Transactions: {len(profile.get('balance_history', []))}
Profile Created: {datetime.datetime.fromisoformat(profile['created_at']).strftime('%Y-%m-%d')}
Screenshots: {screenshot_count} files

NOTES:
------
- Keep this folder safe as a backup
- The profile_data folder contains all your trading data
- You can import this profile on any computer with Trading Journal v2.0.0
""")
            
            # Success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Profile '{profile['username']}' exported successfully!\n\n"
                f"Location: {full_export_path}\n\n"
                f"Contents:\n"
                f"- Profile JSON\n"
                f"- Trading history (trades.xlsx)\n"
                f"- Screenshots ({screenshot_count} files)\n"
                f"- README instructions"
            )
            
            # Ask to open folder
            response = QMessageBox.question(
                self,
                "Open Export Folder?",
                "Would you like to open the export folder?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                import platform
                if platform.system() == 'Windows':
                    os.startfile(full_export_path)
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{full_export_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{full_export_path}"')
                    
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export profile:\n\n{str(e)}\n\n"
                f"Technical details:\n{traceback.format_exc()[:300]}"
            )

    def import_profile(self):
        """Import profile from exported backup"""
        # Select JSON file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Profile JSON to Import",
            os.path.expanduser("~/Desktop"),
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        new_profile_path = None  # Track for rollback
        
        try:
            # Load JSON
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            profile_data = import_data.get('profile')
            if not profile_data:
                raise ValueError("Invalid profile export file - missing profile data")
            
            # Check if username already exists
            username_exists = False
            for existing in self.profile_manager.get_all_profiles():
                if existing['username'].lower() == profile_data['username'].lower():
                    username_exists = True
                    break
            
            if username_exists:
                response = QMessageBox.question(
                    self,
                    "Profile Already Exists",
                    f"A profile named '{profile_data['username']}' already exists.\n\n"
                    "Do you want to rename the imported profile?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if response == QMessageBox.No:
                    return
                else:
                    # Rename
                    new_name, ok = QInputDialog.getText(
                        self,
                        "Rename Profile",
                        "Enter new username for imported profile:",
                        text=f"{profile_data['username']}_imported"
                    )
                    if ok and new_name:
                        profile_data['username'] = new_name
                    else:
                        return
            
            # Ask for new password
            new_password, ok = QInputDialog.getText(
                self,
                "Set Password",
                f"Set password for imported profile '{profile_data['username']}':",
                QLineEdit.Password
            )
            
            if not ok or not new_password:
                QMessageBox.warning(self, "Cancelled", "Import cancelled - password required")
                return
            
            # Hash new password
            import hashlib
            profile_data['password'] = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Assign new ID
            new_id = max([p['id'] for p in self.profile_manager.profiles], default=0) + 1
            old_id = profile_data.get('id', 0)
            profile_data['id'] = new_id
            profile_data['is_active'] = False
            profile_data['last_login'] = datetime.datetime.now().isoformat()
            
            # ✅ Create profile folder FIRST (before saving to JSON)
            new_profile_path = f"profiles/profile_{new_id}"
            os.makedirs(new_profile_path, exist_ok=True)
            os.makedirs(f"{new_profile_path}/screenshots", exist_ok=True)
            os.makedirs(f"{new_profile_path}/exports", exist_ok=True)
            
            # ✅ Find and copy files BEFORE adding to profiles list
            import_folder = os.path.dirname(file_path)
            profile_source_folder = None
            
            # Check multiple possible locations
            possible_locations = [
                os.path.join(import_folder, "profile_data"),
                os.path.join(import_folder, f"profile_{old_id}"),
                os.path.join(import_folder, "profile_2"),
                import_folder  # Files might be in same folder as JSON
            ]
            
            for location in possible_locations:
                if os.path.exists(os.path.join(location, "trades.xlsx")):
                    profile_source_folder = location
                    break
            
            if not profile_source_folder:
                raise ValueError(
                    "Could not find trades.xlsx file.\n\n"
                    f"Expected in:\n• {import_folder}/profile_2/\n"
                    f"• {import_folder}/profile_data/\n"
                    f"• {import_folder}/"
                )
            
            files_imported = []
            
            # Copy trades.xlsx
            trades_source = os.path.join(profile_source_folder, "trades.xlsx")
            if os.path.exists(trades_source):
                shutil.copy(trades_source, os.path.join(new_profile_path, "trades.xlsx"))
                files_imported.append("✓ trades.xlsx")
            else:
                files_imported.append("⚠ trades.xlsx (not found)")
            
            # Copy screenshots
            screenshots_source = os.path.join(profile_source_folder, "screenshots")
            screenshot_count = 0
            if os.path.exists(screenshots_source):
                screenshot_files = [f for f in os.listdir(screenshots_source) if f.endswith('.png')]
                for file in screenshot_files:
                    try:
                        shutil.copy(
                            os.path.join(screenshots_source, file),
                            os.path.join(new_profile_path, "screenshots", file)
                        )
                        screenshot_count += 1
                    except Exception as e:
                        print(f"Failed to copy {file}: {e}")
                files_imported.append(f"✓ {screenshot_count} screenshots")
            else:
                files_imported.append("⚠ screenshots folder not found")
            
            # Copy exports folder
            exports_source = os.path.join(profile_source_folder, "exports")
            if os.path.exists(exports_source):
                try:
                    export_files = os.listdir(exports_source)
                    for item in export_files:
                        src = os.path.join(exports_source, item)
                        dst = os.path.join(new_profile_path, "exports", item)
                        if os.path.isfile(src):
                            shutil.copy(src, dst)
                    files_imported.append(f"✓ exports folder ({len(export_files)} files)")
                except:
                    files_imported.append("⚠ exports folder (copy failed)")
            
            # ✅ NOW save profile to JSON (after files are copied)
            self.profile_manager.profiles.append(profile_data)
            
            # Save profiles.json manually
            profiles_json_path = 'profiles.json'
            with open(profiles_json_path, 'w') as f:
                json.dump(self.profile_manager.profiles, f, indent=4)
            
            # Success message
            QMessageBox.information(
                self,
                "✅ Import Successful",
                f"Profile '{profile_data['username']}' imported successfully!\n\n"
                f"📊 Balance: ${profile_data['balance']:.2f}\n"
                f"📅 Created: {datetime.datetime.fromisoformat(profile_data['created_at']).strftime('%Y-%m-%d')}\n"
                f"📈 Transactions: {len(profile_data.get('balance_history', []))}\n\n"
                f"Files Imported:\n" + "\n".join(files_imported) +
                f"\n\n💡 Login with your new password to access the profile!"
            )
            
            self.refresh_profile_list()
            
        except json.JSONDecodeError:
            # Rollback: delete profile folder if created
            if new_profile_path and os.path.exists(new_profile_path):
                shutil.rmtree(new_profile_path)
            
            QMessageBox.critical(
                self,
                "Invalid File",
                "The selected file is not a valid JSON profile export."
            )
            
        except Exception as e:
            # Rollback: delete profile folder if created
            if new_profile_path and os.path.exists(new_profile_path):
                shutil.rmtree(new_profile_path)
            
            import traceback
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import profile:\n\n{str(e)}\n\n"
                f"Ensure the profile_2 folder (with trades.xlsx) is in the same directory as the JSON file."
            )

    
    def refresh_profile_list(self):
        self.profile_list.clear()
        for profile in self.profile_manager.get_all_profiles():
            item_text = f"{'⭐' if profile.get('is_active') else '👤'} {profile['username']} (${profile['balance']:.2f})"
            self.profile_list.addItem(item_text)
    
    def load_profile_details(self):
        if self.profile_list.currentRow() < 0:
            return
        
        profile_index = self.profile_list.currentRow()
        profile = self.profile_manager.get_all_profiles()[profile_index]
        stats = self.profile_manager.get_profile_stats(profile["id"])
        
        details = f"""
<h2>👤 {stats['username']}</h2>
<hr>
<p><b>Created:</b> {stats['created_at']}</p>
<p><b>Last Login:</b> {stats['last_login']}</p>
<p><b>Days Active:</b> {stats['days_active']} days</p>
<p><b>Current Balance:</b> ${stats['current_balance']:.2f}</p>
<p><b>Initial Balance:</b> ${stats['initial_balance']:.2f}</p>
<p><b>Balance Changes:</b> {stats['balance_changes']} times</p>
<p><b>Status:</b> {'🟢 Active' if profile.get('is_active') else '⚪ Inactive'}</p>
<hr>
<h3>📈 Balance History (Last 5):</h3>
        """
        
        for entry in profile.get("balance_history", [])[-5:]:
            date = datetime.datetime.fromisoformat(entry["date"]).strftime("%Y-%m-%d %H:%M")
            details += f"<p>• {date}: ${entry['balance']:.2f} ({entry['action']})</p>"
        
        self.details_text.setHtml(details)
    
    def switch_profile(self):
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        
        password, ok = QInputDialog.getText(self, "Enter Password", 
                                            f"Enter password for {profile['username']}:", 
                                            QLineEdit.Password)
        if not ok or not password:
            return
        
        success, message = self.profile_manager.switch_profile(profile["id"], password)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.refresh_profile_list()
            self.load_profile_details()
            self.accept()  # Close dialog and refresh main app
        else:
            QMessageBox.warning(self, "Error", message)
    
    def delete_profile(self):
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete profile '{profile['username']}'?\n\n"
                                       "This will permanently delete all trades, screenshots, and data!",
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm != QMessageBox.Yes:
            return
        
        password, ok = QInputDialog.getText(self, "Enter Password", 
                                            f"Enter password for {profile['username']}:", 
                                            QLineEdit.Password)
        if not ok or not password:
            return
        
        success, message = self.profile_manager.delete_profile(profile["id"], password)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.refresh_profile_list()
            self.details_text.clear()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def change_password(self):
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        
        old_password, ok = QInputDialog.getText(self, "Current Password", 
                                                "Enter current password:", 
                                                QLineEdit.Password)
        if not ok or not old_password:
            return
        
        new_password, ok = QInputDialog.getText(self, "New Password", 
                                                "Enter new password:", 
                                                QLineEdit.Password)
        if not ok or not new_password:
            return
        
        confirm_password, ok = QInputDialog.getText(self, "Confirm Password", 
                                                    "Confirm new password:", 
                                                    QLineEdit.Password)
        if not ok or new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        success, message = self.profile_manager.change_password(profile["id"], old_password, new_password)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)
    
    def clone_profile(self):
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile to clone")
            return
        
        source_profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        
        new_username, ok = QInputDialog.getText(self, "Clone Profile", 
                                                "Enter username for cloned profile:")
        if not ok or not new_username:
            return
        
        new_password, ok = QInputDialog.getText(self, "New Password", 
                                                "Enter password for cloned profile:", 
                                                QLineEdit.Password)
        if not ok or not new_password:
            return
        
        success, message = self.profile_manager.clone_profile(source_profile["id"], new_username, new_password)
        
        if success:
            QMessageBox.information(self, "Success", f"Profile cloned as '{new_username}'")
            self.refresh_profile_list()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def export_profile(self):
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile to export")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Profile", 
                                                    f"{profile['username']}_export.json",
                                                    "JSON Files (*.json)")
        if not file_path:
            return
        
        success, message = self.profile_manager.export_profile(profile["id"], file_path)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)
    
    def adjust_balance(self, action):
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile")
            return
        
        try:
            amount = float(self.amount_entry.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid amount")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        
        if action == "deposit":
            new_balance = profile["balance"] + amount
            action_text = f"Deposit +${amount:.2f}"
        else:
            new_balance = profile["balance"] - amount
            action_text = f"Withdrawal -${amount:.2f}"
        
        self.profile_manager.update_balance(profile["id"], new_balance, action_text)
        
        QMessageBox.information(self, "Success", f"Balance updated to ${new_balance:.2f}")
        self.refresh_profile_list()
        self.load_profile_details()
        self.amount_entry.clear()
    
    def reset_balance(self):
        if self.profile_list.currentRow() < 0:
            QMessageBox.warning(self, "Error", "Please select a profile")
            return
        
        profile = self.profile_manager.get_all_profiles()[self.profile_list.currentRow()]
        initial_balance = profile["balance_history"][0]["balance"] if profile["balance_history"] else 0
        
        confirm = QMessageBox.question(self, "Confirm Reset",
                                       f"Reset balance to initial amount of ${initial_balance:.2f}?",
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            self.profile_manager.update_balance(profile["id"], initial_balance, "Balance Reset")
            QMessageBox.information(self, "Success", "Balance reset to initial amount")
            self.refresh_profile_list()
            self.load_profile_details()

# -------------------- ORIGINAL GUI APP (your full functionality preserved) --------------------
# I reused your previously-fixed long version (with the mapping from self.* attributes to self.journal_tab.*),
# keeping all functionality (Excel saving, screenshots, filters, etc.) intact.
class CryptoTradeAlert(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        # Left section: Input fields and buttons
        left_layout = QVBoxLayout()

        # Add dropdown for calculator selection
        self.current_calculator = "Leverage Calculator"
        self.calculator_selector = QComboBox()
        self.calculator_selector.addItems(["Leverage Calculator", "Margin Calculator"])
        self.calculator_selector.currentTextChanged.connect(self.switch_calculator)
        left_layout.addWidget(self.calculator_selector)

        # Input fields - HORIZONTAL LAYOUT
        coin_layout = QHBoxLayout()
        self.coin_entry = QLineEdit(self)
        self.coin_entry.setPlaceholderText("e.g., BTC/USDT")
        self.coin_entry.textChanged.connect(self.convert_coin_to_uppercase)
        coin_layout.addWidget(QLabel('Coin:'))
        coin_layout.addWidget(self.coin_entry)
        left_layout.addLayout(coin_layout)

        position_layout = QHBoxLayout()
        self.position_dropdown = QComboBox(self)
        self.position_dropdown.addItems(['LONG', 'SHORT'])
        position_layout.addWidget(QLabel('Position Type:'))
        position_layout.addWidget(self.position_dropdown)
        left_layout.addLayout(position_layout)

        trade_type_layout = QHBoxLayout()
        self.trade_type_dropdown = QComboBox(self)
        self.trade_type_dropdown.addItems(['IDEA', 'SIGNAL', 'STRATEGY'])
        trade_type_layout.addWidget(QLabel('Trade Type:'))
        trade_type_layout.addWidget(self.trade_type_dropdown)
        left_layout.addLayout(trade_type_layout)

        entry_price_layout = QHBoxLayout()
        self.entry_price_entry = QLineEdit(self)
        self.entry_price_entry.setPlaceholderText("Entry Price")
        entry_price_layout.addWidget(QLabel('Entry Price:'))
        entry_price_layout.addWidget(self.entry_price_entry)
        left_layout.addLayout(entry_price_layout)

        stop_loss_layout = QHBoxLayout()
        self.stop_loss_entry = QLineEdit(self)
        self.stop_loss_entry.setPlaceholderText("Stop Loss Price")
        stop_loss_layout.addWidget(QLabel('Stop Loss Price:'))
        stop_loss_layout.addWidget(self.stop_loss_entry)
        left_layout.addLayout(stop_loss_layout)

        take_profit_layout = QHBoxLayout()
        self.take_profit_entry = QLineEdit(self)
        self.take_profit_entry.setPlaceholderText("Take Profit Price")
        take_profit_layout.addWidget(QLabel('Take Profit Price:'))
        take_profit_layout.addWidget(self.take_profit_entry)
        left_layout.addLayout(take_profit_layout)

        # Margin/Leverage input field - HORIZONTAL
        margin_layout = QHBoxLayout()
        self.margin_label = QLabel('Margin:')
        self.margin_entry = QLineEdit(self)
        self.margin_entry.setPlaceholderText("Margin")
        margin_layout.addWidget(self.margin_label)
        margin_layout.addWidget(self.margin_entry)
        left_layout.addLayout(margin_layout)

        risk_layout = QHBoxLayout()
        self.risk_amount_entry = QLineEdit(self)
        self.risk_amount_entry.setPlaceholderText("Risk Amount")
        risk_layout.addWidget(QLabel('Risk Amount:'))
        risk_layout.addWidget(self.risk_amount_entry)
        left_layout.addLayout(risk_layout)

        # Buttons: Calculate, Add Record
        button_layout = QHBoxLayout()
        calculate_btn = QPushButton('Calculate', self)
        calculate_btn.clicked.connect(self.calculate)
        button_layout.addWidget(calculate_btn)

        add_record_btn = QPushButton('Add Record', self)
        add_record_btn.clicked.connect(self.add_record)
        button_layout.addWidget(add_record_btn)

        left_layout.addLayout(button_layout)

        # Right section: Output and buttons
        right_layout = QVBoxLayout()
        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)
        right_layout.addWidget(QLabel('Output:'))
        right_layout.addWidget(self.output_text)

        # Horizontal layout for Copy Output and Clear buttons
        output_button_layout = QHBoxLayout()
        copy_btn = QPushButton('Copy Output', self)
        copy_btn.clicked.connect(self.copy_output)
        output_button_layout.addWidget(copy_btn)

        clear_btn = QPushButton('Clear', self)
        clear_btn.clicked.connect(self.clear_all)
        output_button_layout.addWidget(clear_btn)

        right_layout.addLayout(output_button_layout)

        # Add left and right layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def switch_calculator(self, calculator_type):
        self.current_calculator = calculator_type
        if calculator_type == "Leverage Calculator":
            self.margin_label.setText("Margin:")
            self.margin_entry.setPlaceholderText("Margin")
        elif calculator_type == "Margin Calculator":
            self.margin_label.setText("Leverage:")
            self.margin_entry.setPlaceholderText("Leverage")

    def calculate(self):
        if self.current_calculator == "Margin Calculator":
            self.calculate_margin()
        else:
            self.calculate_leverage()

    def calculate_leverage(self):
        try:
            coin = self.coin_entry.text()
            position = self.position_dropdown.currentText()
            trade_type = self.trade_type_dropdown.currentText()
            entry_price = self._to_float_or_raise(self.entry_price_entry.text(), "entry price")
            stop_loss_price = self._to_float_or_raise(self.stop_loss_entry.text(), "stop loss")
            take_profit_price = self._to_float_or_raise(self.take_profit_entry.text(), "take profit")
            margin = self._to_float_or_raise(self.margin_entry.text(), "margin")
            risk_amount = self._to_float_or_raise(self.risk_amount_entry.text(), "risk amount")

            if position == 'LONG':
                sl_movement_pct = ((entry_price - stop_loss_price) / entry_price) * 100
                tp_movement_pct = ((take_profit_price - entry_price) / entry_price) * 100
            else:
                sl_movement_pct = ((stop_loss_price - entry_price) / entry_price) * 100
                tp_movement_pct = ((entry_price - take_profit_price) / entry_price) * 100

            if sl_movement_pct == 0:
                leverage = 0.0
            else:
                leverage = (risk_amount / margin) / (sl_movement_pct / 100)

            position_emoji = "🟢" if position == 'LONG' else "🔴"
            # ✅ UPDATED: Added emoji for STRATEGY
            if trade_type == 'SIGNAL':
                trade_type_emoji = "✅"
            elif trade_type == 'STRATEGY':
                trade_type_emoji = "🎯"
            else:
                trade_type_emoji = "💡"


            output = (
                f"Coin: #{coin}\n"
                f"{position_emoji} {position}\n"
                f"{trade_type_emoji} {trade_type}\n"
                f"👉 Entry: {entry_price:.6f}\n"
                f"🌐 Leverage: {leverage:.2f}x\n"
                f"🎯 Target: {take_profit_price:.6f} (📈 {tp_movement_pct:.2f}%)\n"
                f"❌ StopLoss: {stop_loss_price:.6f} (📉 {abs(sl_movement_pct):.2f}%)\n"
                f"💰 Margin: ${margin:.2f}\n"
                f"⚠ Risk Amount: ${risk_amount:.2f}\n\n"
            )
            self.output_text.append(output)

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

    def calculate_margin(self):
        try:
            coin = self.coin_entry.text()
            position = self.position_dropdown.currentText()
            trade_type = self.trade_type_dropdown.currentText()
            entry_price = self._to_float_or_raise(self.entry_price_entry.text(), "entry price")
            stop_loss_price = self._to_float_or_raise(self.stop_loss_entry.text(), "stop loss")
            take_profit_price = self._to_float_or_raise(self.take_profit_entry.text(), "take profit")
            leverage = self._to_float_or_raise(self.margin_entry.text(), "leverage")
            risk_amount = self._to_float_or_raise(self.risk_amount_entry.text(), "risk amount")

            if position == 'LONG':
                sl_movement_pct = ((entry_price - stop_loss_price) / entry_price) * 100
                tp_movement_pct = ((take_profit_price - entry_price) / entry_price) * 100
            else:
                sl_movement_pct = ((stop_loss_price - entry_price) / entry_price) * 100
                tp_movement_pct = ((entry_price - take_profit_price) / entry_price) * 100

            margin = (risk_amount * 100) / (leverage * abs(sl_movement_pct))

            position_emoji = "🟢" if position == 'LONG' else "🔴"
            # ✅ UPDATED: Added emoji for STRATEGY
            if trade_type == 'SIGNAL':
                trade_type_emoji = "✅"
            elif trade_type == 'STRATEGY':
                trade_type_emoji = "🎯"
            else:
                trade_type_emoji = "💡"


            output = (
                f"Coin: #{coin}\n"
                f"{position_emoji} {position}\n"
                f"{trade_type_emoji} {trade_type}\n"
                f"👉 Entry: {entry_price:.6f}\n"
                f"🌐 Leverage: {leverage:.2f}x\n"
                f"🎯 Target: {take_profit_price:.6f} (📈 {tp_movement_pct:.2f}%)\n"
                f"❌ StopLoss: {stop_loss_price:.6f} (📉 {abs(sl_movement_pct):.2f}%)\n"
                f"💰 Margin: ${margin:.2f}\n"
                f"⚠ Risk Amount: ${risk_amount:.2f}\n\n"
            )
            self.output_text.append(output)

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

    def convert_coin_to_uppercase(self):
        text = self.coin_entry.text()
        self.coin_entry.blockSignals(True)
        self.coin_entry.setText(text.upper())
        self.coin_entry.blockSignals(False)

    def _to_float_or_raise(self, text, field_name="value"):
        try:
            return float(text)
        except Exception:
            raise ValueError(f"Please enter a valid numeric {field_name}.")

    def copy_output(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())

    def clear_all(self):
        self.coin_entry.clear()
        self.entry_price_entry.clear()
        self.stop_loss_entry.clear()
        self.take_profit_entry.clear()
        self.margin_entry.clear()
        self.risk_amount_entry.clear()
        self.output_text.clear()

    def add_record(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Redirect",
            "Do you want to redirect to the Journal tab and add this record?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                coin = self.coin_entry.text()
                position = self.position_dropdown.currentText()
                trade_type = self.trade_type_dropdown.currentText()
                entry_price = self._to_float_or_raise(self.entry_price_entry.text(), "entry price")
                stop_loss_price = self._to_float_or_raise(self.stop_loss_entry.text(), "stop loss")
                take_profit_price = self._to_float_or_raise(self.take_profit_entry.text(), "take profit")
                margin_or_leverage = self._to_float_or_raise(self.margin_entry.text(), "margin or leverage")
                risk_amount = self._to_float_or_raise(self.risk_amount_entry.text(), "risk amount")

                if position == 'LONG':
                    sl_percent = ((entry_price - stop_loss_price) / entry_price) * 100
                    tp_percent = ((take_profit_price - entry_price) / entry_price) * 100
                else:
                    sl_percent = ((stop_loss_price - entry_price) / entry_price) * 100
                    tp_percent = ((entry_price - take_profit_price) / entry_price) * 100

                # Calculate margin if in Margin Calculator mode
                if self.current_calculator == "Margin Calculator":
                    leverage = margin_or_leverage
                    margin = (risk_amount * 100) / (leverage * abs(sl_percent))
                else:
                    margin = margin_or_leverage

                self.redirect_to_journal(coin, position, trade_type, sl_percent, tp_percent, margin)

            except ValueError as e:
                QMessageBox.warning(self, "Input Error", str(e))

    def redirect_to_journal(self, coin, position, trade_type, sl_percent, tp_percent, trade_size):
        journal_tab = self.main_app.journal_tab
        try:
            journal_tab.pair_entry.setText(coin)
        except Exception:
            pass
        try:
            journal_tab.position_dropdown.setCurrentText(position if position in ['Long Position','Short Position','LONG','SHORT'] else position)
        except Exception:
            pass
        try:
            journal_tab.trade_type_dropdown.setCurrentText(trade_type)
            journal_tab.trade_type_dropdown.setVisible(True)
        except Exception:
            pass
        try:
            journal_tab.tp_entry.setText(f"{tp_percent:.2f}")
            journal_tab.sl_entry.setText(f"{sl_percent:.2f}")
            journal_tab.trade_size_entry.setText(str(trade_size))
        except Exception:
            pass

        # Only set leverage in Journal tab if using Margin Calculator
        if self.current_calculator == "Margin Calculator":
            try:
                # Calculate leverage for Margin Calculator
                entry_price = self._to_float_or_raise(self.entry_price_entry.text(), "entry price")
                stop_loss_price = self._to_float_or_raise(self.stop_loss_entry.text(), "stop loss")
                risk_amount = self._to_float_or_raise(self.risk_amount_entry.text(), "risk amount")
                leverage = self._to_float_or_raise(self.margin_entry.text(), "leverage")

                if position == 'LONG':
                    sl_movement_pct = ((entry_price - stop_loss_price) / entry_price) * 100
                else:
                    sl_movement_pct = ((stop_loss_price - entry_price) / entry_price) * 100

                # Set leverage in Journal tab
                journal_tab.leverage_entry.setText(f"{leverage:.2f}")
            except Exception:
                pass

        self.main_app.tabs.setCurrentWidget(journal_tab)

class TradeJournalApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # ==================== STEP 1: Initialize Theme Manager ====================
        self.theme_manager = ThemeManager()
        
        # ==================== STEP 2: Initialize Profile Manager ====================
        self.profile_manager = EnhancedProfileManager()
        
        # ==================== STEP 3: Profile Selection ====================
        selector = ProfileSelectorDialog(self.profile_manager)
        if selector.exec_() != QDialog.Accepted:
            import sys
            sys.exit(0)
        
        # ==================== STEP 4: Load Profile Data ====================
        self.active_profile = self.profile_manager.get_active_profile()
        self.account_balance = self.active_profile['balance']
        
        self.profile_id = self.active_profile['id']
        self.profile_path = f"profiles/profile_{self.profile_id}"
        self.screenshot_folder = f"{self.profile_path}/screenshots"
        self.trades_file = f"{self.profile_path}/trades.xlsx"
        
        os.makedirs(self.screenshot_folder, exist_ok=True)
        
        # ==================== STEP 5: Initialize UI ====================
        self.load_data()
        self.initUI()  # Now theme_manager exists!
        self.current_trade_index = None
        self.screenshot_counter = self.get_screenshot_counter()
        self._matrix_server_url = None

    def get_screenshot_counter(self):
        return len([f for f in os.listdir(self.screenshot_folder) if f.endswith('.png')])
    
    def initUI(self):
            self.setWindowTitle(f'Trade Journal - 👤 {self.active_profile["username"]}')
            self.setGeometry(100, 100, 1500, 700)
            
            # Set custom window icon ✅
            from PyQt5.QtGui import QIcon
            try:
                self.setWindowIcon(QIcon('app_icon.ico'))
            except:
                pass  # If icon file not found, use default
            
            # Create main layout
            main_layout = QVBoxLayout()
            
            # Add toolbar with profile info and buttons at the top
            toolbar_layout = QHBoxLayout()
            
            # Profile indicator (shows active profile)
            profile_color = self.active_profile.get('color', '#4CAF50')
            self.profile_indicator = QLabel(f"🔵 {self.active_profile['username']} | 💰 ${self.active_profile['balance']:.2f}")
            self.profile_indicator.setStyleSheet(f"""
                background-color: {profile_color};
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            """)
            toolbar_layout.addWidget(self.profile_indicator)
            
            toolbar_layout.addStretch()
            
            # Quick switch button (emoji only)
            switch_btn = QPushButton("🔄")
            switch_btn.setToolTip("Switch Profile")
            switch_btn.clicked.connect(self.quick_switch_profile)
            switch_btn.setFixedSize(50, 50)
            switch_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: none;
                    border-radius: 25px;
                    font-size: 24px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            toolbar_layout.addWidget(switch_btn)
            
            # Manage profiles button (emoji only)
            manage_btn = QPushButton("⚙️")
            manage_btn.setToolTip("Manage Profiles")
            manage_btn.clicked.connect(self.open_profile_dialog)
            manage_btn.setFixedSize(50, 50)
            manage_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    border: none;
                    border-radius: 25px;
                    font-size: 24px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            toolbar_layout.addWidget(manage_btn)
            
            # ✅ AI INTEGRATION: API Key Settings button
            if API_KEY_MANAGER_AVAILABLE:
                api_key_btn = QPushButton("🔑")
                api_key_btn.setToolTip("API Key Settings")
                api_key_btn.clicked.connect(self.open_api_key_dialog)
                api_key_btn.setFixedSize(50, 50)
                api_key_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FF9800;
                        border: none;
                        border-radius: 25px;
                        font-size: 24px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #F57C00;
                    }
                """)
                toolbar_layout.addWidget(api_key_btn)
            
            # Theme toggle button
            self.theme_toggle_btn = self.theme_manager.create_toggle_button(self)
            self.theme_toggle_btn.clicked.connect(self.toggle_theme_action)
            toolbar_layout.addWidget(self.theme_toggle_btn)
            
            main_layout.addLayout(toolbar_layout)
            
            # Create tabs
            self.tabs = QTabWidget()
            
            # Dashboard tab
            self.dashboard_tab = QWidget()
            self.init_dashboard_tab()
            self.tabs.addTab(self.dashboard_tab, 'Dashboard')
            
            # Alert tab
            self.alert_tab = CryptoTradeAlert(self)
            self.tabs.addTab(self.alert_tab, 'Calculator')
            
            # Journal and Trades tabs
            self.journal_tab = QWidget()
            self.trades_tab = QWidget()
            self.tabs.addTab(self.journal_tab, 'Journal')
            self.tabs.addTab(self.trades_tab, 'Trades')
            
            self.init_journal_tab()
            self.init_trades_tab()
            
            main_layout.addWidget(self.tabs)
            self.setLayout(main_layout)

            # Apply initial theme
            app = QApplication.instance()
            self.theme_manager.apply_theme(app, self.theme_toggle_btn)

    def quick_switch_profile(self):
        """Quick profile switching with password"""
        dialog = ProfileSelectorDialog(self.profile_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            # Reload the entire application with new profile
            self.reload_with_new_profile()

    def toggle_theme_action(self):
        """Toggle between dark and light theme"""
        self.theme_manager.toggle_theme()
        
        # Get the main QApplication instance
        app = QApplication.instance()
        
        # Apply new theme
        self.theme_manager.apply_theme(app, self.theme_toggle_btn)
        
        # No popup - just silently apply the theme ✅
    
    def open_profile_dialog(self):
        """Open the full profile management dialog"""
        dialog = EnhancedProfileDialog(self.profile_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            # Profile was switched, reload app
            self.reload_with_new_profile()
    
    def reload_with_new_profile(self):
            """Reload the application with the newly active profile"""
            # Get new active profile
            self.active_profile = self.profile_manager.get_active_profile()
            
            # Update paths
            self.profile_id = self.active_profile['id']
            self.profile_path = f"profiles/profile_{self.profile_id}"
            self.screenshot_folder = f"{self.profile_path}/screenshots"
            self.trades_file = f"{self.profile_path}/trades.xlsx"
            
            # CRITICAL: Sync account balance from profile manager
            self.active_profile = self.profile_manager.get_active_profile()
            self.account_balance = self.active_profile['balance']
            
            # Update window title
            self.setWindowTitle(f'Trade Journal - {self.active_profile["username"]}')
            
            # Update profile indicator
            profile_color = self.active_profile.get('color', '#4CAF50')
            self.profile_indicator.setText(f"Profile: {self.active_profile['username']} | Balance: ${self.account_balance:.2f}")
            self.profile_indicator.setStyleSheet(f"""
                background-color: {profile_color};
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            """)
            
            # Reload data
            self.load_data()
            self.populate_trades()
            self.refresh_dashboard()
            
            # Update balance label
            if hasattr(self, 'account_balance_label'):
                self.account_balance_label.setText(f"Account Balance: ${self.account_balance:.2f}")
            
            QMessageBox.information(self, "Profile Switched", 
                                f"Now using profile: {self.active_profile['username']}")
            
    # ✅ AI INTEGRATION: Open AI Analyzer method
    def open_ai_analyzer(self):
        """Open hidden AI analyzer tab"""
        if not AI_ANALYZER_AVAILABLE:
            QMessageBox.warning(
                self,
                "AI Analyzer Unavailable",
                "ai_analyzer.py module not found.\n\n"
                "Please ensure ai_analyzer.py is in the same directory as journal.py"
            )
            return
        
        # Create AI tab if it doesn't exist
        if not hasattr(self, 'ai_analyzer_tab'):
            self.ai_analyzer_tab = AIChartAnalyzer(self)
            # Add as hidden tab (not shown in tab bar initially)
            self.tabs.addTab(self.ai_analyzer_tab, '🤖 AI Analyzer')
        
        # Switch to AI analyzer tab
        self.tabs.setCurrentWidget(self.ai_analyzer_tab)
    
    # ✅ AI INTEGRATION: Open API Key Dialog
    def open_api_key_dialog(self):
        """Open API key management dialog"""
        if not API_KEY_MANAGER_AVAILABLE:
            QMessageBox.warning(
                self,
                "API Key Manager Unavailable",
                "api_key_manager.py module not found.\n\n"
                "Please ensure api_key_manager.py is in the same directory as journal.py"
            )
            return
        
        dialog = APIKeyDialog(self.profile_manager, self.profile_id, self)
        dialog.exec_()
    

    def refresh_dashboard(self):
        """Refresh the dashboard metrics and chart without rebuilding the layout."""
        if not hasattr(self, 'win_rate_label'):
            return  # dashboard not yet built

        # --- Load latest data from profile-specific file ---
        if os.path.exists(self.trades_file):
            try:
                df = pd.read_excel(self.trades_file)
            except Exception:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

        # --- Compute metrics safely ---
        if not df.empty and 'Outcome' in df.columns:
            total_trades = len(df)
            wins = (df['Outcome'] == 'Win').sum()
            losses = (df['Outcome'] == 'Loss').sum()
            win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

            pnl_values = pd.to_numeric(df.get('PnL %', pd.Series(dtype=float)), errors='coerce')
            avg_pnl = pnl_values.mean() if not pnl_values.empty else 0

            if 'PnL' in df.columns and len(df) > 0:
                df['PnL'] = pd.to_numeric(df['PnL'], errors='coerce').fillna(0)
                win_trades = df[df['PnL'] > 0].shape[0]
                loss_trades = df[df['PnL'] < 0].shape[0]
                total_trades = len(df)
                win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
                profit_factor = win_trades / loss_trades if loss_trades != 0 else 0
                biggest_win = df['PnL'].max()
                biggest_loss = df['PnL'].min()
                # CRITICAL: Use profile balance
                account_balance = self.account_balance
            else:
                win_rate = 0
                profit_factor = 0
                biggest_win = 0
                biggest_loss = 0
                # CRITICAL: Use profile balance
                account_balance = self.account_balance
        else:
            total_trades = wins = losses = win_rate = avg_pnl = profit_factor = biggest_win = biggest_loss = 0
        
        # CRITICAL: Always use profile's current balance from profile manager
        self.account_balance = self.active_profile['balance']
        account_balance = self.account_balance
        
        # Update profile indicator to match current balance
        if hasattr(self, 'profile_indicator') and hasattr(self, 'active_profile'):
            profile_color = self.active_profile.get('color', '#4CAF50')
            self.profile_indicator.setText(f"Profile: {self.active_profile['username']} | Balance: ${self.account_balance:.2f}")
            self.profile_indicator.setStyleSheet(f"""
                background-color: {profile_color};
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            """)

        # --- Update primary metrics ---
        self.win_rate_label.setText(f"🏆 Win Rate: {win_rate:.2f}%")
        self.total_trades_label.setText(f"📊 Total Trades: {total_trades}")
        self.wins_label.setText(f"✅ Wins: {wins}")
        self.losses_label.setText(f"❌ Losses: {losses}")

        # --- Update secondary cards ---
        self.account_balance_card.setText(f"${self.account_balance:.2f}")
        self.avg_pnl_card.setText(f"{avg_pnl:.2f}%")
        self.profit_factor_card.setText(f"{profit_factor:.2f}")
        self.biggest_card.setText(f"{biggest_win:.2f} / {biggest_loss:.2f}")

        # Update profile indicator
        if hasattr(self, 'profile_indicator'):
            self.profile_indicator.setText(f"🔵 {self.active_profile['username']} | 💰 ${account_balance:.2f}")

        # --- Refresh chart & recent trades ---
        self.update_dashboard_chart(df)
   
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
        
    def init_dashboard_tab(self):
        layout = QVBoxLayout()

        # --- BUTTONS ROW ---
        btn_layout = QHBoxLayout()
        self.matrix_btn = QPushButton("Matrix", self)
        self.matrix_btn.clicked.connect(self.open_matrix)
        btn_layout.addWidget(self.matrix_btn)

        # ✅ AI INTEGRATION: Modified Calculate button to open AI analyzer
        self.calculate_btn = QPushButton("Calculate", self)
        if AI_ANALYZER_AVAILABLE:
            self.calculate_btn.clicked.connect(self.open_ai_analyzer)
        else:
            self.calculate_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.alert_tab))
        btn_layout.addWidget(self.calculate_btn)


        refresh_btn = QPushButton("🔄 Refresh", self)
        refresh_btn.clicked.connect(self.refresh_dashboard)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

        # --- LOAD DATA ---
        # --- LOAD DATA ---
        # --- LOAD DATA ---
        df = None
        if os.path.exists(self.trades_file):
            try:
                df = pd.read_excel(self.trades_file)
            except Exception:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

        # --- CALCULATE INITIAL METRICS ---
        # Normalize column names immediately for safety (only if df is not empty)
        if not df.empty and len(df.columns) > 0:
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)
        # Ensure PnL % is numeric for avg_pnl calculation
        pnl_pct_series = pd.to_numeric(df.get('PnL %', pd.Series(dtype=float)), errors='coerce')

        if not df.empty:
            # Make sure Outcome / Status columns exist as strings
            if 'Outcome' in df.columns:
                total_trades = len(df)
                wins = (df['Outcome'] == 'Win').sum()
                losses = (df['Outcome'] == 'Loss').sum()
                win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
            else:
                total_trades = 0
                wins = 0
                losses = 0
                win_rate = 0

            avg_pnl = pnl_pct_series.mean() if not pnl_pct_series.empty and not pnl_pct_series.isnull().all() else 0

            # Ensure numeric PnL (closed trades contribute numbers, running trades -> 0)
            # Ensure numeric PnL (closed trades contribute numbers, running trades -> 0)
            if 'PnL' in df.columns:
                df['PnL'] = pd.to_numeric(df['PnL'], errors='coerce').fillna(0)
                win_sum = df[df['PnL'] > 0]['PnL'].sum()
                loss_sum = abs(df[df['PnL'] < 0]['PnL'].sum())
                profit_factor = win_sum / loss_sum if loss_sum != 0 else 0
                biggest_win = df['PnL'].max() if not df['PnL'].empty else 0
                biggest_loss = df['PnL'].min() if not df['PnL'].empty else 0
                # Use profile's current balance instead of calculating from scratch
                account_balance = self.account_balance
            else:
                # If no PnL column, still compute useful defaults
                profit_factor = 0
                biggest_win = 0
                biggest_loss = 0
                # CRITICAL: Use profile balance, not global settings
                account_balance = self.account_balance
        else:
            # DEFAULT VALUES WHEN NO TRADES AVAILABLE
            total_trades = 0
            wins = 0
            losses = 0
            win_rate = 0
            avg_pnl = 0
            profit_factor = 0
            biggest_win = 0
            biggest_loss = 0
                
            # Always use the profile's current account balance
            account_balance = self.account_balance

        # --- TOP METRICS (Horizontal Row) ---
        stats_layout = QHBoxLayout()
        font_style = "font-size: 28px; font-weight: bold; color: black;"

        # Store labels as attributes for live refresh
        self.win_rate_label = QLabel(f"🏆 Win Rate: {win_rate:.2f}%")
        self.win_rate_label.setStyleSheet(font_style)
        self.win_rate_label.setAlignment(Qt.AlignCenter)

        self.total_trades_label = QLabel(f"📊 Total Trades: {total_trades}")
        self.total_trades_label.setStyleSheet(font_style)
        self.total_trades_label.setAlignment(Qt.AlignCenter)

        self.wins_label = QLabel(f"✅ Wins: {wins}")
        self.wins_label.setStyleSheet(font_style)
        self.wins_label.setAlignment(Qt.AlignCenter)

        self.losses_label = QLabel(f"❌ Losses: {losses}")
        self.losses_label.setStyleSheet(font_style)
        self.losses_label.setAlignment(Qt.AlignCenter)

        stats_layout.addWidget(self.win_rate_label)
        stats_layout.addWidget(self.total_trades_label)
        stats_layout.addWidget(self.wins_label)
        stats_layout.addWidget(self.losses_label)
        layout.addLayout(stats_layout)

        # --- PERFORMANCE CARDS (Second Row) ---
        perf_layout = QHBoxLayout()

        # modified make_card() returns both frame and the value label
        def make_card(title, value, emoji=""):
            frame = QFrame()
            frame_layout = QVBoxLayout()
            label_title = QLabel(f"{emoji} {title}")
            label_value = QLabel(str(value))
            label_title.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
            label_value.setStyleSheet("font-size: 22px; color: black; font-weight: bold;")
            label_title.setAlignment(Qt.AlignCenter)
            label_value.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(label_title)
            frame_layout.addWidget(label_value)
            frame.setLayout(frame_layout)
            frame.setStyleSheet("QFrame {background-color: #f2f2f2; border-radius: 10px; padding: 10px;}")
            return frame, label_value

        # Create and keep references for refresh
        card1, self.account_balance_card = make_card("Account Balance", f"${account_balance:.2f}", "💰")
        card2, self.avg_pnl_card = make_card("Avg PnL %", f"{avg_pnl:.2f}%", "📈")
        card3, self.profit_factor_card = make_card("Profit Factor", f"{profit_factor:.2f}", "📊")
        card4, self.biggest_card = make_card("Biggest Win/Loss", f"{biggest_win:.2f} / {biggest_loss:.2f}", "💥")

        perf_layout.addWidget(card1)
        perf_layout.addWidget(card2)
        perf_layout.addWidget(card3)
        perf_layout.addWidget(card4)
        layout.addLayout(perf_layout)

        # --- CHART + RECENT TRADES CODE (keep as before) ---
        # (You can keep your chart and recent list sections exactly the same.)
        # --- PnL CURVE CHART ---
        chart_frame = QFrame()
        chart_layout = QVBoxLayout()

        self.pnl_fig = Figure(figsize=(6, 3))
        self.pnl_canvas = FigureCanvas(self.pnl_fig)
        chart_layout.addWidget(self.pnl_canvas)

        chart_frame.setLayout(chart_layout)
        layout.addWidget(chart_frame)

    # Draw first chart
        self.update_dashboard_chart(df)

        self.dashboard_tab.setLayout(layout)
        layout.addStretch(1)   # ← MUST be after setting layout

    # --- FIXED: Use the real Matrix launcher ---
    def open_matrix(self):
        if not FLASK_AVAILABLE:
            QMessageBox.warning(self, "Flask Missing", "Flask is not installed. Install Flask (pip install flask) to use Matrix.")
            return

        # CRITICAL: Get latest profile data
        self.active_profile = self.profile_manager.get_active_profile()
        self.account_balance = self.active_profile['balance']
        
        # Use unique port for each session to avoid conflicts
        import time
        port = 5001 + (int(time.time()) % 10)  # Rotates between 5001-5010
        
        ok, result = run_matrix_server(
            port=port, 
            profile_id=self.profile_id, 
            profile_balance=self.account_balance
        )
        
        if not ok:
            QMessageBox.warning(self, "Matrix Error", f"Could not start Matrix server: {result}")
            return
        
        self._matrix_server_url = result
        webbrowser.open(self._matrix_server_url)
            
    def update_dashboard_chart(self, df):
        # Clear chart
        self.pnl_fig.clear()
        ax = self.pnl_fig.add_subplot(111)

        # Safe copy + normalize name spacing
        df = df.copy() if df is not None else pd.DataFrame()
        
        # Only normalize columns if dataframe is not empty
        if not df.empty and len(df.columns) > 0:
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)

        if df.empty:
            ax.text(0.5, 0.5, "No data", ha='center', va='center')
            self.pnl_canvas.draw()
            return

        # Ensure numeric PnL (closed trades numeric, running trades -> 0)
        if 'PnL' in df.columns:
            df['PnL'] = pd.to_numeric(df['PnL'], errors='coerce').fillna(0)
        else:
            df['PnL'] = 0

        # Time-based sorting (if Time column valid)
        if 'Time' in df.columns:
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
            if not df['Time'].isnull().all():
                df = df.sort_values('Time').reset_index(drop=True)

        # Build cumulative PnL
        df['Cumulative'] = df['PnL'].cumsum()

        # X-axis selection
        if 'Time' in df.columns and not df['Time'].isnull().all():
            x = df['Time']
            ax.plot(x, df['Cumulative'])
            try:
                import matplotlib.dates as mdates
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
                for lbl in ax.get_xticklabels():
                    lbl.set_rotation(30)
                    lbl.set_ha('right')
            except:
                pass
        else:
            ax.plot(df.index, df['Cumulative'])

        # Labels
        ax.set_title("PnL Over Time")
        ax.set_ylabel("Cumulative PnL ($)")
        ax.set_xlabel("Trades")

        # Draw final
        self.pnl_fig.tight_layout()
        self.pnl_canvas.draw()

    # ---------------- Journal tab initialization ----------------
    def init_journal_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # ===== ROW 1: Trade Time, Day, Pair, Position, Type =====
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)

        # Trade Time
        row1_layout.addWidget(QLabel('Trade Time:'))
        self.time_entry = QLineEdit(self)
        self.time_entry.setReadOnly(True)
        self.time_entry.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.time_entry.setFixedWidth(150)
        row1_layout.addWidget(self.time_entry)

        # Day
        row1_layout.addWidget(QLabel('Day:'))
        self.day_entry = QLineEdit(self)
        self.day_entry.setReadOnly(True)
        self.day_entry.setFixedWidth(100)
        self.update_day()
        row1_layout.addWidget(self.day_entry)

        # Pair
        row1_layout.addWidget(QLabel('Pair:'))
        self.pair_entry = QLineEdit(self)
        self.pair_entry.setPlaceholderText("e.g., BTC/USDT")
        self.pair_entry.textChanged.connect(self.convert_pair_to_uppercase)
        self.pair_entry.setMinimumWidth(150)
        row1_layout.addWidget(self.pair_entry)

        # Position
        row1_layout.addWidget(QLabel('Position:'))
        self.position_dropdown = QComboBox(self)
        self.position_dropdown.addItems(['Long Position', 'Short Position'])
        self.position_dropdown.setFixedWidth(130)
        row1_layout.addWidget(self.position_dropdown)

        # Trade Type (hidden by default)
        row1_layout.addWidget(QLabel('Type:'))
        self.trade_type_dropdown = QComboBox(self)
        self.trade_type_dropdown.addItems(['IDEA', 'SIGNAL', 'STRATEGY'])
        self.trade_type_dropdown.setVisible(False)
        self.trade_type_dropdown.setFixedWidth(100)
        row1_layout.addWidget(self.trade_type_dropdown)

        row1_layout.addStretch()
        layout.addLayout(row1_layout)

        # ===== ROW 2: Notes =====
        row2_layout = QHBoxLayout()
        notes_label = QLabel('Notes:')
        notes_label.setFixedWidth(80)
        notes_label.setAlignment(Qt.AlignTop)
        row2_layout.addWidget(notes_label)
        
        self.notes_entry = QTextEdit(self)
        self.notes_entry.setFixedHeight(70)
        row2_layout.addWidget(self.notes_entry)
        layout.addLayout(row2_layout)

        # ===== Upload Screenshot 1 Button =====
        self.upload_btn1 = QPushButton('Upload Screenshot 1', self)
        self.upload_btn1.clicked.connect(lambda: self.upload_screenshot(1))
        layout.addWidget(self.upload_btn1)

        # ===== ROW 3: Trade Size, Leverage, TP%, SL% =====
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(10)

        row3_layout.addWidget(QLabel('Trade Size:'))
        self.trade_size_entry = QLineEdit(self)
        self.trade_size_entry.setFixedWidth(100)
        self.trade_size_entry.setMinimumWidth(100)
        row3_layout.addWidget(self.trade_size_entry)

        row3_layout.addWidget(QLabel('Leverage:'))
        self.leverage_entry = QLineEdit(self)
        self.leverage_entry.setFixedWidth(80)
        self.leverage_entry.setMinimumWidth(80)
        row3_layout.addWidget(self.leverage_entry)

        row3_layout.addWidget(QLabel('TP %:'))
        self.tp_entry = QLineEdit(self)
        self.tp_entry.setFixedWidth(80)
        self.tp_entry.setMinimumWidth(80)
        row3_layout.addWidget(self.tp_entry)

        row3_layout.addWidget(QLabel('SL %:'))
        self.sl_entry = QLineEdit(self)
        self.sl_entry.setFixedWidth(80)
        self.sl_entry.setMinimumWidth(80)
        row3_layout.addWidget(self.sl_entry)

        row3_layout.addStretch()
        layout.addLayout(row3_layout)

        # ===== ROW 4: TP Amount, SL Amount, R/R =====
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(10)

        row4_layout.addWidget(QLabel('TP Amount:'))
        self.tp_amount_entry = QLineEdit(self)
        self.tp_amount_entry.setFixedWidth(100)
        row4_layout.addWidget(self.tp_amount_entry)

        row4_layout.addWidget(QLabel('SL Amount:'))
        self.sl_amount_entry = QLineEdit(self)
        self.sl_amount_entry.setFixedWidth(100)
        row4_layout.addWidget(self.sl_amount_entry)

        row4_layout.addWidget(QLabel('R/R:'))
        self.rr_ratio_entry = QLineEdit(self)
        self.rr_ratio_entry.setFixedWidth(80)
        row4_layout.addWidget(self.rr_ratio_entry)

        row4_layout.addStretch()
        layout.addLayout(row4_layout)

        # ===== ROW 5: Status =====
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(10)

        row5_layout.addWidget(QLabel('Status:'))
        self.status_dropdown = QComboBox(self)
        self.status_dropdown.addItems(['Running', 'Closed'])
        self.status_dropdown.currentIndexChanged.connect(self.status_changed)
        self.status_dropdown.setFixedWidth(130)
        row5_layout.addWidget(self.status_dropdown)

        row5_layout.addStretch()
        layout.addLayout(row5_layout)

        # ===== HIDDEN WIDGET (For Closed Status) =====
        self.hidden_widget = QWidget()
        hidden_main_layout = QVBoxLayout(self.hidden_widget)
        hidden_main_layout.setSpacing(8)
        hidden_main_layout.setContentsMargins(0, 0, 0, 0)

        # Outcome, PnL, PnL% in one line
        hidden_row1 = QHBoxLayout()
        hidden_row1.setSpacing(10)

        hidden_row1.addWidget(QLabel('Outcome:'))
        self.outcome_dropdown = QComboBox(self)
        self.outcome_dropdown.addItems(['Break Even', 'Win', 'Loss'])
        self.outcome_dropdown.currentIndexChanged.connect(self.calculate_pnl)
        self.outcome_dropdown.setFixedWidth(120)
        hidden_row1.addWidget(self.outcome_dropdown)

        hidden_row1.addWidget(QLabel('PnL:'))
        self.pnl_entry = QLineEdit(self)
        self.pnl_entry.setFixedWidth(100)
        hidden_row1.addWidget(self.pnl_entry)

        hidden_row1.addWidget(QLabel('PnL %:'))
        self.pnl_percent_entry = QLineEdit(self)
        self.pnl_percent_entry.setFixedWidth(100)
        hidden_row1.addWidget(self.pnl_percent_entry)

        hidden_row1.addStretch()
        hidden_main_layout.addLayout(hidden_row1)

        # Upload Screenshot 2
        self.upload_btn2 = QPushButton('Upload Screenshot 2', self)
        self.upload_btn2.clicked.connect(lambda: self.upload_screenshot(2))
        hidden_main_layout.addWidget(self.upload_btn2)

        # Closed Notes
        hidden_notes_layout = QHBoxLayout()
        closed_notes_label = QLabel('Closed Notes:')
        closed_notes_label.setFixedWidth(100)
        closed_notes_label.setAlignment(Qt.AlignTop)
        hidden_notes_layout.addWidget(closed_notes_label)
        
        self.closed_notes_entry = QTextEdit(self)
        self.closed_notes_entry.setFixedHeight(70)
        hidden_notes_layout.addWidget(self.closed_notes_entry)
        hidden_main_layout.addLayout(hidden_notes_layout)

        layout.addWidget(self.hidden_widget)
        self.hidden_widget.setVisible(False)

        # ===== ACTION BUTTONS =====
        reset_btn = QPushButton('Reset', self)
        reset_btn.clicked.connect(self.reset_fields)
        layout.addWidget(reset_btn)

        add_trade_btn = QPushButton('Add Trade', self)
        add_trade_btn.clicked.connect(self.add_trade)
        layout.addWidget(add_trade_btn)

        update_trade_btn = QPushButton('Update Trade', self)
        update_trade_btn.clicked.connect(self.update_trade)
        layout.addWidget(update_trade_btn)

        self.capital_btn = QPushButton('Edit Capital', self)
        self.capital_btn.clicked.connect(self.edit_capital)
        layout.addWidget(self.capital_btn)

        # ===== RIGHT SIDE: Screenshots =====
        right_layout = QVBoxLayout()
        
        self.screenshot1_label = QLabel(self)
        self.screenshot1_label.setFixedSize(350, 180)
        self.screenshot1_label.setStyleSheet("border: 2px solid #4CAF50; border-radius: 6px;")
        self.screenshot1_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.screenshot1_label)
        
        self.screenshot2_label = QLabel(self)
        self.screenshot2_label.setFixedSize(350, 180)
        self.screenshot2_label.setStyleSheet("border: 2px solid #4CAF50; border-radius: 6px;")
        self.screenshot2_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.screenshot2_label)
        
        right_layout.addStretch()

        # ===== MAIN LAYOUT: Left + Right =====
        main_journal_layout = QHBoxLayout()
        main_journal_layout.addLayout(layout, 3)  # Left side takes more space
        main_journal_layout.addLayout(right_layout, 1)  # Right side for screenshots

        # ===== SCROLL AREA =====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        container.setLayout(main_journal_layout)
        scroll_area.setWidget(container)

        journal_main_layout = QVBoxLayout()
        journal_main_layout.addWidget(scroll_area)
        journal_main_layout.setContentsMargins(0, 0, 0, 0)
        self.journal_tab.setLayout(journal_main_layout)

        # ===== MAP WIDGETS TO JOURNAL TAB =====
        widget_names = [
            'time_entry', 'day_entry', 'pair_entry', 'position_dropdown', 'trade_type_dropdown',
            'notes_entry', 'upload_btn1', 'trade_size_entry', 'leverage_entry', 'tp_entry', 'sl_entry',
            'tp_amount_entry', 'sl_amount_entry', 'rr_ratio_entry', 'status_dropdown', 'hidden_widget',
            'outcome_dropdown', 'pnl_entry', 'pnl_percent_entry', 'upload_btn2', 'closed_notes_entry',
            'screenshot1_label', 'screenshot2_label'
        ]
        for name in widget_names:
            if hasattr(self, name):
                setattr(self.journal_tab, name, getattr(self, name))

        # ===== CONNECT SIGNALS =====
        self.trade_size_entry.textChanged.connect(self.calculate_amounts)
        self.leverage_entry.textChanged.connect(self.calculate_amounts)
        self.tp_entry.textChanged.connect(self.calculate_amounts)
        self.sl_entry.textChanged.connect(self.calculate_amounts)
        self.time_entry.textChanged.connect(self.update_day)
    def update_day(self):
        try:
            trade_time = datetime.datetime.strptime(self.time_entry.text(), '%Y-%m-%d %H:%M:%S')
            self.day_entry.setText(trade_time.strftime('%A'))
        except ValueError:
            pass

    def convert_pair_to_uppercase(self):
        text = self.pair_entry.text()
        self.pair_entry.setText(text.upper())

    def get_screenshot_counter(self):
        return len([f for f in os.listdir(self.screenshot_folder) if f.endswith('.png')])

    def upload_screenshot(self, screenshot_num):
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(
                self, 
                "Upload Screenshot", 
                "", 
                "Images (*.png *.xpm *.jpg *.jpeg)", 
                options=options
            )
            
            if file_name:
                date_str = datetime.datetime.now().strftime('%Y-%m-%d')
                new_file_name = f"{date_str}_{self.screenshot_counter + 1}.png"
                new_file_path = os.path.join(self.screenshot_folder, new_file_name)
                
                shutil.copy(file_name, new_file_path)
                
                if screenshot_num == 1:
                    self.screenshot1_path = new_file_path
                    pixmap = QPixmap(new_file_path).scaled(
                        self.screenshot1_label.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.screenshot1_label.setPixmap(pixmap)
                    self.screenshot_counter += 1
                elif screenshot_num == 2:
                    self.screenshot2_path = new_file_path
                    pixmap = QPixmap(new_file_path).scaled(
                        self.screenshot2_label.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.screenshot2_label.setPixmap(pixmap)
                    self.screenshot_counter += 1

  
    def status_changed(self, index):
        if self.status_dropdown.currentText() == 'Closed':
            self.hidden_widget.setVisible(True)
        else:
            self.hidden_widget.setVisible(False)

    def reset_fields(self):
        self.time_entry.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.update_day()
        self.pair_entry.clear()
        self.notes_entry.clear()
        self.screenshot1_label.clear()
        self.screenshot2_label.clear()
        self.trade_size_entry.clear()
        self.leverage_entry.clear()
        self.tp_entry.clear()
        self.sl_entry.clear()
        self.tp_amount_entry.clear()
        self.sl_amount_entry.clear()
        self.rr_ratio_entry.clear()
        self.status_dropdown.setCurrentIndex(0)
        self.hidden_widget.setVisible(False)
        self.outcome_dropdown.setCurrentIndex(0)
        self.pnl_entry.clear()
        self.pnl_percent_entry.clear()
        self.closed_notes_entry.clear()
        self.position_dropdown.setCurrentIndex(0)
        self.current_trade_index = None
        self.trade_type_dropdown.setVisible(False)

    def calculate_amounts(self):
        try:
            trade_size = float(self.trade_size_entry.text())
            leverage = float(self.leverage_entry.text())
            tp_percent = float(self.tp_entry.text())
            sl_percent = float(self.sl_entry.text())
            tp_amount = trade_size * leverage * (tp_percent / 100)
            sl_amount = trade_size * leverage * (sl_percent / 100)
            rr_ratio = tp_amount / sl_amount if sl_amount != 0 else 0
            self.tp_amount_entry.setText(f"{tp_amount:.2f}")
            self.sl_amount_entry.setText(f"{sl_amount:.2f}")
            self.rr_ratio_entry.setText(f"{rr_ratio:.2f}")
        except Exception:
            self.tp_amount_entry.clear()
            self.sl_amount_entry.clear()
            self.rr_ratio_entry.clear()

    def calculate_pnl(self):
        outcome = self.outcome_dropdown.currentText()
        try:
            tp_amount = float(self.tp_amount_entry.text())
            account_capital = self.account_balance
            if outcome == 'Break Even':
                pnl = 0
                pnl_percent = 0
            elif outcome == 'Win':
                pnl = tp_amount
                pnl_percent = (tp_amount / account_capital) * 100
            elif outcome == 'Loss':
                pnl = -float(self.sl_amount_entry.text())
                pnl_percent = (pnl / account_capital) * 100
            self.pnl_entry.setText(f"{pnl:.2f}")
            self.pnl_percent_entry.setText(f"{pnl_percent:.2f}")
        except Exception:
            self.pnl_entry.clear()
            self.pnl_percent_entry.clear()

    def add_trade(self):
            try:
                trade_size_val = float(self.trade_size_entry.text())
            except Exception:
                QMessageBox.warning(self, "Input Error", "Please enter a valid numeric Trade Size.")
                return
            
            trade_data = {
                'Time': self.time_entry.text(),
                'Pair': self.pair_entry.text(),
                'Notes': self.notes_entry.toPlainText(),
                'Screenshot1': getattr(self, 'screenshot1_path', ''),
                'Screenshot2': getattr(self, 'screenshot2_path', ''),
                'Trade Size': trade_size_val,
                'Leverage': self.leverage_entry.text(),
                'Take Profit %': self.tp_entry.text(),
                'Stop Loss %': self.sl_entry.text(),
                'Take Profit Amount': self.tp_amount_entry.text(),
                'Stop Loss Amount': self.sl_amount_entry.text(),
                'Risk/Reward Ratio': self.rr_ratio_entry.text(),
                'Status': self.status_dropdown.currentText(),
                'Outcome': self.outcome_dropdown.currentText() if self.status_dropdown.currentText() == 'Closed' else '',
                'PnL': self.pnl_entry.text() if self.status_dropdown.currentText() == 'Closed' else '',
                'PnL %': self.pnl_percent_entry.text() if self.status_dropdown.currentText() == 'Closed' else '',
                'Closed Notes': self.closed_notes_entry.toPlainText() if self.status_dropdown.currentText() == 'Closed' else '',
                'Position Type': self.position_dropdown.currentText()
            }
            
            # CRITICAL: Update account balance and profile
            self.account_balance -= trade_data['Trade Size']
            
            # Update profile balance in profile manager
            self.profile_manager.update_balance(
                self.profile_id, 
                self.account_balance, 
                f"Trade opened: {trade_data['Pair']}"
            )
            
            # CRITICAL: Reload active profile to get updated balance
            self.active_profile = self.profile_manager.get_active_profile()
            self.account_balance = self.active_profile['balance'] 

            # Add to dataframe
            if not hasattr(self, 'df'):
                self.df = pd.DataFrame()
            self.df = pd.concat([self.df, pd.DataFrame([trade_data])], ignore_index=True)
            
            # Save to profile-specific file
            try:
                self.df.to_excel(self.trades_file, index=False)
            except Exception as e:
                print("Error saving trades:", e)
            
            # Update UI
            self.populate_trades()
            self.reset_fields()
            self.account_balance_label.setText(f"Account Balance: ${self.account_balance:.2f}")
            
            # Update profile indicator
            self.profile_indicator.setText(f"🔵 {self.active_profile['username']} | 💰 ${self.account_balance:.2f}")
            
            self.refresh_dashboard()

    def update_trade(self):
            if self.current_trade_index is not None:
                try:
                    trade_size_val = float(self.trade_size_entry.text())
                except Exception:
                    QMessageBox.warning(self, "Input Error", "Please enter a valid numeric Trade Size.")
                    return
                
                trade_data = {
                    'Time': self.time_entry.text(),
                    'Pair': self.pair_entry.text(),
                    'Notes': self.notes_entry.toPlainText(),
                    'Screenshot1': getattr(self, 'screenshot1_path', ''),
                    'Screenshot2': getattr(self, 'screenshot2_path', ''),
                    'Trade Size': trade_size_val,
                    'Leverage': self.leverage_entry.text(),
                    'Take Profit %': self.tp_entry.text(),
                    'Stop Loss %': self.sl_entry.text(),
                    'Take Profit Amount': self.tp_amount_entry.text(),
                    'Stop Loss Amount': self.sl_amount_entry.text(),
                    'Risk/Reward Ratio': self.rr_ratio_entry.text(),
                    'Status': self.status_dropdown.currentText(),
                    'Outcome': self.outcome_dropdown.currentText() if self.status_dropdown.currentText() == 'Closed' else '',
                    'PnL': self.pnl_entry.text() if self.status_dropdown.currentText() == 'Closed' else '',
                    'PnL %': self.pnl_percent_entry.text() if self.status_dropdown.currentText() == 'Closed' else '',
                    'Closed Notes': self.closed_notes_entry.toPlainText() if self.status_dropdown.currentText() == 'Closed' else '',
                    'Position Type': self.position_dropdown.currentText()
                }
                
                # Recalculate balance
                # CRITICAL: Recalculate balance from profile manager
                old_status = self.df.at[self.current_trade_index, 'Status']
                old_trade_size = self.df.at[self.current_trade_index, 'Trade Size']
                
                # Return old trade size if it was running
                if old_status == 'Running':
                    self.account_balance += old_trade_size
                
                # Process new trade status
                if trade_data['Status'] == 'Running':
                    # Deduct new trade size
                    self.account_balance -= trade_data['Trade Size']
                elif trade_data['Status'] == 'Closed':
                    try:
                        pnl_float = float(trade_data['PnL'])
                    except Exception:
                        pnl_float = 0.0
                    # If was closed, don't deduct trade size, just add PnL difference
                    if old_status == 'Closed':
                        old_pnl = float(self.df.at[self.current_trade_index, 'PnL']) if self.df.at[self.current_trade_index, 'PnL'] else 0
                        self.account_balance += (pnl_float - old_pnl)
                    else:
                        # Was running, now closed: add trade size back + PnL
                        self.account_balance += pnl_float
                
                # Update profile balance
                self.profile_manager.update_balance(
                    self.profile_id,
                    self.account_balance,
                    f"Trade updated: {trade_data['Pair']}"
                )
                
                # CRITICAL: Reload profile
                self.active_profile = self.profile_manager.get_active_profile()
                self.account_balance = self.active_profile['balance']
                
                # Update dataframe
                for key, value in trade_data.items():
                    self.df.at[self.current_trade_index, key] = value
                
                # Save to profile-specific file
                try:
                    self.df.to_excel(self.trades_file, index=False)
                except Exception:
                    pass
                
                # Update UI
                self.populate_trades()
                self.reset_fields()
                self.account_balance_label.setText(f"Account Balance: ${self.account_balance:.2f}")
                
                # Update profile indicator
                self.active_profile = self.profile_manager.get_active_profile()
                self.profile_indicator.setText(f"🔵 {self.active_profile['username']} | 💰 ${self.account_balance:.2f}")
                
                self.refresh_dashboard()
    def load_trade(self, item):
        self.tabs.setCurrentWidget(self.journal_tab)
        time, pair = item.text().split(' - ')
        trade = self.df[(self.df['Time'] == time) & (self.df['Pair'] == pair)]
        if not trade.empty:
            self.current_trade_index = trade.index[0]
            trade = trade.iloc[0]
            self.time_entry.setText(trade['Time'])
            self.update_day()
            self.pair_entry.setText(trade['Pair'])
            # ---- SAFE FIX: force Notes fields to string ----
            notes = trade.get('Notes', "")
            closed_notes = trade.get('Closed Notes', "")

            # Convert floats/NaN to clean strings
            if not isinstance(notes, str):
                notes = "" if pd.isna(notes) else str(notes)
            if not isinstance(closed_notes, str):
                closed_notes = "" if pd.isna(closed_notes) else str(closed_notes)

            self.notes_entry.setPlainText(notes)
            if trade['Screenshot1'] and not pd.isna(trade['Screenshot1']):
                pixmap = QPixmap(trade['Screenshot1']).scaled(self.screenshot1_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.screenshot1_label.setPixmap(pixmap)
                self.screenshot1_path = trade['Screenshot1']
            else:
                self.screenshot1_label.clear()
                self.screenshot1_path = ''
            if trade['Screenshot2'] and not pd.isna(trade['Screenshot2']):
                pixmap = QPixmap(trade['Screenshot2']).scaled(self.screenshot2_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.screenshot2_label.setPixmap(pixmap)
                self.screenshot2_path = trade['Screenshot2']
            else:
                self.screenshot2_label.clear()
                self.screenshot2_path = ''
            self.trade_size_entry.setText(str(trade['Trade Size']))
            self.leverage_entry.setText(str(trade['Leverage']))
            self.tp_entry.setText(str(trade['Take Profit %']))
            self.sl_entry.setText(str(trade['Stop Loss %']))
            self.tp_amount_entry.setText(str(trade['Take Profit Amount']))
            self.sl_amount_entry.setText(str(trade['Stop Loss Amount']))
            self.rr_ratio_entry.setText(str(trade['Risk/Reward Ratio']))
            self.status_dropdown.setCurrentText(trade['Status'])
            self.position_dropdown.setCurrentText(trade['Position Type'])
            if trade['Status'] == 'Closed':
                self.hidden_widget.setVisible(True)
                self.outcome_dropdown.setCurrentText(trade['Outcome'])
                self.pnl_entry.setText(str(trade['PnL']))
                self.pnl_percent_entry.setText(str(trade['PnL %']))
                # Same protection for closed notes
                closed_notes = trade.get('Closed Notes', "")
                if not isinstance(closed_notes, str):
                    closed_notes = "" if pd.isna(closed_notes) else str(closed_notes)
                self.closed_notes_entry.setPlainText(closed_notes)
            else:
                self.hidden_widget.setVisible(False)

    def delete_trade(self):
            selected_items = self.running_trades_list.selectedItems() + self.closed_trades_list.selectedItems()
            if selected_items:
                item = selected_items[0]
                time, pair = item.text().split(' - ')
                trade = self.df[(self.df['Time'] == time) & (self.df['Pair'] == pair)]
                if not trade.empty:
                    trade_row = trade.iloc[0]
                    
                    # CRITICAL: Return balance if trade was running
                    if trade_row['Status'] == 'Running':
                        self.account_balance += trade_row['Trade Size']
                        self.profile_manager.update_balance(
                            self.profile_id,
                            self.account_balance,
                            f"Trade deleted: {trade_row['Pair']}"
                        )
                        self.active_profile = self.profile_manager.get_active_profile()
                        self.account_balance = self.active_profile['balance']
                    
                    # Delete trade
                    self.df = self.df.drop(trade.index)
                    try:
                        self.df.to_excel(self.trades_file, index=False)
                    except Exception:
                        pass
                    
                    # Update UI
                    self.populate_trades()
                    self.account_balance_label.setText(f"Account Balance: ${self.account_balance:.2f}")
                    self.profile_indicator.setText(f"Profile: {self.active_profile['username']} | Balance: ${self.account_balance:.2f}")
                    self.refresh_dashboard()

    def filter_trades(self, index):
        filter_option = self.filter_dropdown.currentText()
        today = datetime.date.today()
        if filter_option == 'Today':
            filtered_df = self.df[self.df['Time'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date() == today)]
        elif filter_option == 'Last 7 Days':
            filtered_df = self.df[self.df['Time'].apply(lambda x: (today - datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()).days <= 7)]
        elif filter_option == 'Last 30 Days':
            filtered_df = self.df[self.df['Time'].apply(lambda x: (today - datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()).days <= 30)]
        else:
            filtered_df = self.df
        self.populate_filtered_trades(filtered_df)

    def populate_filtered_trades(self, filtered_df):
        running_trades = filtered_df[filtered_df['Status'] == 'Running']
        closed_trades = filtered_df[filtered_df['Status'] == 'Closed']
        self.running_trades_list.clear()
        self.closed_trades_list.clear()
        for index, row in running_trades.iterrows():
            self.running_trades_list.addItem(f"{row['Time']} - {row['Pair']}")
        for index, row in closed_trades.iterrows():
            self.closed_trades_list.addItem(f"{row['Time']} - {row['Pair']}")

    def load_data(self):
            # CRITICAL: Always use profile-specific file path
            if os.path.exists(self.trades_file):
                try:
                    self.df = pd.read_excel(self.trades_file)
                    
                    # Force text columns to string
                    text_cols = ['Notes', 'Closed Notes', 'Screenshot1', 'Screenshot2', 'Pair', 'Outcome', 'Status']
                    for col in text_cols:
                        if col in self.df.columns:
                            self.df[col] = self.df[col].astype(str).fillna("")
                except Exception as e:
                    print(f"Error loading {self.trades_file}: {e}")
                    self.df = pd.DataFrame(columns=[
                        'Time', 'Pair', 'Notes', 'Screenshot1', 'Screenshot2', 'Trade Size', 'Leverage',
                        'Take Profit %', 'Stop Loss %', 'Take Profit Amount', 'Stop Loss Amount',
                        'Risk/Reward Ratio', 'Status', 'Outcome', 'PnL', 'PnL %',
                        'Closed Notes', 'Position Type'
                    ])
            else:
                self.df = pd.DataFrame(columns=[
                    'Time', 'Pair', 'Notes', 'Screenshot1', 'Screenshot2', 'Trade Size', 'Leverage',
                    'Take Profit %', 'Stop Loss %', 'Take Profit Amount', 'Stop Loss Amount',
                    'Risk/Reward Ratio', 'Status', 'Outcome', 'PnL', 'PnL %',
                    'Closed Notes', 'Position Type'
                ])
        

    def populate_trades(self):
        running_trades = self.df[self.df['Status'] == 'Running'] if 'Status' in self.df.columns else pd.DataFrame()
        closed_trades = self.df[self.df['Status'] == 'Closed'] if 'Status' in self.df.columns else pd.DataFrame()
        self.running_trades_list.clear()
        self.closed_trades_list.clear()
        for index, row in running_trades.iterrows():
            self.running_trades_list.addItem(f"{row['Time']} - {row['Pair']}")
        for index, row in closed_trades.iterrows():
            self.closed_trades_list.addItem(f"{row['Time']} - {row['Pair']}")

    def edit_capital(self):
            new_balance, ok = QInputDialog.getDouble(
                self, 
                "Edit Capital", 
                "Enter new account balance:", 
                self.account_balance, 
                0, 1e9, 2
            )
            
            if ok:
                self.account_balance = new_balance
                
                # Update profile balance
                self.profile_manager.update_balance(
                    self.profile_id,
                    new_balance,
                    "Manual balance adjustment"
                )
                
                # Update UI
                self.account_balance_label.setText(f"Account Balance: ${self.account_balance:.2f}")
                
                # Update profile indicator
                self.active_profile = self.profile_manager.get_active_profile()
                self.profile_indicator.setText(f"🔵 {self.active_profile['username']} | 💰 ${self.account_balance:.2f}")
                
                try:
                    self.refresh_dashboard()
                except Exception:
                    pass

    def init_trades_tab(self):
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        self.filter_dropdown = QComboBox(self)
        self.filter_dropdown.addItems(['Today', 'Last 7 Days', 'Last 30 Days', 'All'])
        self.filter_dropdown.currentIndexChanged.connect(self.filter_trades)
        filter_layout.addWidget(QLabel('Filter Trades:'))
        filter_layout.addWidget(self.filter_dropdown)
        layout.addLayout(filter_layout)
        self.running_trades_list = QListWidget(self)
        self.running_trades_list.itemDoubleClicked.connect(self.load_trade)
        layout.addWidget(QLabel('Running Trades:'))
        layout.addWidget(self.running_trades_list)
        self.closed_trades_list = QListWidget(self)
        self.closed_trades_list.itemDoubleClicked.connect(self.load_trade)
        layout.addWidget(QLabel('Closed Trades:'))
        layout.addWidget(self.closed_trades_list)      
        delete_btn = QPushButton('Delete Trade', self)
        delete_btn.clicked.connect(self.delete_trade)
        layout.addWidget(delete_btn)
        self.account_balance_label = QLabel(f"Account Balance: ${self.account_balance:.2f}", self)
        layout.addWidget(self.account_balance_label)
        self.trades_tab.setLayout(layout)

        # 🔥 FIX: Populate trades immediately when Trades tab is created
        try:
            self.populate_trades()
        except Exception as e:
            print("Error populating trades:", e)


# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TradeJournalApp()
    ex.show()
    sys.exit(app.exec_())