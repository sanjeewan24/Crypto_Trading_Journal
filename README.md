# 📊 Crypto Trading Journal Pro v2.0.0

A professional cryptocurrency trading journal desktop application built with Python and PyQt5. Track, analyze, and improve your trading performance with advanced features including AI-powered chart analysis, multi-profile support, and comprehensive analytics.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)

<img width="1501" height="727" alt="Screenshot 2025-12-07 191621" src="https://github.com/user-attachments/assets/6c523519-9086-4a20-8430-f6e066a5f7a6" />

<img width="1502" height="877" alt="Screenshot 2025-12-07 191637" src="https://github.com/user-attachments/assets/30060cff-da50-40a3-afab-717ceb607e95" />

## ✨ Key Features

### 📝 Core Trading Journal
- **Trade Entry Management**: Record detailed trade information including entry/exit prices, position type (Long/Short), leverage, stop loss, and take profit levels
- **Screenshot Attachments**: Upload and store chart screenshots for each trade (before and after)
- **Automatic Calculations**: Auto-calculate TP/SL amounts, R:R ratios, and PnL percentages
- **Trade Status Tracking**: Monitor open and closed trades with outcome classification (Win/Loss/Break Even)

### 🤖 AI Chart Analyzer (NEW in v2.0.0)
- **Gemini AI Integration**: Analyze TradingView chart screenshots using Google's Gemini Flash model
- **Automatic Trade Parameter Detection**: Extract entry price, stop loss, take profit, and position type from chart images
- **Dual Calculator Modes**:
  - **Leverage Calculator**: Calculate position size and risk based on margin
  - **Margin Calculator**: Determine required margin based on leverage
- **Intelligent Parsing**: AI-powered detection of trading annotations and price levels
- **One-Click Transfer**: Send AI-analyzed data directly to your journal or calculator

### 👥 Multi-Profile System
- **Unlimited Profiles**: Create separate trading journals for different strategies or accounts
- **Profile Analytics**: View detailed statistics per profile including creation date, activity days, and balance history
- **Profile Switching**: Quick profile switching with automatic data isolation
- **Avatar Support**: Customize each profile with unique avatars

### 📈 Advanced Analytics Dashboard
- **Performance Metrics**: 50+ calculated trading metrics including:
  - Win rate, loss rate, profit factor
  - Risk/reward ratios, Kelly Criterion
  - Average returns on winners/losers
  - Consecutive win/loss streaks
  - System Quality Number (SQN)
- **Visual Charts**: Matplotlib-powered charts for equity curve and P&L visualization
- **Real-Time Updates**: Live calculation and display of all metrics

### 🌐 Web Matrix Dashboard
- **Flask-Based Server**: Access your trading statistics through a web browser
- **Responsive Design**: Beautiful, modern interface accessible from any device
- **Live Data**: Real-time metrics synchronized with your desktop app
- **Filter Options**: View data for all time, last 7 days, or last 30 days
- **One-Click Launch**: Start web server directly from the app on port 5001

### 🎨 Theme System
- **Dark & Light Modes**: Toggle between professional dark and light themes
- **Persistent Preferences**: Theme selection saved across sessions
- **Modern UI Design**: Clean, emoji-enhanced interface with smooth animations
- **Customizable Styling**: Professional color schemes and typography

### 🔑 API Key Management
- **Per-Profile Keys**: Store separate Gemini API keys for each profile
- **Secure Storage**: Encrypted key storage with password masking
- **Key Testing**: Built-in functionality to test API key validity before saving
- **Easy Configuration**: Intuitive dialog for managing API credentials

### 💾 Data Management
- **Excel-Based Storage**: All trades stored in `.xlsx` format for easy backup
- **Profile Isolation**: Each profile maintains its own `trades.xlsx` file
- **Settings Persistence**: JSON-based configuration for app settings
- **Auto-Save**: Automatic data persistence on every change

## 📋 Requirements

### Python Dependencies
```
PyQt5>=5.15.0
pandas>=2.0.0
openpyxl>=3.1.0
matplotlib>=3.7.0
Pillow>=10.0.0
google-generativeai>=0.3.0
Flask>=3.0.0
```

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python Version**: 3.8 or higher
- **RAM**: Minimum 4GB recommended
- **Storage**: ~50MB for application + space for trade data

### API Requirements
- **Gemini API Key** (optional): Required for AI Chart Analyzer feature
  - Free tier: 15 requests/minute, 250,000 tokens/minute
  - Get your key at [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/sanjeewan24/Crypto_Trading_Journal.git
cd Crypto_Trading_Journal
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python journal.py
```

## 📖 Usage Guide

### Getting Started

1. **Create a Profile**
   - Launch the app and go to the "Profile Manager" tab
   - Click "Create New Profile"
   - Set username, password, and initial balance
   - Optionally upload an avatar

2. **Configure API Key** (Optional for AI features)
   - Go to Settings → API Keys
   - Select your profile
   - Enter your Gemini API key
   - Click "Test Key" to verify
   - Save the key

3. **Record Your First Trade**
   - Switch to the "Journal" tab
   - Fill in trade details (pair, position type, entry price, etc.)
   - Upload chart screenshots if desired
   - Click "Add Trade" to save

### Using AI Chart Analyzer

1. **Upload Chart Screenshot**
   - Navigate to "AI Chart Analyzer" tab
   - Click "Upload Chart Screenshot"
   - Select your TradingView chart image

2. **Analyze Chart**
   - Click "Calculate" to start AI analysis
   - Wait for Gemini to process the image (~5-15 seconds)
   - Review detected values in the AI Detection Log

3. **Transfer to Journal**
   - Click "Send to Calculator" to populate fields
   - Or click "Add Record" to create journal entry directly
   - Verify AI-detected values before saving

### Viewing Analytics

1. **Dashboard Tab**
   - View comprehensive statistics for current profile
   - See equity curve and P&L charts
   - Monitor key performance indicators

2. **Web Matrix Dashboard**
   - Click "Open Matrix Dashboard" in the Dashboard tab
   - Access web interface at `http://localhost:5001`
   - Filter data by time period
   - View all metrics in a responsive web layout

### Managing Profiles

- **Switch Profile**: Select from dropdown in Profile Manager
- **Edit Balance**: Update initial capital for any profile
- **View Statistics**: See detailed profile analytics
- **Delete Profile**: Remove profile and all associated data (requires confirmation)

## 🗂️ Project Structure

```
Crypto_Trading_Journal/
├── journal.py              # Main application file
├── ai_analyzer.py          # AI chart analysis module
├── api_key_manager.py      # API key management system
├── theme_manager.py        # Theme and styling manager
├── requirements.txt        # Python dependencies
├── profiles/               # Profile data directory
│   └── profile_{id}/
│       └── trades.xlsx     # Trade data per profile
├── screenshots/            # Trade screenshot storage
├── avatars/               # Profile avatar images
├── settings.json          # Application settings
├── api_keys.json          # Encrypted API keys
└── theme_config.json      # Theme preferences
```

## 🔧 Configuration Files

### settings.json
Stores global application settings including initial balance configuration.

### api_keys.json
Securely stores Gemini API keys mapped to profile IDs.

### theme_config.json
Saves user's theme preference (dark/light mode).

## 🎯 Features in Detail

### Trade Entry Fields
- **Time**: Automatic timestamp with manual edit option
- **Day**: Auto-calculated day of the week
- **Pair**: Crypto trading pair (e.g., BTC/USDT)
- **Position Type**: Long or Short position
- **Trade Type**: IDEA, SIGNAL, or STRATEGY
- **Trade Size**: Position size in USDT
- **Leverage**: Trading leverage (1x-125x)
- **TP & SL**: Take profit and stop loss prices with auto-calculated amounts
- **R:R Ratio**: Risk-reward ratio calculation
- **Status**: Running or Closed
- **Outcome**: Win, Loss, or Break Even
- **PnL**: Profit/Loss in USDT and percentage

### Calculated Metrics
- **Account Performance**: Net/gross returns, current balance, daily P&L
- **Win/Loss Statistics**: Win rate, profit factor, expectancy
- **Position Analysis**: Long vs Short performance
- **Risk Metrics**: Kelly Criterion, Sharpe-like SQN
- **Extremes**: Biggest win/loss ($ and %)
- **Consistency**: Standard deviation, consecutive streaks

## 🛠️ Development

### Building Executable
Package the application as a standalone .exe using PyInstaller:

```bash
pyinstaller --onefile --windowed --icon=app_icon.ico journal.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI**: For powerful image analysis capabilities
- **PyQt5**: For robust desktop GUI framework
- **Pandas & Matplotlib**: For data handling and visualization
- **Flask**: For web dashboard functionality

## 📧 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/sanjeewan24/Crypto_Trading_Journal/issues)
- **Author**: Sanjeewan
- **Repository**: https://github.com/sanjeewan24/Crypto_Trading_Journal

---

**⚠️ Disclaimer**: This software is for educational and journaling purposes only. Cryptocurrency trading involves substantial risk. The developers are not responsible for any financial losses incurred through trading decisions.
