import pandas as pd
import pandas_ta as ta
import yfinance as yf
import threading
import Indicators
from Indicators import Indicator

"""df = pd.read_csv("BMW.DEEUR_Candlestick_1_D_BID_03.01.2011-11.05.2024.csv")
df["Gmt time"]=df["Gmt time"].str.replace(".000","")
df['Gmt time']=pd.to_datetime(df['Gmt time'],format='%d.%m.%Y %H:%M:%S')
"""

"""df = yf.download("TSLA", start="2013-01-01", end="2024-01-01", interval="1d")

df.ta.bbands(append=True, length=30, std=2)
df.ta.rsi(append=True, length=14)

df.rename(columns={'BBU_30_2.0':'UBB', 'BBL_30_2.0':'LBB', 'RSI_14':'RSI'}, inplace=True)
print(df.head())
"""
class Backtest:
    def __init__(self, user_id, data, conditions, parameters, strategy_window):

        self.user_id = user_id
        self.data = data
        self.conditions = conditions
        self.parameters = parameters
        self.strategy_window = strategy_window
        self.trades = []  # To store trade details
        self.initialbala = int(parameters["Initial Investment"])#for calculation of min trade size
        self.balance=self.initialbala
        self.equity=self.balance #set to balance to start
        self.tradesize= 0.1
        self.stop_loss_pct = float(parameters["Stop Loss"])
        self.take_profit_pct = float(parameters["Take Profit"])
        print(f"Initializing Backtest for User ID: {user_id}")


        print(self.balance, self.stop_loss_pct, self.take_profit_pct)

    def _execute_backtest(self):

        print("Starting signal generation...")
        self._generate_signals()

        print("Running backtest...")
        self._run_backtest()

        if not self.trades:
            print("No trades executed. Returning to Strategy Selection.")
            return False  # Indicate that no trades were executed

        print("Evaluating performance...")
        self.strategy_window.app.destroy()
        self._evaluate_performance()


    def _generate_signals(self):

        # Initialize the 'Buy_Signal' column to False
        if 'Buy_Signal' not in self.data.columns:
            self.data['Buy_Signal'] = False


        for cond in self.conditions:
            indicator1 = cond['indicator1']
            condition = cond['condition']
            indicator2 = cond['indicator2']

            #add chosen indicators to data frame if they don't already exist.

            if indicator1 == "RSI" or indicator2 == "RSI":
                if "RSI" not in self.data.columns:
                    Indicators.RSI(self.data)
                    print("added RSI")
            if indicator1 == "BBW" or indicator2 == "BBW":
                if "BBW" not in self.data.columns:
                    Indicators.BBANDS(self.data)
                    print("added Bollinger Bands")
            if indicator1 == "MACD" or indicator2 == "MACD":
                if "MACD" not in self.data.columns:
                    Indicators.MACD(self.data)
                    print("added MACD")
            if indicator1 == "ATR" or indicator2 == "ATR":
                if "ATR" not in self.data.columns:
                    Indicators.ATR(self.data)
                    print("added ATR")
            if indicator1 == "SMA5" or indicator2 == "SMA5":
                if "SMA5" not in self.data.columns:
                    Indicators.SMA(self.data, 5)
                    print("added SMA5")
            if indicator1 == "SMA15" or indicator2 == "SMA15":
                if "SMA15" not in self.data.columns:
                    Indicators.SMA(self.data, 15)
                    print("added SMA15")
            if indicator1 == "SMA45" or indicator2 == "SMA45":
                if "SMA45" not in self.data.columns:
                    Indicators.SMA(self.data, 45)
                    print("added SMA45")
            if indicator1 == "SMA150" or indicator2 == "SMA150":
                if "SMA150" not in self.data.columns:
                    Indicators.SMA(self.data, 150)
                    print("added SMA150")


        #must be done after all indicators are added
        for cond in self.conditions:
            #map indicator names to df columns
            column1 = self.data[indicator1]
            column2 = self.data[indicator2]

            # Create the condition dynamically
            if condition == "=":
                result = column1 == column2
            elif condition == "<":
                result = column1 < column2
            elif condition == ">":
                result = column1 > column2
            else:
                raise ValueError(f"Invalid condition: {condition}")

            self.data['Buy_Signal'] = self.data['Buy_Signal'] | result  # Combine multiple conditions with OR

    def _run_backtest(self):

        position = None  # Track if we are currently in a trade

        for index, row in self.data.iterrows():
            if position is None:  # No current trade
                # Check for a buy signal
                if row['Buy_Signal']:
                    if self.equity > self.initialbala*self.tradesize:
                        position = {
                            'entry_price': row['Close'],
                            'entry_index': index,
                            'position_val': self.equity*self.tradesize, #available equity multiplied by the tradesize specified
                            'position_vol': (self.equity*self.tradesize)/row['Close'], #position value over price per share
                            'stop_loss': row['Close'] * (1 - self.stop_loss_pct),
                            'take_profit': row['Close'] * (1 + self.take_profit_pct)
                        }
                        self.equity = self.equity - self.equity*self.tradesize #update available equity
                        #print(f"Opening trade at {index} with entry price {position['entry_price']}")
                        #print(position)
                    else:
                        print("Currently in max concurrent trades.")

            else:  # We are in a trade
                # Check for exit conditions
                exit_trade = False
                exit_reason = None

                # Stop Loss
                if row['Low'] <= position['stop_loss']:
                    exit_trade = True
                    exit_reason = 'Stop Loss'
                    exit_price = position['stop_loss']

                # Take Profit
                elif row['High'] >= position['take_profit']:
                    exit_trade = True
                    exit_reason = 'Take Profit'
                    exit_price = position['take_profit']

                if exit_trade:
                    # Record the trade
                    profit = position['position_vol']*(exit_price - position['entry_price'])
                    trade = {
                        'entry_index': position['entry_index'],
                        'entry_price': position['entry_price'],
                        'exit_index': index,
                        'exit_price': exit_price,
                        'exit_val': position['position_vol']*exit_price,
                        'exit_reason': exit_reason,
                        'profit': profit,
                        'post_trade_balance': self.balance+profit
                    }
                    self.trades.append(trade)

                    self.balance = self.balance + profit
                    self.equity = self.balance
                    #print(f"Closing trade at {index} with exit price {exit_price} due to {exit_reason}")
                    #print (profit)

                    position = None  # Reset position



    def _evaluate_performance(self):

        # Convert trades to a DataFrame for analysis
        trades_df = pd.DataFrame(self.trades)
        #for trade in trades_df.itertuples():
            #print(f"Trade: Entry={trade.entry_price}, Exit={trade.exit_price}, Profit={trade.profit}")

        import Results
        results_window = Results.ResultsWindow(self.user_id, self.data, trades_df, self.conditions, self.parameters)
        results_window.app.mainloop()


"""df = yf.download("TSLA", start="2013-01-01", end="2024-01-01", interval="1d")
conditions = [{'indicator1': 'SMA5', 'condition': '>', 'indicator2': 'SMA15'}]
parameters = {'Initial Investment': '10000', 'Stop Loss': '.2', 'Take Profit': '.4'}
bt = Backtest(1,df,conditions, parameters)
bt._execute_backtest()"""