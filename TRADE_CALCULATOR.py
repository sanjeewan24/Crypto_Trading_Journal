import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QHBoxLayout

class CalculatorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.history = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.calculator_type = QComboBox(self)
        self.calculator_type.addItem("Select Calculator")
        self.calculator_type.addItem("Margin Calculator")
        self.calculator_type.addItem("Leverage Calculator")
        layout.addWidget(self.calculator_type)

        self.trading_pair = QComboBox(self)
        self.trading_pair.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT", "ADA/USDT"])
        layout.addWidget(self.trading_pair)

        self.input_labels = [QLabel("Leverage:"), QLabel("Lose:"), QLabel("Price Movement:"),
                             QLabel("Fixed Stop Loss Amount:"), QLabel("Margin:")]
        self.input_fields = [QLineEdit(self) for _ in range(5)]

        for label, field in zip(self.input_labels, self.input_fields):
            layout.addWidget(label)
            layout.addWidget(field)
            label.hide()
            field.hide()

        self.calculate_button = QPushButton('Calculate', self)
        self.calculate_button.clicked.connect(self.calculate)
        layout.addWidget(self.calculate_button)

        self.result_label = QLabel('Result:', self)
        layout.addWidget(self.result_label)
        self.result_label.hide()

        self.result_text = QTextEdit(self)
        layout.addWidget(self.result_text)
        self.result_text.hide()

        history_layout = QHBoxLayout()
        self.history_label = QLabel('History:', self)
        history_layout.addWidget(self.history_label)

        self.history_text = QTextEdit(self)
        self.history_text.setReadOnly(True)
        history_layout.addWidget(self.history_text)

        layout.addLayout(history_layout)
        self.history_label.hide()
        self.history_text.hide()

        self.calculator_type.currentIndexChanged.connect(self.update_inputs)

        self.setLayout(layout)
        self.setWindowTitle('Calculator App')
        self.show()

    def update_inputs(self):
        current_calculator = self.calculator_type.currentText()

        for label, field in zip(self.input_labels, self.input_fields):
            label.hide()
            field.hide()
            field.clear()

        self.result_label.hide()
        self.result_text.hide()

        if current_calculator == "Margin Calculator":
            for i in range(3):
                self.input_labels[i].show()
                self.input_fields[i].show()
        elif current_calculator == "Leverage Calculator":
            for i in range(2, 5):  # Show Price Movement, Fixed Stop Loss Amount, Margin
                self.input_labels[i].show()
                self.input_fields[i].show()


    def calculate(self):
        current_calculator = self.calculator_type.currentText()
        selected_pair = self.trading_pair.currentText()

        if current_calculator == "Margin Calculator":
            try:
                leverage = float(self.input_fields[0].text())
                lose = float(self.input_fields[1].text())
                movement = float(self.input_fields[2].text())
                margin = (lose * 100) / (leverage * movement)
                result_text = f"Margin --> ${margin:.2f}"
            except ValueError:
                result_text = "Invalid input. Please enter numeric values."

        elif current_calculator == "Leverage Calculator":
            try:
                sl = float(self.input_fields[3].text())
                margin = float(self.input_fields[4].text())
                movement = float(self.input_fields[2].text())
                leverage = (-sl * 100) / (margin * (-movement))
                result_text = f"Leverage --> {leverage:.2f}x"
            except ValueError:
                result_text = "Invalid input. Please enter numeric values."

        else:
            result_text = "Please select a calculator."

        self.result_text.setPlainText(result_text)
        self.result_label.show()
        self.result_text.show()

        # Save to history with trading pair
        self.history.append(f"{selected_pair}: {result_text}")
        self.update_history()

    def update_history(self):
        self.history_label.show()
        self.history_text.show()
        self.history_text.setPlainText("\n\n".join(self.history))

def main():
    app = QApplication(sys.argv)
    ex = CalculatorApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
