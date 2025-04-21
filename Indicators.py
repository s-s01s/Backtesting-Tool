import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import pandas_ta as ta


class Indicator:
    def __init__(self, data):
        self.Data = data

class SMA(Indicator):
    def __init__(self, data, period=20):
        super().__init__(data)
        self.period = period
        data[f"SMA{period}"] = data['Close'].rolling(window=self.period).mean()

class BBANDS(Indicator):
    def __init__(self, data):
        Indicator.__init__(self, data)
        # Calculate the 20-period Simple Moving Average (SMA)
        SMA = data['Close'].rolling(window=30).mean()

        # Calculate the 20-period Standard Deviation (SD)
        SD = data['Close'].rolling(window=30).std()

        # Calculating  Upper Bollinger Band (UBB) and Lower Bollinger Band (LBB)
        data['UBB'] = SMA + 2 * SD
        data['LBB'] = SMA - 2 * SD
        data['BBW'] = (data['UBB'] - data['LBB'])/((data['UBB']+data['LBB'])/2)

class RSI(Indicator):
    def __init__(self, data, period=14, scalar=100):
        Indicator.__init__(self, data)
        self.period = period

        # Calculate the change in prices
        change = data["Close"].diff()

        # Separate gains and losses
        change_up = change.copy()
        change_down = change.copy()

        # Set gains and losses
        change_up[change_up < 0] = 0
        change_down[change_down > 0] = 0
        change_down = change_down.abs()

        # Calculate the RMA (Rolling Moving Average) using EMA with alpha = 1/period
        avg_up = change_up.ewm(alpha=1/period, adjust=False).mean()
        avg_down = change_down.ewm(alpha=1/period, adjust=False).mean()

        # Calculate the RSI
        rs = avg_up / avg_down
        data["RSI"] = scalar * avg_up / (avg_up + avg_down)

class MACD(Indicator):
    def __init__(self, data):
        data['EMA12'] = self.calculate_ema(data['Close'], 12)
        data['EMA26'] = self.calculate_ema(data['Close'], 26)

        # Calculate MACD
        data['MACD_no_ema'] = data['EMA12'] - data['EMA26']
        # Calculate Signal Line (9-period EMA of MACD)
        data['MACD'] = self.calculate_ema(data['MACD_no_ema'], 9)

    def calculate_ema(self, series, period):
        alpha = 2 / (period + 1)
        ema_values = [series.iloc[0]]  # Start with the first value as the initial EMA

        for price in series[1:]:
            new_ema = (price * alpha) + (ema_values[-1] * (1 - alpha))
            ema_values.append(new_ema)

        return pd.Series(ema_values, index=series.index)

class ATR(Indicator):
    def __init__(self, data, period=14):
        super().__init__(data)
        self.period = period

        # Calculate True Range (TR)
        data['High-Low'] = data['High'] - data['Low']
        data['High-PreviousClose'] = (data['High'] - data['Close'].shift(1)).abs()
        data['Low-PreviousClose'] = (data['Low'] - data['Close'].shift(1)).abs()

        # True Range is the maximum of these three values
        data['TrueRange'] = data[['High-Low', 'High-PreviousClose', 'Low-PreviousClose']].max(axis=1)

        # Calculate ATR using a rolling average of True Range
        data['ATR'] = data['TrueRange'].rolling(window=self.period).mean()

        # Clean up the temporary columns
        data.drop(columns=['High-Low', 'High-PreviousClose', 'Low-PreviousClose', 'TrueRange'], inplace=True)

class SMA(Indicator):
    def __init__(self, data, period):
        super().__init__(data)
        self.period = period
        data[f'SMA{period}'] = data['Close'].rolling(window=period).mean()

"""
df = yf.download("TSLA", start="2010-01-01", end="2020-01-01", interval="1d")
df=df[df.High!=df.Low]

# Comparing my BBW to PandasTA BBW
df.ta.bbands(append=True, length=30, std=2)

#df.ta.rsi(append=True, length=14)
BBANDS(df)
df.dropna(inplace=True)
print(df.head())

plt.figure(figsize=(12, 6))
plt.plot(df.index, df["BBW"], label="Custom BBW", linestyle='--')
plt.plot(df.index, df["TA_BBW"], label="PandasTA BBW", linestyle='-')
plt.title("BBW Comparison: Custom vs PandasTA")
plt.xlabel("Index")
plt.ylabel("BBW")
plt.legend()
plt.show()
"""

# Download TSLA historical data
df = yf.download("TSLA", start="2010-01-01", end="2020-01-01", interval="1d")
df = df[df.High != df.Low]  # Remove invalid rows where High == Low

# Apply Pandas TA Indicators
df.ta.atr(append=True, length=14)  # Pandas TA ATR (default period 14)
df.ta.macd(append=True, fast=12, slow=26, signal=9)  # Pandas TA MACD

df.rename(columns={
    'ATRr_14': 'TA_ATR',
    'MACD_12_26_9': 'TA_MACD',
    'MACDs_12_26_9': 'TA_MACD_Signal',
}, inplace=True)

ATR(df, period=14)  # Custom ATR implementation
MACD(df)  # Custom MACD implementation

df.dropna(inplace=True)

plt.figure(figsize=(12, 5))
plt.plot(df.index, df["ATR"], label="Custom ATR", linestyle="--")
plt.plot(df.index, df["TA_ATR"], label="PandasTA ATR", linestyle="-")
plt.title("ATR Comparison: Custom vs PandasTA")
plt.xlabel("Date")
plt.ylabel("ATR")
plt.legend()
plt.show()

plt.figure(figsize=(12, 5))
plt.plot(df.index, df["MACD"], label="Custom MACD", linestyle="--")
plt.plot(df.index, df["TA_MACD"], label="PandasTA MACD", linestyle="-")
plt.title("MACD Comparison: Custom vs PandasTA")
plt.xlabel("Date")
plt.ylabel("MACD")
plt.legend()
plt.show()

