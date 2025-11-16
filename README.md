## 📘 Trading Journal (PyQt5)

A clean and efficient desktop trading journal built with Python + PyQt5 for cryptocurrency and stock traders.  
Supports multi-profile management, Excel-based trade tracking, real-time balance handling, calculators, and a web-based analytics dashboard.

---

## 🚀 Features

### 🔐 Multi-Profile System
- Password-protected profiles (SHA-256)
- Quick profile switching with verification
- Fully isolated data per profile:
  - trades.xlsx
  - screenshots folder
  - balance history
  - metrics
- Create / delete / clone / export profiles

### 💰 Balance Management
- Real-time balance updates
- Full balance audit log
- Deposit / Withdrawal tracking
- Balance reset
- Accurate handling of running vs closed trades

### 📝 Trade Journal
- Long/Short positions
- Position size, leverage, TP/SL
- Automatic Risk/Reward calculation
- Outcomes: Win / Loss / Break Even
- Automatic PnL calculation
- Entry & exit screenshots
- Notes for trades

### 🧮 Trade Calculator
- Leverage calculator
- Margin calculator
- Automatic R/R ratio
- One-click journal entry

### 📈 Dashboard
- Win rate, total trades, wins/losses
- Profit factor, average PnL %
- Biggest win/loss
- Cumulative PnL curve
- Real-time updates

### 📊 Matrix Analytics (Web Dashboard)
- Flask-powered analytics interface
- 50+ trading metrics
- Interactive PnL chart
- Time filters (All / 7D / 30D)
- Exportable metrics report

### 🎨 Themes
- Dark mode / Light mode
- One-click toggle
- Saves user preference

---

## 📂 Project Structure

project/  
│── journal.py  
│── profiles.json  
│── theme_settings.json  
│── profiles/  
│     └── profile_X/  
│           ├── trades.xlsx  
│           ├── screenshots/  
│           └── balance_history.json  
│── requirements.txt  
└── README.md  

---

## 📦 Installation

### Option 1 — Run from Source
git clone https://github.com/yourusername/trading-journal.git

cd trading-journal
pip install -r requirements.txt
python journal.py


### Option 2 — Windows Executable
- Download **TradeJournal.exe** from Releases
- Default login:
  - username: admin
  - password: admin

---

## 🖥️ Usage

### First Launch
1. Login with default credentials  
2. Create your own profile  
3. Begin journaling trades  

### Adding a Trade
- Use **Calculator** → Add Record  
- Or add directly using the **Journal** tab  

### Closing a Trade
1. Open **Trades** tab  
2. Double-click a running trade  
3. Set status to Closed  
4. Select outcome → Save  

### Viewing Analytics
- Click **Matrix** on Dashboard  
- Browser opens analytics page  
- Apply filters (All, 7D, 30D)

### Switching Profiles
- Click the 🔄 icon  
- Select profile  
- Enter password  

---

## 🐛 Known Issues
- Matrix dashboard uses rotating ports (5001–5010)
- Opening multiple Matrix windows rapidly may conflict
- Excel file must be closed while saving trades

---

## 🔮 Future Enhancements
- Profile avatars  
- Profile import  
- Cloud sync  
- Advanced charting  
- Exchange API integrations  
- Mobile app  
- Profile comparison analytics  

---

## 🧾 Requirements
- Windows 10/11, macOS 10.14+, Linux  
- Python 3.7+  
- 4GB RAM (8GB recommended)  
- ~100MB storage + trade data  

---

## 👤 Author
**Sanjeewan**  
GitHub: https://github.com/sanjeewan24  

Made with ❤️ for traders.

