import sqlite3
import pandas as pd
import json
from customtkinter import CTk, CTkLabel, CTkButton, CTkScrollableFrame, CENTER, set_appearance_mode, CTkFrame, \
    CTkComboBox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import mplfinance as mpf

class PreviousRunsWindow():
    def __init__(self, user_id):

        self.app = CTk()

        self.user_id = user_id
        self.app.title("Previous Runs")
        self.app.geometry("550x600")
        self.app.resizable(0, 0)
        self.previous_runs = []
        set_appearance_mode("dark")

        self.load_previous_runs()
        self.create_ui()

    def load_previous_runs(self):

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, time, stock_data, conditions, parameters, trades_data, results_data 
            FROM previousRuns 
            WHERE user_id = ?
        """, (self.user_id,))
        self.previous_runs = cursor.fetchall()
        conn.close()

    def create_ui(self):

        self.clear_ui() # First clear the UI in case sorting is used

        # Title Label
        title_label = CTkLabel(self.app, text="Previous Runs", width=200, height=50, fg_color="#C850C0")
        title_label.place(relx=0.5, rely=0.075, anchor=CENTER)

        # Sorting Dropdown
        sort_options = ["Date", "Total Profit", "Win Rate", "Number of Trades", "Average Profit", "ROI"]
        self.sort_dropdown = CTkComboBox(
            master=self.app,
            values=sort_options,
            command=lambda choice: self.sort_previous_runs(choice),  # Ensure function receives argument
            state="readonly"
        )
        self.sort_dropdown.set("Sort By (desc)")  # Default placeholder
        self.sort_dropdown.place(relx=0.5, rely=0.16, anchor=CENTER)

        # Scrollable frame for listing runs
        scrollable_frame = CTkScrollableFrame(self.app, width=500, height=400)
        scrollable_frame.place(relx=0.5, rely=0.55, anchor=CENTER)

        if not self.previous_runs:
            # If there are no previous runs, display a message
            no_runs_label = CTkLabel(
                scrollable_frame,
                text="No previous runs found.",
                fg_color="transparent",
                text_color="white"
            )
            no_runs_label.pack(pady=20)
        else:
            # Display each previous run
            for idx, run in enumerate(self.previous_runs):
                run_id, date, time, stock_data, conditions, parameters, trades_data, results_data = run

                # Run information label
                run_label = CTkLabel(
                    scrollable_frame,
                    text=f"Run ID: {run_id} | Date: {date} | Time: {time}",
                    fg_color="transparent",
                    text_color="white"
                )
                run_label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

                # View button for details
                view_button = CTkButton(
                    scrollable_frame,
                    text="View Details",
                    command=lambda r=run: self.view_run_details(r),
                    fg_color="#C850C0",
                    hover_color="#4158D0"
                )
                view_button.grid(row=idx, column=1, padx=10, pady=5)

        # Back button
        back_button = CTkButton(self.app, text="Back", fg_color="#C850C0", hover_color=("#4158D0"),
                                command=self.back_to_mainmenu)
        back_button.place(relx=0.5, rely=0.95, anchor=CENTER)

    def clear_ui(self):

        for widget in self.app.winfo_children():
            widget.destroy()

    def sort_previous_runs(self, choice):

        if choice == "Date":
            self.previous_runs.sort(key=lambda x: x[1], reverse=True)  # Sort by date (column index 1)
        elif choice == "Total Profit":
            self.previous_runs.sort(key=lambda x: json.loads(x[7])[0]["Total Profit"], reverse=True)  # Sort by profit
        elif choice == "Win Rate":
            self.previous_runs.sort(key=lambda x: json.loads(x[7])[0]["Win Rate"], reverse=True)  # Sort by win rate
        elif choice == "Number of Trades":
            self.previous_runs.sort(key=lambda x: json.loads(x[7])[0]["Number of Trades"], reverse=True)  # Sort by num trades
        elif choice == "Average Profit":
            self.previous_runs.sort(key=lambda x: json.loads(x[7])[0]["Avg Profit"], reverse=True)  # Sort by avg profit
        elif choice == "ROI":
            self.previous_runs.sort(key=lambda x: json.loads(x[7])[0]["ROI"], reverse=True)  # Sort by ROI

        self.create_ui()  # Refresh UI with sorted data

    def plot_stock_chart(self, stock_data: pd.DataFrame, trades: pd.DataFrame, parent):

        # Ensure all indexes are datetime
        stock_data.index = pd.to_datetime(stock_data.index, errors='coerce')
        stock_data = stock_data.dropna(subset=['Open', 'High', 'Low', 'Close'])

        # Convert entry_index and exit_index to datetime
        trades['entry_index'] = pd.to_datetime(trades['entry_index'], unit='ms', errors='coerce')
        trades['exit_index'] = pd.to_datetime(trades['exit_index'], unit='ms', errors='coerce')


        # Set dark mode style
        plt.style.use("dark_background")

        # Create candlestick chart
        fig, ax = plt.subplots(figsize=(10, 6), facecolor="black")
        mpf.plot(
            stock_data,
            type='candle',
            ax=ax,
            style='charles',  # Use a dark mplfinance style
            show_nontrading=True,
        )

        # Add buy markers
        if not trades.empty:
            ax.scatter(
                trades['entry_index'], trades['entry_price'],
                color='lime', label='Entry', marker='^', s=80
            )

        # Add sell markers
        if not trades.empty:
            ax.scatter(
                trades['exit_index'], trades['exit_price'],
                color='orangered', label='Exit', marker='v', s=80
            )

        # Customize the chart
        ax.set_title("Stock Price with Entry and Exit Points", fontsize=14, color="white")
        ax.set_xlabel("Date", fontsize=12, color="white")
        ax.set_ylabel("Price", fontsize=12, color="white")
        ax.legend(facecolor="gray", edgecolor="white")

        # Customize tick colors
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        # Embed the chart in the Tkinter frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        canvas.draw()

    def view_run_details(self, run):

        run_id, date, time, stock_data_json, conditions_json, parameters_json, trades_json, results_data_json = run

        # Deserialize JSON strings
        stock_data = pd.read_json(stock_data_json)
        trades_data = pd.read_json(trades_json)
        conditions = json.loads(conditions_json)
        parameters = json.loads(parameters_json)

        # Calculate metrics
        initialbala = float(parameters[0].get("Initial Investment", 0))
        total_profit = trades_data['profit'].sum() if not trades_data.empty else 0
        win_rate = (trades_data['profit'] > 0).mean() * 100 if not trades_data.empty else 0
        num_trades = len(trades_data)
        avg_profit = trades_data['profit'].mean() if not trades_data.empty else 0
        ROI = (total_profit / initialbala) * 100 if initialbala > 0 else 0

        # Display details in a new window
        details_window = CTk()
        details_window.title(f"Run Details - ID: {run_id}")
        details_window.geometry("900x700")

        # Make a scrollable frame inside the window
        scrollable_details_frame = CTkScrollableFrame(details_window, width=880, height=650)
        scrollable_details_frame.pack(pady=10, expand=True, fill="both")

        CTkLabel(scrollable_details_frame, text=f"Run Date: {date}", fg_color="transparent").pack(pady=5)
        CTkLabel(scrollable_details_frame, text=f"Run Time: {time}", fg_color="transparent").pack(pady=5)
        CTkLabel(scrollable_details_frame, text=f"Conditions: {conditions}", fg_color="transparent").pack(pady=5)
        CTkLabel(scrollable_details_frame, text=f"Parameters: {parameters}", fg_color="transparent").pack(pady=5)

        # Add a candlestick chart
        plot_frame = CTkFrame(scrollable_details_frame, width=1000, height=900)
        plot_frame.pack(pady=10)
        self.plot_stock_chart(stock_data, trades_data, plot_frame)

        # Add metrics
        CTkLabel(scrollable_details_frame, text=f"Initial balance: {initialbala}", fg_color="transparent").pack(pady=5)
        CTkLabel(scrollable_details_frame, text=f"Total Profit: {total_profit}", fg_color="transparent").pack(pady=5)
        CTkLabel(scrollable_details_frame, text=f"Win Rate: {win_rate:.2f}%", fg_color="transparent").pack(pady=5)
        CTkLabel(scrollable_details_frame, text=f"Number of Trades: {num_trades}", fg_color="transparent").pack(pady=5)
        CTkLabel(scrollable_details_frame, text=f"Average Profit: {avg_profit:.2f}", fg_color="transparent").pack(pady=5)
        CTkLabel(scrollable_details_frame, text=f"ROI: {ROI:.2f}%", fg_color="transparent").pack(pady=5)

        CTkButton(scrollable_details_frame, text="Close", fg_color="#C850C0", hover_color=("#4158D0"), command=details_window.destroy).pack(pady=10)
        details_window.mainloop()

    def back_to_mainmenu(self):
        self.app.destroy()
        from MainMenu import MainMenu
        mainmenu = MainMenu(self.user_id)
        mainmenu.run()

    def run(self):

        self.app.mainloop()

# Example usage:
# Replace 1 with the actual user ID
if __name__ == "__main__":
    app = PreviousRunsWindow(user_id=1)
    app.run()