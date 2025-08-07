from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# Load the trades from the Excel file
trades_df = pd.read_excel('trades.xlsx')

# Use the 'Time' column for date filtering
date_column = 'Time'

# Convert the 'Time' column to datetime
trades_df[date_column] = pd.to_datetime(trades_df[date_column])

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trading Journal 🚀</title>
        <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            body {
                background-color: #121212;
                color: #ffffff;
                font-family: 'Open Sans', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .calendar {
                width: 90%;
                max-width: 1200px;
                background-color: #1e1e1e;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                background-color: #333;
                font-size: 1.2em;
                font-weight: 600;
            }
            .header button {
                background-color: #444;
                border: none;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 1em;
            }
            .days {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 10px;
                padding: 15px;
            }
            .day {
                background-color: #2e2e2e;
                border-radius: 6px;
                padding: 12px;
                font-size: 1em;
                text-align: center;
                line-height: 1.4;
            }
            .trade {
                margin: 8px 0;
                padding: 10px;
                border-radius: 4px;
                font-size: 0.9em;
                line-height: 1.4;
                font-style: italic;
            }
            .trade.win {
                background-color: #4caf50;
            }
            .trade.loss {
                background-color: #f44336;
            }
            .trade.break-even {
                background-color: #ffeb3b;
                color: black;
            }
            .no-trades {
                color: #888;
                font-size: 0.9em;
                margin-top: 10px;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="calendar">
            <div class="header">
                <button id="prev-month">⬅️ Previous</button>
                <h1 id="month-year">📅 April 2025</h1>
                <button id="next-month">Next ➡️</button>
            </div>
            <div class="days">
                <!-- Days will be dynamically inserted here -->
            </div>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const daysContainer = document.querySelector('.days');
                const monthYearElement = document.querySelector('#month-year');
                const prevMonthButton = document.querySelector('#prev-month');
                const nextMonthButton = document.querySelector('#next-month');
                let currentDate = new Date();

                function renderCalendar() {
                    daysContainer.innerHTML = '';
                    monthYearElement.textContent = `${currentDate.toLocaleString('default', { month: 'long' })} ${currentDate.getFullYear()} 📅`;
                    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
                    const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

                    for (let i = 0; i < firstDay.getDay(); i++) {
                        const emptyDay = document.createElement('div');
                        emptyDay.classList.add('day');
                        daysContainer.appendChild(emptyDay);
                    }

                    for (let i = 1; i <= lastDay.getDate(); i++) {
                        const dayElement = document.createElement('div');
                        dayElement.classList.add('day');
                        dayElement.innerHTML = `<span style="font-size: 1.2em;">${i}</span> 🗓️`;

                        // Fetch and display trades for this day
                        fetch(`/api/trades?date=${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${i.toString().padStart(2, '0')}`)
                            .then(response => response.json())
                            .then(trades => {
                                if (trades.length === 0) {
                                    const noTradesElement = document.createElement('div');
                                    noTradesElement.classList.add('no-trades');
                                    noTradesElement.textContent = 'No trades today 🤷‍♂️';
                                    dayElement.appendChild(noTradesElement);
                                } else {
                                    trades.forEach(trade => {
                                        const tradeElement = document.createElement('div');
                                        tradeElement.classList.add('trade', trade.outcome.toLowerCase().replace(' ', '-'));

                                        // Determine the emoji and additional styling based on the outcome
                                        let outcomeEmoji = '';
                                        if (trade.outcome.toLowerCase() === 'win') {
                                            outcomeEmoji = '🎉';
                                        } else if (trade.outcome.toLowerCase() === 'loss') {
                                            outcomeEmoji = '😢';
                                        } else if (trade.outcome.toLowerCase() === 'break even') {
                                            outcomeEmoji = '😐';
                                        }

                                        tradeElement.innerHTML = `
                                            <strong>${trade.pair} 🔄</strong><br>
                                            Outcome: ${trade.outcome} ${outcomeEmoji}<br>
                                            PnL: ${trade.pnl}% 💸
                                        `;
                                        dayElement.appendChild(tradeElement);
                                    });
                                }
                            });
                        daysContainer.appendChild(dayElement);
                    }
                }

                prevMonthButton.addEventListener('click', function() {
                    currentDate.setMonth(currentDate.getMonth() - 1);
                    renderCalendar();
                });

                nextMonthButton.addEventListener('click', function() {
                    currentDate.setMonth(currentDate.getMonth() + 1);
                    renderCalendar();
                });

                renderCalendar();
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/api/trades', methods=['GET'])
def get_trades():
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d')

    # Filter trades for the given date
    trades = trades_df[trades_df[date_column].dt.date == date.date()]

    # Convert to list of dictionaries
    trades_list = trades.to_dict(orient='records')

    # Rename columns to match the front-end expectations
    for trade in trades_list:
        trade['pair'] = trade['Pair']
        trade['outcome'] = trade['Outcome']
        trade['pnl'] = trade['PnL %']

    return jsonify(trades_list)

if __name__ == '__main__':
    app.run(debug=True)
