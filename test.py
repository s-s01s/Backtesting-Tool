import pandas as pd

#Custom Dataset
dates = pd.date_range(start='2020-01-01', periods=20, freq='D')
data = pd.DataFrame({
    'Open':  [100] * 20,
    'High':  [100] * 20,
    'Low':   [100] * 20,
    'Close': [100] * 20
}, index=dates)

# Adjust days 15-18:
data.loc['2020-01-15', ['Open', 'High', 'Low', 'Close']] = 101           # Day 15: Price = 101 (entry)
data.loc['2020-01-16', 'High'] = 105.04                                  # Day 16: High  = TP = 101×1.04 = 105.04 (TP triggered)
data.loc['2020-01-17', ['Open', 'High', 'Low', 'Close']] = 101           # Day 17: Price reset to 101 (entry)
data.loc['2020-01-18', 'Low'] = 98.98                                    # Day 18: Low = SL = 101×0.98 = 98.98 (SL triggered)


# Compute SMA5 and SMA15
data['SMA5'] = data['Close'].rolling(window=5).mean()
data['SMA15'] = data['Close'].rolling(window=15).mean()

data.dropna(inplace=True)  # Remove rows where the rolling window is incomplete.

print("=== Data with SMA Indicators ===")
print(data.head())


class Backtest:
    def __init__(self, data, conditions, parameters):

        self.data = data
        self.conditions = conditions
        self.parameters = parameters
        self.trades = []  # To store trade details
        self.initialbala = int(parameters["Initial Investment"])
        self.balance = self.initialbala
        self.equity = self.balance  # Equity starts equal to balance.
        self.tradesize = 0.1
        self.stop_loss_pct = float(parameters["Stop Loss"])
        self.take_profit_pct = float(parameters["Take Profit"])
        print(f"Initial Balance: {self.balance}, Stop Loss: {self.stop_loss_pct}, Take Profit: {self.take_profit_pct}")

    def generate_signals(self):

        # Test Strategy
        # Entry signal when SMA5 value > SMA15 value

        self.data["Buy_Signal"] = (self.data["SMA5"] > self.data["SMA15"])

        if 'Buy_Signal' not in self.data.columns:
            self.data['Buy_Signal'] = False
        if 'Sell_Signal' not in self.data.columns:
            self.data['Sell_Signal'] = False

        for cond in self.conditions:
            indicator1 = cond['indicator1']
            condition = cond['condition']
            indicator2 = cond['indicator2']
            # For simplicity, assume the necessary indicators (SMA5 and SMA15) are already computed.
            column1 = self.data[indicator1]
            column2 = self.data[indicator2]
            if condition == "=":
                result = column1 == column2
            elif condition == "<":
                result = column1 < column2
            elif condition == ">":
                result = column1 > column2
            else:
                raise ValueError(f"Invalid condition: {condition}")
            # Combine with any previous signals.
            self.data['Buy_Signal'] = self.data['Buy_Signal'] | result

    def run_backtest(self):

        position = None  # No open trade initially.

        for index, row in self.data.iterrows():
            if position is None:
                # Check for a buy signal and available equity.
                if row['Buy_Signal']:
                    if self.equity > self.initialbala * self.tradesize:
                        position = {
                            'entry_price': row['Close'],
                            'entry_index': index,
                            'position_val': self.equity * self.tradesize,  # Cash allocated to this trade.
                            'position_vol': (self.equity * self.tradesize) / row['Close'],  # Number of shares.
                            'stop_loss': row['Close'] * (1 - self.stop_loss_pct),
                            'take_profit': row['Close'] * (1 + self.take_profit_pct)
                        }
                        # Deduct the allocated trade value from the available equity.
                        self.equity = self.equity - self.equity * self.tradesize
                        print("Opened trade:", position)
                    else:
                        print("Currently in max concurrent trades.")
            else:
                # Trade is open; check for exit conditions.
                exit_trade = False
                exit_reason = None
                if row['Low'] <= position['stop_loss']:
                    exit_trade = True
                    exit_reason = 'Stop Loss'
                    exit_price = position['stop_loss']
                elif row['High'] >= position['take_profit']:
                    exit_trade = True
                    exit_reason = 'Take Profit'
                    exit_price = position['take_profit']
                elif row['Sell_Signal']:
                    exit_trade = True
                    exit_reason = 'Sell Signal'
                    exit_price = row['Close']
                if exit_trade:
                    profit = position['position_vol'] * (exit_price - position['entry_price'])
                    trade = {
                        'entry_index': position['entry_index'],
                        'entry_price': position['entry_price'],
                        'exit_index': index,
                        'exit_price': exit_price,
                        'exit_val': position['position_vol'] * exit_price,
                        'exit_reason': exit_reason,
                        'profit': profit,
                        'post_trade_balance': self.balance + profit
                    }
                    self.trades.append(trade)
                    # Update the overall balance and equity.
                    self.balance = self.balance + profit
                    self.equity = self.balance
                    print(f"Closed trade at {index} with exit price {exit_price} due to {exit_reason}, profit: {profit:.2f}")
                    position = None

    def evaluate_performance(self):

        #Convert trades to DataFrame
        trades_df = pd.DataFrame(self.trades)
        if trades_df.empty:
            print("No trades were executed.")
            return

        #Calculate metrics
        total_profit = trades_df['profit'].sum()
        win_rate = (trades_df['profit'] > 0).mean()
        num_trades = len(trades_df)
        avg_profit = trades_df['profit'].mean()
        ROI = (total_profit / self.initialbala)

        #Display metrics
        print(f"Total Profit: {total_profit}")
        print(f"Win Rate: {win_rate * 100:.2f}%")
        print(f"Number of Trades: {num_trades}")
        print(f"Average Profit per Trade: {avg_profit}")
        print(f"Return on Investment: {ROI * 100:.2f}%")
        print("Final Balance:", self.balance, "Final Equity:", self.equity)
        return trades_df


conditions = [{"indicator1": "SMA5", "condition": ">", "indicator2": "SMA15"}]
parameters = {"Initial Investment": 10000, "Stop Loss": 0.02, "Take Profit": 0.04}

backtest = Backtest(data, conditions=conditions, parameters=parameters)
backtest.generate_signals()
backtest.run_backtest()
results = backtest.evaluate_performance()

print("\n=== Trade Log ===")
for trade in backtest.trades:
    print(f"Entry Date: {trade['entry_index']}, Entry Price: {trade['entry_price']}\n",
        f" Exit Date: {trade['exit_index']}, Exit Price: {trade['exit_price']}\n"
        f"  Profit: {trade['profit']}, Post Trade Balance: {trade['post_trade_balance']}")


