from flask import Flask, render_template_string, request, Response
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO

app = Flask(__name__)

def load_data():
    df = pd.read_excel('D:/Trading/Trading/trades.xlsx')
    df['Time'] = pd.to_datetime(df['Time'])
    df['PnL %'] = pd.to_numeric(df['PnL %'], errors='coerce')
    return df

def calculate_metrics(df):
    initial_balance = 4889.77  # Reset the account balance to $4,900.91
    total_shares = 100
    metrics = {}

    metrics['Acc. Return Net $'] = df['PnL'].sum()
    metrics['Acc. Return Gross $'] = df['PnL'].abs().sum()
    metrics['Account Balance'] = initial_balance + metrics['Acc. Return Net $']

    # Calculate today's total return
    today = datetime.now().date()
    daily_return = df[df['Time'].dt.date == today]['PnL'].sum()
    metrics['Daily Return $'] = round(daily_return, 2)

    metrics['Return on Winners'] = df[df['Outcome'] == 'Win']['PnL'].sum()
    metrics['Return on Losers'] = df[df['Outcome'] == 'Loss']['PnL'].sum()

    if 'Position Type' in df.columns:
        metrics['Return $ on Long'] = df[df['Position Type'] == 'Long Position']['PnL'].sum()
        metrics['Return $ on Short'] = df[df['Position Type'] == 'Short Position']['PnL'].sum()
    else:
        metrics['Return $ on Long'] = "Position Type column not found"
        metrics['Return $ on Short'] = "Position Type column not found"

    metrics['Biggest Profit $'] = df[df['PnL'] > 0]['PnL'].max()
    metrics['Biggest Loss $'] = df[df['PnL'] < 0]['PnL'].min()

    if metrics['Return on Losers'] != 0:
        metrics['Profit/Loss Ratio'] = abs(metrics['Return on Winners']) / abs(metrics['Return on Losers'])
        metrics['Profit Factor'] = metrics['Return on Winners'] / abs(metrics['Return on Losers'])
    else:
        metrics['Profit/Loss Ratio'] = 0
        metrics['Profit Factor'] = 0

    metrics['Trade $ Expectancy'] = df['PnL'].mean()
    metrics['Win %'] = (df['Outcome'] == 'Win').mean() * 100
    metrics['Loss %'] = (df['Outcome'] == 'Loss').mean() * 100
    metrics['BE %'] = (df['Outcome'] == 'Break Even').mean() * 100
    metrics['Open %'] = (df['Status'] == 'Running').mean() * 100
    metrics['Acc. Return %'] = (metrics['Acc. Return Net $'] / initial_balance) * 100
    metrics['Biggest % Profit'] = df[df['PnL %'] > 0]['PnL %'].max()
    metrics['Biggest % Loser'] = df[df['PnL %'] < 0]['PnL %'].min()
    metrics['Return per Share'] = metrics['Acc. Return Net $'] / total_shares

    if metrics['Profit/Loss Ratio'] != 0:
        metrics['Kelly Criterion'] = (metrics['Win %'] / 100 * (metrics['Profit/Loss Ratio'] + 1) - 1) / metrics['Profit/Loss Ratio']
    else:
        metrics['Kelly Criterion'] = 0

    metrics['Avg Return'] = df['PnL %'].mean()
    metrics['Avg Return $'] = df['PnL'].mean()
    metrics['Return/Size'] = metrics['Acc. Return Net $'] / df['Trade Size'].sum()
    metrics['Avg $ on Winners'] = df[df['Outcome'] == 'Win']['PnL'].mean()
    metrics['Avg $ on Losers'] = df[df['Outcome'] == 'Loss']['PnL'].mean()
    metrics['Avg Daily P&L'] = daily_return
    metrics['Avg Return %'] = df['PnL %'].mean()
    metrics['Avg % Return'] = df['PnL %'].mean()

    if 'Position Type' in df.columns:
        metrics['Avg % on Shorts'] = df[df['Position Type'] == 'Short Position']['PnL %'].mean()
        metrics['Avg % on Long'] = df[df['Position Type'] == 'Long Position']['PnL %'].mean()
    else:
        metrics['Avg % on Shorts'] = "Position Type column not found"
        metrics['Avg % on Long'] = "Position Type column not found"

    metrics['Avg % on Winners'] = df[df['Outcome'] == 'Win']['PnL %'].mean()
    metrics['Avg % on Losers'] = df[df['Outcome'] == 'Loss']['PnL %'].mean()
    metrics['Trades'] = len(df)
    metrics['Total Winner'] = (df['Outcome'] == 'Win').sum()
    metrics['Total Open Trades'] = (df['Status'] == 'Running').sum()
    metrics['Tot. Closed Trades'] = (df['Status'] == 'Closed').sum()
    metrics['Total Losers'] = (df['Outcome'] == 'Loss').sum()
    metrics['Total BE'] = (df['Outcome'] == 'Break Even').sum()
    metrics['Max Consec. Loss'] = df['PnL'].lt(0).astype(int).cumsum().mul(df['PnL'].lt(0)).diff().fillna(0).cummax().max()
    metrics['Max Consec. Win'] = df['PnL'].gt(0).astype(int).cumsum().mul(df['PnL'].gt(0)).diff().fillna(0).cummax().max()
    metrics['PnL Std Dev'] = df['PnL'].std()
    metrics['PnL Std Dev (W)'] = df[df['Outcome'] == 'Win']['PnL'].std()
    metrics['PnL Std Dev (L)'] = df[df['Outcome'] == 'Loss']['PnL'].std()

    if metrics['PnL Std Dev'] != 0:
        metrics['SQN'] = metrics['Avg Return $'] / metrics['PnL Std Dev'] * (metrics['Trades'] ** 0.5)
    else:
        metrics['SQN'] = 0

    return metrics

def generate_report(metrics):
    report = StringIO()
    report.write("📊 Trade Metrics Report 📊\n")
    report.write("="*50 + "\n")
    for key, value in metrics.items():
        report.write(f"{key}: {value}\n")
    report.seek(0)
    return report

@app.route('/', methods=['GET', 'POST'])
def index():
    df = load_data()
    filter_option = request.form.get('filter') if request.method == 'POST' else 'all'

    if filter_option == 'last_7_days':
        start_date = datetime.now() - timedelta(days=7)
        df = df[df['Time'] >= start_date]
    elif filter_option == 'last_30_days':
        start_date = datetime.now() - timedelta(days=30)
        df = df[df['Time'] >= start_date]

    metrics = calculate_metrics(df)

    html_template = '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>📈 Trade Metrics</title>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');
          body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Open Sans', sans-serif;
            margin: 0;
            padding: 0;
          }
          .header {
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 20px;
            background-color: #1f1f1f;
          }
          .header h1 {
            margin: 0;
            font-size: 24px;
            color: #ffffff;
          }
          .header p {
            margin: 0;
            font-size: 20px;
            color: #ffffff;
          }
          .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            padding: 20px;
          }
          .card {
            background-color: #1f1f1f;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            width: 220px;
            text-align: center;
          }
          .card h3 {
            margin: 0;
            font-size: 18px;
            color: #ffffff;
          }
          .card p {
            margin: 10px 0;
            font-size: 16px;
            color: #0f0;
          }
          .chart-container {
            position: relative;
            height: 400px;
            width: 100%;
            margin: auto;
          }
          .filter-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin: 20px;
          }
          .filter-container label, .filter-container select, .filter-container button {
            font-size: 18px;
            margin: 5px;
            color: #ffffff;
          }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      </head>
      <body>
        <div class="header">
          <div>
            <h1>💸 Account Balance</h1>
            <p>${{ metrics['Account Balance'] }}</p>
          </div>
          <div>
            <h1>📊 Total Trades</h1>
            <p>{{ metrics['Trades'] }}</p>
          </div>
          <div>
            <h1>🏆 Win Rate</h1>
            <p>{{ metrics['Win %'] }}%</p>
          </div>
        </div>
        <div class="filter-container">
          <form method="post" style="display: flex; align-items: center;">
            <label for="filter">🔍 Filter:</label>
            <select name="filter" id="filter">
              <option value="all">All Time</option>
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
            </select>
            <button type="submit">Apply ✅</button>
          </form>
          <form action="/save_report" method="post" style="display: flex; align-items: center;">
            <input type="hidden" name="filter" value="{{ filter_option }}">
            <button type="submit">💾 Save Report</button>
          </form>
        </div>
        <div class="container">
          {% for key, value in metrics.items() %}
            <div class="card">
              <h3>{{ key }}</h3>
              <p>{{ value }}</p>
            </div>
          {% endfor %}
        </div>
        <div class="chart-container">
          <canvas id="pnlChart"></canvas>
        </div>
        <script>
          var ctx = document.getElementById('pnlChart').getContext('2d');
          var pnlChart = new Chart(ctx, {
            type: 'line',
            data: {
              labels: {{ df.index.tolist() | tojson | safe }},
              datasets: [{
                label: 'PnL Over Time 📈',
                data: {{ df['PnL'].tolist() | tojson | safe }},
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                fill: false,
              }]
            },
            options: {
              scales: {
                x: {
                  title: {
                    display: true,
                    text: 'Trade Index 🔢'
                  }
                },
                y: {
                  title: {
                    display: true,
                    text: 'PnL 💵'
                  }
                }
              },
              plugins: {
                legend: {
                  display: true,
                  position: 'top'
                }
              }
            }
          });
        </script>
      </body>
    </html>
    '''
    return render_template_string(html_template, metrics=metrics, df=df, filter_option=filter_option)

@app.route('/save_report', methods=['POST'])
def save_report():
    df = load_data()
    filter_option = request.form.get('filter')

    if filter_option == 'last_7_days':
        start_date = datetime.now() - timedelta(days=7)
        df = df[df['Time'] >= start_date]
    elif filter_option == 'last_30_days':
        start_date = datetime.now() - timedelta(days=30)
        df = df[df['Time'] >= start_date]

    metrics = calculate_metrics(df)
    report = generate_report(metrics)

    return Response(
        report.getvalue(),
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={filter_option}_report.txt'}
    )

if __name__ == '__main__':
    app.run(debug=True)
