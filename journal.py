import sys
import os
import shutil
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QComboBox, QTextEdit, QPushButton, QFileDialog, QTabWidget,
                             QListWidget, QMessageBox, QInputDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDate
import pandas as pd
import datetime

class TradeJournalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.account_balance = 5000
        self.screenshot_folder = 'screenshots'
        if not os.path.exists(self.screenshot_folder):
            os.makedirs(self.screenshot_folder)
        self.initUI()
        self.load_data()
        self.current_trade_index = None
        self.screenshot_counter = self.get_screenshot_counter()

    def get_screenshot_counter(self):
        return len([f for f in os.listdir(self.screenshot_folder) if f.endswith('.png')])

    def initUI(self):
        self.setWindowTitle('Trade Journal')
        self.setGeometry(100, 100, 800, 600)
        self.tabs = QTabWidget()
        self.journal_tab = QWidget()
        self.trades_tab = QWidget()
        self.tabs.addTab(self.journal_tab, 'Journal')
        self.tabs.addTab(self.trades_tab, 'Trades')
        self.init_journal_tab()
        self.init_trades_tab()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def init_journal_tab(self):
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        middle_layout = QHBoxLayout()

        # Trade Time and Session, Sweep, CISD Dropdowns
        self.time_entry = QLineEdit(self)
        self.time_entry.setReadOnly(True)
        self.time_entry.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.time_entry.setFixedWidth(150)
        top_layout.addWidget(QLabel('Trade Time:'))
        top_layout.addWidget(self.time_entry)

        self.session_dropdown = QComboBox(self)
        self.session_dropdown.addItems(['(none)', 'London', 'New York'])
        self.session_dropdown.setFixedWidth(150)
        top_layout.addWidget(QLabel('Session:'))
        top_layout.addWidget(self.session_dropdown)

        self.sweep_dropdown = QComboBox(self)
        self.sweep_dropdown.addItems(['(none)', 'PWH', 'PWL', 'PDH', 'PDL', '4H Low', '4H High', '1H Low', '1H High','Asian high', 'Asian Low', 'London high','London low','NY high','NY low'])
        self.sweep_dropdown.setFixedWidth(150)
        top_layout.addWidget(QLabel('Sweep:'))
        top_layout.addWidget(self.sweep_dropdown)

        self.cisd_dropdown = QComboBox(self)
        self.cisd_dropdown.addItems(['(none)', 'Confirmed', 'Not Confirmed'])
        self.cisd_dropdown.setFixedWidth(150)
        top_layout.addWidget(QLabel('CISD:'))
        top_layout.addWidget(self.cisd_dropdown)

        # Cryptocurrency Pair and Position Type
        self.pair_dropdown = QComboBox(self)
        self.pair_dropdown.addItems(['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT'])
        self.pair_dropdown.setFixedWidth(150)
        middle_layout.addWidget(QLabel('Cryptocurrency Pair:'))
        middle_layout.addWidget(self.pair_dropdown)

        self.position_dropdown = QComboBox(self)
        self.position_dropdown.addItems(['Long Position', 'Short Position'])
        self.position_dropdown.setFixedWidth(150)
        middle_layout.addWidget(QLabel('Position Type:'))
        middle_layout.addWidget(self.position_dropdown)

        # Notes Section
        self.notes_entry = QTextEdit(self)
        layout.addLayout(top_layout)
        layout.addLayout(middle_layout)
        layout.addWidget(QLabel('Notes:'))
        layout.addWidget(self.notes_entry)

        # Connect dropdown signals to update notes
        self.session_dropdown.currentTextChanged.connect(self.update_notes)
        self.sweep_dropdown.currentTextChanged.connect(self.update_notes)
        self.cisd_dropdown.currentTextChanged.connect(self.update_notes)

        # Upload Screenshot Button
        self.upload_btn1 = QPushButton('Upload Screenshot 1', self)
        self.upload_btn1.clicked.connect(lambda: self.upload_screenshot(1))
        layout.addWidget(self.upload_btn1)

        # Trade Size and Leverage
        size_leverage_layout = QHBoxLayout()
        self.trade_size_entry = QLineEdit(self)
        self.leverage_entry = QLineEdit(self)
        size_leverage_layout.addWidget(QLabel('Trade Size:'))
        size_leverage_layout.addWidget(self.trade_size_entry)
        size_leverage_layout.addWidget(QLabel('Leverage:'))
        size_leverage_layout.addWidget(self.leverage_entry)
        layout.addLayout(size_leverage_layout)

        # Take Profit and Stop Loss
        tp_sl_layout = QHBoxLayout()
        self.tp_entry = QLineEdit(self)
        self.sl_entry = QLineEdit(self)
        tp_sl_layout.addWidget(QLabel('Take Profit %:'))
        tp_sl_layout.addWidget(self.tp_entry)
        tp_sl_layout.addWidget(QLabel('Stop Loss %:'))
        tp_sl_layout.addWidget(self.sl_entry)
        layout.addLayout(tp_sl_layout)

        # Take Profit Amount, Stop Loss Amount, and Risk/Reward Ratio
        self.tp_amount_entry = QLineEdit(self)
        self.sl_amount_entry = QLineEdit(self)
        self.rr_ratio_entry = QLineEdit(self)
        tp_sl_amount_layout = QHBoxLayout()
        tp_sl_amount_layout.addWidget(QLabel('Take Profit Amount:'))
        tp_sl_amount_layout.addWidget(self.tp_amount_entry)
        tp_sl_amount_layout.addWidget(QLabel('Stop Loss Amount:'))
        tp_sl_amount_layout.addWidget(self.sl_amount_entry)
        tp_sl_amount_layout.addWidget(QLabel('Risk/Reward Ratio:'))
        tp_sl_amount_layout.addWidget(self.rr_ratio_entry)
        layout.addLayout(tp_sl_amount_layout)

        # Status Dropdown
        self.status_dropdown = QComboBox(self)
        self.status_dropdown.addItems(['Running', 'Closed'])
        self.status_dropdown.currentIndexChanged.connect(self.status_changed)
        layout.addWidget(QLabel('Status:'))
        layout.addWidget(self.status_dropdown)

        # Hidden Widget for Closed Trades
        self.hidden_widget = QWidget()
        self.hidden_layout = QVBoxLayout(self.hidden_widget)
        self.outcome_dropdown = QComboBox(self)
        self.outcome_dropdown.addItems(['Break Even', 'Win', 'Loss'])
        self.outcome_dropdown.currentIndexChanged.connect(self.calculate_pnl)
        self.hidden_layout.addWidget(QLabel('Outcome:'))
        self.hidden_layout.addWidget(self.outcome_dropdown)
        self.pnl_entry = QLineEdit(self)
        self.pnl_percent_entry = QLineEdit(self)
        self.hidden_layout.addWidget(QLabel('PnL:'))
        self.hidden_layout.addWidget(self.pnl_entry)
        self.hidden_layout.addWidget(QLabel('PnL %:'))
        self.hidden_layout.addWidget(self.pnl_percent_entry)
        self.upload_btn2 = QPushButton('Upload Screenshot 2', self)
        self.upload_btn2.clicked.connect(lambda: self.upload_screenshot(2))
        self.hidden_layout.addWidget(self.upload_btn2)
        self.closed_notes_entry = QTextEdit(self)
        self.hidden_layout.addWidget(QLabel('Notes:'))
        self.hidden_layout.addWidget(self.closed_notes_entry)
        layout.addWidget(self.hidden_widget)
        self.hidden_widget.setVisible(False)

        # Buttons for Reset, Add Trade, Update Trade, and Edit Capital
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

        # Right Section for Screenshots
        right_layout = QVBoxLayout()
        self.screenshot1_label = QLabel(self)
        self.screenshot1_label.setFixedSize(400, 200)
        self.screenshot1_label.setStyleSheet("border: 1px solid black;")
        right_layout.addWidget(self.screenshot1_label)
        self.screenshot2_label = QLabel(self)
        self.screenshot2_label.setFixedSize(400, 200)
        self.screenshot2_label.setStyleSheet("border: 1px solid black;")
        right_layout.addWidget(self.screenshot2_label)

        main_journal_layout = QHBoxLayout()
        main_journal_layout.addLayout(layout)
        main_journal_layout.addLayout(right_layout)
        self.journal_tab.setLayout(main_journal_layout)

        # Connect signals for real-time calculations
        self.trade_size_entry.textChanged.connect(self.calculate_amounts)
        self.leverage_entry.textChanged.connect(self.calculate_amounts)
        self.tp_entry.textChanged.connect(self.calculate_amounts)
        self.sl_entry.textChanged.connect(self.calculate_amounts)

    def update_notes(self):
        session = self.session_dropdown.currentText()
        sweep = self.sweep_dropdown.currentText()
        cisd = self.cisd_dropdown.currentText()

        notes = []
        if session != '(none)':
            notes.append(f"Session: {session}")
        if sweep != '(none)':
            notes.append(f"Sweep: {sweep}")
        if cisd != '(none)':
            notes.append(f"CISD: {cisd}")

        if any(dropdown.currentText() == '(none)' for dropdown in [self.session_dropdown, self.sweep_dropdown, self.cisd_dropdown]):
            grade = "A"
        else:
            grade = "A+"

        notes.append(f"Grade: {grade}")
        self.notes_entry.setPlainText("\n".join(notes))

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

    def load_data(self):
        if os.path.exists('trades.xlsx'):
            self.df = pd.read_excel('trades.xlsx', dtype={'Screenshot1': str, 'Screenshot2': str})
            self.populate_trades()
        else:
            self.df = pd.DataFrame(columns=[
                'Time', 'Pair', 'Notes', 'Screenshot1', 'Screenshot2', 'Trade Size', 'Leverage',
                'Take Profit %', 'Stop Loss %', 'Take Profit Amount', 'Stop Loss Amount',
                'Risk/Reward Ratio', 'Status', 'Outcome', 'PnL', 'PnL %', 'Closed Notes', 'Position Type'
            ])

    def populate_trades(self):
        running_trades = self.df[self.df['Status'] == 'Running']
        closed_trades = self.df[self.df['Status'] == 'Closed']
        self.running_trades_list.clear()
        self.closed_trades_list.clear()
        for index, row in running_trades.iterrows():
            self.running_trades_list.addItem(f"{row['Time']} - {row['Pair']}")
        for index, row in closed_trades.iterrows():
            self.closed_trades_list.addItem(f"{row['Time']} - {row['Pair']}")

    def upload_screenshot(self, screenshot_num):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload Screenshot", "", "Images (*.png *.xpm *.jpg *.jpeg)", options=options)
        if file_name:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
            new_file_name = f"{date_str}_{self.screenshot_counter + 1}.png"
            new_file_path = os.path.join(self.screenshot_folder, new_file_name)
            shutil.copy(file_name, new_file_path)
            if screenshot_num == 1:
                self.screenshot1_path = new_file_path
                pixmap = QPixmap(new_file_path).scaled(self.screenshot1_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.screenshot1_label.setPixmap(pixmap)
                self.screenshot_counter += 1
            elif screenshot_num == 2:
                self.screenshot2_path = new_file_path
                pixmap = QPixmap(new_file_path).scaled(self.screenshot2_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.screenshot2_label.setPixmap(pixmap)
                self.screenshot_counter += 1

    def status_changed(self, index):
        if self.status_dropdown.currentText() == 'Closed':
            self.hidden_widget.setVisible(True)
        else:
            self.hidden_widget.setVisible(False)

    def reset_fields(self):
        self.time_entry.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.pair_dropdown.setCurrentIndex(0)
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
        self.session_dropdown.setCurrentIndex(0)
        self.sweep_dropdown.setCurrentIndex(0)
        self.cisd_dropdown.setCurrentIndex(0)

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
        except ValueError:
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
        except ValueError:
            self.pnl_entry.clear()
            self.pnl_percent_entry.clear()

    def add_trade(self):
        trade_data = {
            'Time': self.time_entry.text(),
            'Pair': self.pair_dropdown.currentText(),
            'Notes': self.notes_entry.toPlainText(),
            'Screenshot1': getattr(self, 'screenshot1_path', ''),
            'Screenshot2': getattr(self, 'screenshot2_path', ''),
            'Trade Size': float(self.trade_size_entry.text()),
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
        self.account_balance -= trade_data['Trade Size']
        self.df = pd.concat([self.df, pd.DataFrame([trade_data])], ignore_index=True)
        self.df.to_excel('trades.xlsx', index=False)
        self.populate_trades()
        self.reset_fields()
        self.account_balance_label.setText(f"Account Balance: ${self.account_balance:.2f}")

    def update_trade(self):
        if self.current_trade_index is not None:
            trade_data = {
                'Time': self.time_entry.text(),
                'Pair': self.pair_dropdown.currentText(),
                'Notes': self.notes_entry.toPlainText(),
                'Screenshot1': getattr(self, 'screenshot1_path', ''),
                'Screenshot2': getattr(self, 'screenshot2_path', ''),
                'Trade Size': float(self.trade_size_entry.text()),
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
            if self.df.at[self.current_trade_index, 'Status'] == 'Running':
                self.account_balance += self.df.at[self.current_trade_index, 'Trade Size']
            if trade_data['Status'] == 'Closed':
                self.account_balance += trade_data['Trade Size'] + float(trade_data['PnL'])
            for key, value in trade_data.items():
                self.df.at[self.current_trade_index, key] = value
            self.df.to_excel('trades.xlsx', index=False)
            self.populate_trades()
            self.reset_fields()
            self.account_balance_label.setText(f"Account Balance: ${self.account_balance:.2f}")

    def load_trade(self, item):
        self.tabs.setCurrentWidget(self.journal_tab)
        time, pair = item.text().split(' - ')
        trade = self.df[(self.df['Time'] == time) & (self.df['Pair'] == pair)]
        if not trade.empty:
            self.current_trade_index = trade.index[0]
            trade = trade.iloc[0]
            self.time_entry.setText(trade['Time'])
            self.pair_dropdown.setCurrentText(trade['Pair'])
            self.notes_entry.setPlainText(trade['Notes'])
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
                self.closed_notes_entry.setPlainText(trade['Closed Notes'])
            else:
                self.hidden_widget.setVisible(False)

    def delete_trade(self):
        selected_items = self.running_trades_list.selectedItems() + self.closed_trades_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            time, pair = item.text().split(' - ')
            trade = self.df[(self.df['Time'] == time) & (self.df['Pair'] == pair)]
            if not trade.empty:
                self.df = self.df.drop(trade.index)
                self.df.to_excel('trades.xlsx', index=False)
                self.populate_trades()

    def filter_trades(self, index):
        filter_option = self.filter_dropdown.currentText()
        today = QDate.currentDate()
        if filter_option == 'Today':
            filtered_df = self.df[self.df['Time'].apply(lambda x: QDate.fromString(x, 'yyyy-MM-dd').daysTo(today) == 0)]
        elif filter_option == 'Last 7 Days':
            filtered_df = self.df[self.df['Time'].apply(lambda x: QDate.fromString(x, 'yyyy-MM-dd').daysTo(today) <= 7)]
        elif filter_option == 'Last 30 Days':
            filtered_df = self.df[self.df['Time'].apply(lambda x: QDate.fromString(x, 'yyyy-MM-dd').daysTo(today) <= 30)]
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

    def edit_capital(self):
        new_balance, ok = QInputDialog.getDouble(self, "Edit Capital", "Enter new account balance:", self.account_balance, 0, 1e9, 2)
        if ok:
            self.account_balance = new_balance
            self.account_balance_label.setText(f"Account Balance: ${self.account_balance:.2f}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TradeJournalApp()
    ex.show()
    sys.exit(app.exec_())
