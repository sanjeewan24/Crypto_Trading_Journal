"""
AI Chart Analyzer Tab
Analyzes TradingView screenshots using Gemini API
"""

import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QFileDialog, QMessageBox,
    QFrame, QSplitter, QProgressBar, QApplication
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import google.generativeai as genai
from PIL import Image
from theme_manager import EmojiLib


class GeminiAnalyzerThread(QThread):
    """Background thread for Gemini API calls"""
    analysis_complete = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, api_key, image_path, prompt):
        super().__init__()
        self.api_key = api_key
        self.image_path = image_path
        self.prompt = prompt
    
    def run(self):
        try:
            # Configure Gemini (using latest experimental flash model)
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # Load and prepare image
            img = Image.open(self.image_path)
            
            # Generate analysis (this may take 5-15 seconds)
            response = model.generate_content([self.prompt, img])

            
            # Parse response
            result = self.parse_gemini_response(response.text)
            self.analysis_complete.emit(result)
            
        except Exception as e:
            self.analysis_error.emit(str(e))
    
    def parse_gemini_response(self, text):
        """Parse Gemini response to extract trading parameters"""
        result = {
            'raw_response': text,
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'position_type': None,
            'confidence': 'Unknown',
            'detected_values': []
        }
        
        try:
            # Look for common patterns in trading charts
            lines = text.split('\n')  # Keep original case for number extraction
            
            for line in lines:
                line_lower = line.lower()
                
                # Entry price detection (prioritize lines with "entry" keyword)
                if ('entry' in line_lower or 'enter' in line_lower) and not result['entry_price']:
                    price = self.extract_number(line)
                    if price and price > 0:
                        result['entry_price'] = price
                        result['detected_values'].append(f"Entry Price: {price:,.2f}")
                
                # Stop loss detection (prioritize lines with "stop loss" or "sl")
                if (('stop' in line_lower and 'loss' in line_lower) or 
                    'stoploss' in line_lower or 
                    (line_lower.strip().startswith('sl') and ':' in line)) and not result['stop_loss']:
                    price = self.extract_number(line)
                    if price and price > 0 and price != result.get('entry_price'):
                        result['stop_loss'] = price
                        result['detected_values'].append(f"Stop Loss: {price:,.2f}")
                
                # Take profit detection (prioritize lines with "take profit", "tp", or "target")
                if (('take' in line_lower and 'profit' in line_lower) or 
                    'takeprofit' in line_lower or 
                    'target' in line_lower or
                    (line_lower.strip().startswith('tp') and ':' in line)) and not result['take_profit']:
                    price = self.extract_number(line)
                    if price and price > 0 and price != result.get('entry_price'):
                        result['take_profit'] = price
                        result['detected_values'].append(f"Take Profit: {price:,.2f}")
                
                # Position type detection
                if 'long' in line_lower and not result['position_type']:
                    result['position_type'] = 'LONG'
                    result['detected_values'].append("Position: LONG")
                elif 'short' in line_lower and not result['position_type']:
                    result['position_type'] = 'SHORT'
                    result['detected_values'].append("Position: SHORT")
            
            # Set confidence based on detected values
            detected_count = len([v for v in [result['entry_price'], 
                                              result['stop_loss'], 
                                              result['take_profit']] if v])
            if detected_count == 3 and result['position_type']:
                result['confidence'] = 'High'
            elif detected_count == 3:
                result['confidence'] = 'Medium-High'
            elif detected_count == 2:
                result['confidence'] = 'Medium'
            else:
                result['confidence'] = 'Low'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result

    
    def extract_number(self, text):
        """Extract numeric price from text (handles commas and decimals)"""
        import re
        # Look for numbers with commas and decimal points (e.g., 89,254.3 or 89254.3)
        # Pattern explanation: \d+ (digits) (?:,\d{3})* (optional comma groups) (?:\.\d+)? (optional decimal)
        matches = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', text)
        if matches:
            try:
                # Remove commas and convert to float
                cleaned = matches[0].replace(',', '')
                return float(cleaned)
            except:
                return None
        return None



class AIChartAnalyzer(QWidget):
    """AI-powered chart analysis tab"""
    
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.current_image_path = None
        self.analyzer_thread = None
        self.current_calculator = "Leverage Calculator"
        self.last_ai_result = None  # ✅ Store last AI analysis result
        self.initUI()

    
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left Panel - Input Section
        left_layout = QVBoxLayout()
        
        # Calculator selector
        self.calculator_selector = QComboBox()
        self.calculator_selector.addItems(["Leverage Calculator", "Margin Calculator"])
        self.calculator_selector.currentTextChanged.connect(self.switch_calculator)
        left_layout.addWidget(QLabel("📊 Calculator Type"))
        left_layout.addWidget(self.calculator_selector)
        
        # Image upload section
        upload_frame = QFrame()
        upload_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #4CAF50;
                border-radius: 10px;
                background-color: rgba(76, 175, 80, 0.1);
                padding: 20px;
            }
        """)
        upload_layout = QVBoxLayout()
        
        # Image preview
        self.image_label = QLabel("📸 No image uploaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("border: none; font-size: 16px; color: #888;")
        upload_layout.addWidget(self.image_label)
        
        # Upload button
        upload_btn = QPushButton(f"{EmojiLib.ADD} Upload Chart Screenshot")
        upload_btn.clicked.connect(self.upload_image)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        upload_layout.addWidget(upload_btn)
        
        upload_frame.setLayout(upload_layout)
        left_layout.addWidget(upload_frame)
        
        # ✅ Progress Bar Section
        self.progress_frame = QFrame()
        self.progress_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #2196F3;
                border-radius: 8px;
                background-color: rgba(33, 150, 243, 0.1);
                padding: 10px;
            }
        """)
        self.progress_frame.setVisible(False)  # Hidden by default
        
        progress_layout = QVBoxLayout()
        self.progress_label = QLabel("🔄 Processing...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-weight: bold; color: #2196F3; font-size: 14px; border: none;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                background-color: #1e1e1e;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_frame.setLayout(progress_layout)
        left_layout.addWidget(self.progress_frame)
        
        # Manual input fields
        left_layout.addWidget(QLabel("Manual Inputs:"))

        
        # Margin/Leverage field
        margin_layout = QHBoxLayout()
        self.margin_label = QLabel("💰 Margin")
        self.margin_entry = QLineEdit()
        self.margin_entry.setPlaceholderText("Enter margin amount")
        margin_layout.addWidget(self.margin_label)
        margin_layout.addWidget(self.margin_entry)
        left_layout.addLayout(margin_layout)
        
        # Risk amount
        risk_layout = QHBoxLayout()
        self.risk_entry = QLineEdit()
        self.risk_entry.setPlaceholderText("Enter risk amount")
        risk_layout.addWidget(QLabel("⚠️ Risk Amount"))
        risk_layout.addWidget(self.risk_entry)
        left_layout.addLayout(risk_layout)
        
        # Trade type
        trade_type_layout = QHBoxLayout()
        self.trade_type_dropdown = QComboBox()
        self.trade_type_dropdown.addItems(["IDEA", "SIGNAL", "STRATEGY"])
        trade_type_layout.addWidget(QLabel("📋 Trade Type"))
        trade_type_layout.addWidget(self.trade_type_dropdown)
        left_layout.addLayout(trade_type_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        calculate_btn = QPushButton(f"{EmojiLib.CHART} Calculate")
        calculate_btn.clicked.connect(self.analyze_chart)
        calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px 20px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        add_record_btn = QPushButton(f"{EmojiLib.ADD} Add Record")
        add_record_btn.clicked.connect(self.add_to_journal)
        
        button_layout.addWidget(calculate_btn)
        button_layout.addWidget(add_record_btn)
        left_layout.addLayout(button_layout)
        
        left_layout.addStretch()
        
        # Right Panel - Output Section (Split vertically)
        right_splitter = QSplitter(Qt.Vertical)
        
        # Top section - Results
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_layout.addWidget(QLabel("📊 Calculation Results"))
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)
        results_layout.addWidget(self.results_text)
        results_widget.setLayout(results_layout)
        
        # Bottom section - AI Detection Log
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("🤖 AI Detection Log"))
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        log_layout.addWidget(self.log_text)
        log_widget.setLayout(log_layout)
        
        right_splitter.addWidget(results_widget)
        right_splitter.addWidget(log_widget)
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 2)
        
        # Output buttons
        output_btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton(f"{EmojiLib.SAVE} Copy Output")
        copy_btn.clicked.connect(self.copy_output)
        
        # ✅ NEW: Send to Calculator button
        send_calc_btn = QPushButton("📊 Send to Calculator")
        send_calc_btn.clicked.connect(self.send_to_calculator)
        send_calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 15px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        clear_btn = QPushButton(f"{EmojiLib.DELETE} Clear")
        clear_btn.clicked.connect(self.clear_all)
        clear_btn.setProperty("class", "danger")
        
        output_btn_layout.addWidget(send_calc_btn)
        output_btn_layout.addWidget(copy_btn)
        output_btn_layout.addWidget(clear_btn)

        
        # Combine right panel
        right_layout = QVBoxLayout()
        right_layout.addWidget(right_splitter)
        right_layout.addLayout(output_btn_layout)
        
        # Add to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)
    
    def switch_calculator(self, calculator_type):
        """Switch between calculator types"""
        self.current_calculator = calculator_type
        if calculator_type == "Leverage Calculator":
            self.margin_label.setText("💰 Margin")
            self.margin_entry.setPlaceholderText("Enter margin amount")
        else:
            self.margin_label.setText("🌊 Leverage")
            self.margin_entry.setPlaceholderText("Enter leverage (e.g., 10)")
    
    def upload_image(self):
        """Upload and preview chart image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TradingView Chart Screenshot",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*.*)"
        )
        
        if file_path:
            self.current_image_path = file_path
            
            # Display preview
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
            self.add_log(f"✅ Image loaded: {os.path.basename(file_path)}")
    
    def analyze_chart(self):
        """Analyze chart using Gemini API"""
        # Check if image is uploaded
        if not self.current_image_path:
            QMessageBox.warning(self, "No Image", "Please upload a chart image first!")
            return
        
        # Get API key from profile
        from api_key_manager import APIKeyManager
        api_manager = APIKeyManager()
        api_key = api_manager.get_api_key(self.main_app.profile_id)
        
        if not api_key:
            QMessageBox.warning(
                self,
                "Missing API Key",
                "⚠️ No Gemini API key configured for this profile!\n\n"
                "Please go to Settings → API Keys to configure your key."
            )
            return
        
        # ✅ Show progress and disable entire application
        self.progress_frame.setVisible(True)
        self.progress_label.setText("🔄 Analyzing chart with AI...")
        self.disable_all_controls(True)
        QApplication.processEvents()  # Force UI update
        
        # Start analysis
        self.add_log("🔄 Starting AI analysis...")
        self.add_log(f"📷 Analyzing image: {os.path.basename(self.current_image_path)}")
        self.add_log(f"🤖 Using model: gemini-flash-latest")


        
        # Create analysis prompt
        prompt = """
        Analyze this TradingView chart screenshot and extract the following trading information:
        
        1. Entry Price (the price level where the trade should be entered)
        2. Stop Loss Price (the price level for stop loss)
        3. Take Profit / Target Price (the price level for taking profit)
        4. Position Type (LONG or SHORT)
        
        Look for annotations, lines, text labels, or arrows that indicate these levels.
        Provide the exact numerical values if visible.
        
        Format your response clearly with:
        - Entry: [price]
        - Stop Loss: [price]
        - Take Profit: [price]
        - Position: [LONG or SHORT]
        """
        
        # Run in background thread
        self.analyzer_thread = GeminiAnalyzerThread(api_key, self.current_image_path, prompt)
        self.analyzer_thread.analysis_complete.connect(self.handle_analysis_result)
        self.analyzer_thread.analysis_error.connect(self.handle_analysis_error)
        self.analyzer_thread.start()
    
    def handle_analysis_result(self, result):
        """Handle successful analysis"""
        # ✅ Hide progress and re-enable UI
        self.progress_frame.setVisible(False)
        self.disable_all_controls(False)
        
        # ✅ Store result for later use
        self.last_ai_result = result
        
        self.add_log(f"✅ Analysis complete! Confidence: {result['confidence']}")


        self.add_log("─" * 50)
        
        # Display detected values
        if result['detected_values']:
            for value in result['detected_values']:
                self.add_log(f"  ✓ {value}")
        else:
            self.add_log("  ⚠️ No clear values detected")
        
        self.add_log("─" * 50)
        self.add_log(f"📝 Raw AI Response:\n{result['raw_response'][:500]}...")
        
        # Calculate if we have enough data
        if result['entry_price'] and result['stop_loss'] and result['take_profit']:
            self.perform_calculation(result)
        else:
            QMessageBox.information(
                self,
                "Manual Input Required",
                "AI could not detect all values automatically.\n"
                "Please verify and input missing values manually."
            )
    
    def handle_analysis_error(self, error_msg):
        """Handle analysis error"""
        # ✅ Hide progress and re-enable UI
        self.progress_frame.setVisible(False)
        self.disable_all_controls(False)
        
        self.add_log(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Analysis Error", f"Failed to analyze chart:\n{error_msg}")

    
    def perform_calculation(self, ai_result):
        """Perform trading calculations with AI-detected values"""
        try:
            entry_price = ai_result['entry_price']
            stop_loss = ai_result['stop_loss']
            take_profit = ai_result['take_profit']
            position = ai_result['position_type'] or 'LONG'
            
            # Validate AI-detected values
            if not entry_price or not stop_loss or not take_profit:
                raise ValueError("Missing required values. Please input manually.")
            
            if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
                raise ValueError("Invalid price values detected (all must be > 0)")
            
            if entry_price == stop_loss:
                raise ValueError(f"Entry price ({entry_price:,.2f}) equals stop loss. Cannot calculate.")
            
            # Get manual inputs
            margin_text = self.margin_entry.text().strip()
            risk_text = self.risk_entry.text().strip()
            
            if not margin_text or not risk_text:
                raise ValueError("Please enter Margin and Risk Amount manually")
            
            margin = float(margin_text)
            risk = float(risk_text)
            trade_type = self.trade_type_dropdown.currentText()
            
            if margin <= 0 or risk <= 0:
                raise ValueError("Margin and Risk Amount must be greater than 0")
            
            # Calculate percentages
            if position == 'LONG':
                sl_percent = ((entry_price - stop_loss) / entry_price) * 100
                tp_percent = ((take_profit - entry_price) / entry_price) * 100
            else:
                sl_percent = ((stop_loss - entry_price) / entry_price) * 100
                tp_percent = ((entry_price - take_profit) / entry_price) * 100
            
            # Additional validation
            if abs(sl_percent) < 0.001:
                raise ValueError(f"Stop loss too close to entry (< 0.001%). SL: {stop_loss:,.2f}, Entry: {entry_price:,.2f}")

            
            # Calculate leverage/margin based on calculator type
            if self.current_calculator == "Margin Calculator":
                leverage = margin  # User entered leverage
                calculated_margin = (risk * 100) / (leverage * abs(sl_percent))
            else:
                leverage = (risk / margin) * (100 / abs(sl_percent))
                calculated_margin = margin
            
            # Display results
            position_emoji = "🟢" if position == 'LONG' else "🔴"
            trade_emoji = "💡" if trade_type == "IDEA" else "📡" if trade_type == "SIGNAL" else "🎯"
            
            output = f"""
{position_emoji} Position: {position}
{trade_emoji} Trade Type: {trade_type}

📍 Entry: {entry_price:.6f}
🌊 Leverage: {leverage:.2f}x
🎯 Target: {take_profit:.6f} (+{tp_percent:.2f}%)
🛑 StopLoss: {stop_loss:.6f} (-{abs(sl_percent):.2f}%)

💰 Margin: ${calculated_margin:.2f}
⚠️ Risk Amount: ${risk:.2f}

🤖 AI Confidence: {ai_result['confidence']}
            """
            
            self.results_text.setText(output)
            self.add_log("✅ Calculation complete!")
            
        except Exception as e:
            self.add_log(f"❌ Calculation error: {str(e)}")
            QMessageBox.warning(self, "Calculation Error", str(e))
    
    def add_log(self, message):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def copy_output(self):
        """Copy results to clipboard"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.results_text.toPlainText())
        self.add_log("📋 Output copied to clipboard")
    
    def clear_all(self):
        """Clear all inputs and outputs"""
        self.current_image_path = None
        self.image_label.clear()
        self.image_label.setText("📸 No image uploaded")
        self.margin_entry.clear()
        self.risk_entry.clear()
        self.results_text.clear()
        self.log_text.clear()
        self.add_log("🗑️ All fields cleared")
    
    def add_to_journal(self):
        """Redirect to journal tab with calculated values"""
        if not self.results_text.toPlainText():
            QMessageBox.warning(self, "No Data", "Please calculate first before adding to journal!")
            return
        
        if not hasattr(self, 'last_ai_result') or not self.last_ai_result:
            QMessageBox.warning(self, "No Data", "Please analyze and calculate first!")
            return
        
        try:
            result = self.last_ai_result
            
            # Get values from AI result
            entry_price = result.get('entry_price')
            stop_loss = result.get('stop_loss')
            take_profit = result.get('take_profit')
            position = result.get('position_type', 'LONG')
            
            # Get manual inputs
            margin = float(self.margin_entry.text() or 0)
            risk = float(self.risk_entry.text() or 0)
            trade_type = self.trade_type_dropdown.currentText()
            
            # Calculate percentages
            if position == 'LONG':
                sl_percent = ((entry_price - stop_loss) / entry_price) * 100
                tp_percent = ((take_profit - entry_price) / entry_price) * 100
            else:
                sl_percent = ((stop_loss - entry_price) / entry_price) * 100
                tp_percent = ((entry_price - take_profit) / entry_price) * 100
            
            # Calculate leverage/margin based on calculator type
            if self.current_calculator == "Margin Calculator":
                leverage = margin  # User entered leverage
                calculated_margin = (risk * 100) / (leverage * abs(sl_percent))
                trade_size = calculated_margin
            else:
                leverage = (risk / margin) * (100 / abs(sl_percent))
                trade_size = margin
            
            # Get pair name from image filename or default
            pair = "BTC/USDT"
            if self.current_image_path:
                filename = os.path.basename(self.current_image_path)
                if 'BTC' in filename.upper():
                    pair = "BTC/USDT"
                elif 'ETH' in filename.upper():
                    pair = "ETH/USDT"
            
            self.add_log("➡️ Redirecting to Journal tab...")
            
            # Redirect to journal
            journal_tab = self.main_app.journal_tab
            
            # Fill in the values
            journal_tab.pair_entry.setText(pair)
            
            # Set position (convert LONG/SHORT to Long Position/Short Position)
            if position == 'LONG':
                journal_tab.position_dropdown.setCurrentText('Long Position')
            else:
                journal_tab.position_dropdown.setCurrentText('Short Position')
            
            # Set trade type
            journal_tab.trade_type_dropdown.setCurrentText(trade_type)
            journal_tab.trade_type_dropdown.setVisible(True)
            
            # Set percentages and trade size
            journal_tab.tp_entry.setText(f"{tp_percent:.2f}")
            journal_tab.sl_entry.setText(f"{abs(sl_percent):.2f}")
            journal_tab.trade_size_entry.setText(f"{trade_size:.2f}")
            
            # Set leverage if using Margin Calculator
            if self.current_calculator == "Margin Calculator":
                journal_tab.leverage_entry.setText(f"{leverage:.2f}")
            
            # Switch to Journal tab
            self.main_app.tabs.setCurrentWidget(journal_tab)
            
            self.add_log("✅ Successfully redirected to Journal tab")
            
        except Exception as e:
            self.add_log(f"❌ Redirect error: {str(e)}")
            QMessageBox.warning(self, "Redirect Error", f"Failed to redirect:\n{str(e)}")


    def disable_all_controls(self, disabled):
        """Disable or enable all controls during processing"""
        # Disable buttons in AI tab
        for widget in self.findChildren(QPushButton):
            widget.setDisabled(disabled)
        
        # Disable input fields
        for widget in self.findChildren(QLineEdit):
            widget.setDisabled(disabled)
        
        for widget in self.findChildren(QComboBox):
            widget.setDisabled(disabled)
        
        # Disable main app tabs during processing
        if hasattr(self.main_app, 'tabs'):
            self.main_app.tabs.setTabEnabled(0, not disabled)  # Dashboard
            self.main_app.tabs.setTabEnabled(1, not disabled)  # Calculator
            self.main_app.tabs.setTabEnabled(2, not disabled)  # Journal
            self.main_app.tabs.setTabEnabled(3, not disabled)  # Trades
        
        # Disable toolbar buttons
        if hasattr(self.main_app, 'theme_toggle_btn'):
            self.main_app.theme_toggle_btn.setDisabled(disabled)

    def send_to_calculator(self):
        """Send AI-detected values to Calculator tab"""
        if not hasattr(self, 'last_ai_result') or not self.last_ai_result:
            QMessageBox.warning(self, "No Data", "Please analyze a chart first!")
            return
        
        result = self.last_ai_result
        
        # Check if we have the required values
        if not result.get('entry_price') or not result.get('stop_loss') or not result.get('take_profit'):
            QMessageBox.warning(
                self,
                "Incomplete Data",
                "Missing required values. Please ensure Entry, Stop Loss, and Take Profit are detected."
            )
            return
        
        try:
            calculator_tab = self.main_app.alert_tab
            
            # Fill detected values
            calculator_tab.entry_price_entry.setText(f"{result['entry_price']:.6f}")
            calculator_tab.stop_loss_entry.setText(f"{result['stop_loss']:.6f}")
            calculator_tab.take_profit_entry.setText(f"{result['take_profit']:.6f}")
            
            # Set position
            if result.get('position_type'):
                calculator_tab.position_dropdown.setCurrentText(result['position_type'])
            
            # Switch to Calculator tab
            self.main_app.tabs.setCurrentWidget(calculator_tab)
            
            self.add_log("✅ Values sent to Calculator tab")
            QMessageBox.information(
                self,
                "Success",
                f"AI-detected values sent to Calculator tab:\n\n"
                f"Entry: {result['entry_price']:,.2f}\n"
                f"Stop Loss: {result['stop_loss']:,.2f}\n"
                f"Take Profit: {result['take_profit']:,.2f}\n"
                f"Position: {result.get('position_type', 'LONG')}"
            )
            
        except Exception as e:
            self.add_log(f"❌ Error sending to calculator: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to send to calculator:\n{str(e)}")

