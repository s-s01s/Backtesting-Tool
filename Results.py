from tkinter import CENTER

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import mplfinance as mpf
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton
import sqlite3
from datetime import date, datetime
import json

class ResultsWindow():
    def __init__(self, user_id, stock_data, trades, conditions, parameters):

        self.app = CTk()
        self.results_data = None
        self.user_id = user_id
        self.app.title("Backtest Results")
        self.app.geometry("850x800")
        self.app.resizable(0, 0)

        # Create a frame for the Matplotlib chart
        self.plot_frame = CTkFrame(self.app, width=1000, height=900)
        self.plot_frame.pack(pady=10)

        self.user_id=user_id
        self.stock_data = stock_data
        self.trades = trades
        self.conditions = conditions
        self.parameters = parameters

        self.plot_stock_chart(stock_data, trades)
        self.display_statistics(stock_data, trades, parameters)
        self.buttons()

    def plot_stock_chart(self, stock_data: pd.DataFrame, trades: pd.DataFrame):

        # Convert the DataFrame index to datetime if it's not already
        stock_data.index = pd.to_datetime(stock_data.index)

        # Set dark matplotlib style
        plt.style.use("dark_background")

        # Create the candlestick chart using mplfinance
        fig, ax = plt.subplots(figsize=(10, 6), facecolor="black")  # Set background color
        mpf.plot(
            stock_data,
            type='candle',
            ax=ax,
            style='charles',  # Set dark mplfinance style
            show_nontrading=True,
        )

        # Add buy markers (entry points)
        ax.scatter(
            trades['entry_index'], trades['entry_price'],  # Use entry data
            color='green', label='Entry', marker='^', s=100
        )

        # Add sell markers (exit points)
        ax.scatter(
            trades['exit_index'], trades['exit_price'],  # Use exit data
            color='red', label='Exit', marker='v', s=100
        )

        # Customize the chart
        ax.set_title("Stock Price with Entry and Exit Points", fontsize=14, color="white")
        ax.set_xlabel("Date", fontsize=12, color="white")
        ax.set_ylabel("Price", fontsize=12, color="white")
        ax.legend(facecolor="gray", edgecolor="white")  # Set legend background and border colors

        # Customize tick colors
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        # Embed the Matplotlib figure into the Tkinter frame
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        canvas.draw()

    def display_statistics(self, stock_data: pd.DataFrame, trades: pd.DataFrame, parameters):
        initialbala = int(parameters["Initial Investment"])
        total_profit = trades['profit'].sum()
        win_rate = (trades['profit'] > 0).mean()
        num_trades = len(trades)
        avg_profit = trades['profit'].mean()
        ROI = (total_profit / initialbala)
        self.results_data = [{"Initial Investment": initialbala,
                              "Total Profit": total_profit,
                              "Win Rate": win_rate,
                              "Number of Trades": num_trades,
                              "Avg Profit": avg_profit,
                              "ROI": ROI}]

        CTkLabel(self.app, text=f"Initial balance: {initialbala}", fg_color="transparent").pack(pady=5)
        CTkLabel(self.app, text=f"Total Profit: {total_profit}", fg_color="transparent").pack(pady=5)
        CTkLabel(self.app, text=f"Win Rate: {win_rate}", fg_color="transparent").pack(pady=5)
        CTkLabel(self.app, text=f"Number of Trades: {num_trades}", fg_color="transparent").pack(pady=5)
        CTkLabel(self.app, text=f"Average Profit: {avg_profit}", fg_color="transparent").pack(pady=5)
        CTkLabel(self.app, text=f"ROI: {ROI}", fg_color="transparent").pack(pady=5)


    def save_results(self):
        temp = datetime.now()
        currentDate = temp.strftime("%d/%m/%Y")  # For saving to database
        currentTime = temp.strftime("%H:%M:%S")

        # data to JSON strings
        stock_data_json = self.stock_data.to_json()  # DataFrame to JSON string
        trades_json = self.trades.to_json()  # DataFrame to JSON string
        conditions_json = json.dumps(self.conditions)  # list to JSON string
        parameters_json = json.dumps(self.parameters)  # list to JSON string
        results_data_json = json.dumps(self.results_data)  # list to JSON string

        # Save data to SQLite
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("""
                INSERT INTO previousRuns (date, time, stock_data, conditions, parameters, trades_data, results_data, user_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
        currentDate, currentTime, stock_data_json, conditions_json, parameters_json, trades_json, results_data_json,
        self.user_id))
        conn.commit()
        conn.close()
        print("Results saved successfully.")
        self.save_results_btn.configure(state="disabled")
        self.save_lbl=CTkLabel(self.app,
                text="Results saved successfully.",
                fg_color="transparent",
                text_color="green")
        self.save_lbl.place(relx=0.5, rely=0.95, anchor=CENTER)

    def backtomainmenu(self):
        self.app.destroy()  # Close the ResultsWindow
        from MainMenu import MainMenu
        main_menu = MainMenu(self.user_id)  # Initialize the Main Menu
        main_menu.run()  # Launch the Main Menu

    def buttons(self):
        self.save_results_btn=CTkButton(self.app, text="Save Results", corner_radius=32, fg_color="#C850C0", hover_color=("#4158D0"), border_width=2, command=self.save_results)
        self.save_results_btn.place(relx=0.8, rely=0.95, anchor=CENTER)
        self.backtomainmenubtn=CTkButton(self.app, text="Back to Main Menu", corner_radius=32, fg_color="#C850C0", hover_color=("#4158D0"), border_width=2, command=self.backtomainmenu)
        self.backtomainmenubtn.place(relx=0.2, rely=0.95, anchor=CENTER)

