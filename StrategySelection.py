from customtkinter import CTk, CTkComboBox, CTkButton, CTkLabel, CTkScrollableFrame, StringVar, set_appearance_mode, \
    CENTER, CTkEntry
import threading
import yfinance as yf


class StrategySelectionWindow:
    def __init__(self, user_id):
        # Store user-specific data
        self.user_id = user_id
        print(f"Initialising Strategy Selection for User ID: {self.user_id}")

        # Initialise the app window
        self.app = CTk()
        self.app.geometry('390x450')  # Increased height for better layout with scrollable frame
        self.app.title("ITT")
        self.app.resizable(0, 0)
        set_appearance_mode("dark")

        # Placeholder for stock data
        self.df = None
        self.data_downloaded = False  # Flag to track download status

        # Initialise UI elements
        self.error_label = None  # Persistent error label placeholder
        self.conditions = []
        self.current_row = 0  # Row tracker for grid placement
        self.create_ui()

        # Start downloading stock data in a separate thread
        threading.Thread(target=self.download_stock_data, daemon=True).start()

    def download_stock_data(self):

        print("Downloading stock data...")
        self.df = yf.download("TSLA", start="2013-01-01", end="2024-01-01", interval="1d")
        if not self.df.empty:
            print("Successfully downloaded stock data.")
            # Enable save button
            self.save_button.configure(state="enabled")
        else:
            print("Error downloading stock data.")
            self.update_error_message("Error downloading stock data. Please try again later.")

    def create_ui(self):

        # Title label
        label = CTkLabel(master=self.app, text="ITT", fg_color="#C850C0", width=100, height=50)
        label.place(relx=0.5, rely=0.1, anchor=CENTER)

        # Scrollable frame for conditions
        self.condition_frame = CTkScrollableFrame(master=self.app, width=365, height=225)
        self.condition_frame.place(relx=0.5, rely=0.45, anchor="center")

        # Initialise first row
        self.add_condition_row()

        # Buttons

        CTkButton(master=self.app, text="Back", corner_radius=32, width=25, fg_color="#C850C0",
                                     hover_color="#4158D0", border_width=2, command=self.back_to_mainmenu).place(relx=0.25, rely=0.9, anchor=CENTER)

        CTkButton(master=self.app, text="+", corner_radius=10, width=25, fg_color="#C850C0",
                  hover_color="#4158D0", border_width=2, command=self.add_condition_row).place(relx=0.55, rely=0.9, anchor=CENTER)

        CTkButton(master=self.app, text="-", corner_radius=10, width=25, fg_color="#C850C0",
                  hover_color="#4158D0", border_width=2, command=self.remove_last_row).place(relx=0.45, rely=0.9, anchor=CENTER)

        self.save_button = CTkButton(master=self.app, text="Save", corner_radius=32, width=25, fg_color="#C850C0",
                                     hover_color="#4158D0", border_width=2, command=self.save_conditions)
        self.save_button.place(relx=0.75, rely=0.9, anchor=CENTER)
        self.save_button.configure(state="disabled")  # Disable until data is ready

        # Parameter input fields
        self.takeprof = CTkEntry(self.app, placeholder_text="Take Profit", width=100)
        self.takeprof.place(relx=0.815, rely=0.79, anchor=CENTER)
        self.stoploss = CTkEntry(self.app, placeholder_text="Stop Loss", width=100)
        self.stoploss.place(relx=0.185, rely=0.79, anchor=CENTER)
        self.initialinv = CTkEntry(self.app, placeholder_text="Initial Investment", width=120)
        self.initialinv.place(relx=0.5, rely=0.79, anchor=CENTER)

    def add_condition_row(self):

        comboboxInd1_var = StringVar(value="BBW")
        comboboxInd1 = CTkComboBox(self.condition_frame, values=["SMA5", "SMA15","SMA45","SMA150", "BBW", "RSI", "MACD", "ATR", "Close"],
                                   variable=comboboxInd1_var, state="readonly")
        comboboxInd1.grid(row=self.current_row, column=0, padx=5, pady=5)

        comboboxCond_var = StringVar(value="=")
        comboboxCond = CTkComboBox(self.condition_frame, values=["=", "<", ">"],
                                   variable=comboboxCond_var, state="readonly", width=50)
        comboboxCond.grid(row=self.current_row, column=1, padx=5, pady=5)

        comboboxInd2_var = StringVar(value="BBW")
        comboboxInd2 = CTkComboBox(self.condition_frame, values=["SMA5", "SMA15","SMA45","SMA150", "BBW", "RSI", "MACD", "ATR", "Close"],
                                   variable=comboboxInd2_var, state="readonly")
        comboboxInd2.grid(row=self.current_row, column=2, padx=5, pady=5)

        # Save condition
        self.conditions.append({
            'indicator1': comboboxInd1,
            'condition': comboboxCond,
            'indicator2': comboboxInd2
        })
        self.current_row += 1

    def remove_last_row(self):

        if self.current_row == 1:
            print("There must be at least one condition.")
            return

        last_condition = self.conditions.pop()
        last_condition['indicator1'].grid_forget()
        last_condition['condition'].grid_forget()
        last_condition['indicator2'].grid_forget()
        self.current_row -= 1

    def has_duplicate_conditions(self):

        condition_set = set()
        for cond in self.conditions:
            indicator1 = cond['indicator1'].get()
            condition = cond['condition'].get()
            indicator2 = cond['indicator2'].get()

            # Normalise condition strings
            if condition == ">":
                normalised = f"{indicator1} > {indicator2}"
                reverse_normalised = f"{indicator2} < {indicator1}"
            elif condition == "<":
                normalised = f"{indicator1} < {indicator2}"
                reverse_normalised = f"{indicator2} > {indicator1}"
            elif condition == "=":
                normalised = f"{indicator1} = {indicator2}"
                reverse_normalised = normalised  # Equality is symmetric

            # Check if either the condition or its reverse is already in the set
            if normalised in condition_set or reverse_normalised in condition_set:
                return True  # Duplicate or reverse condition found

            # Add the normalised condition to the set
            condition_set.add(normalised)

        return False


    def save_conditions(self):

        if self.df is None:
            print("Stock data not downloaded yet. Please wait.")
            return

        if self.has_duplicate_conditions():
            self.update_error_message("Duplicate or reverse conditions detected. Please review your conditions.")
            return  # Exit if duplicate or reverse conditions are found

        if not self.validate_inputs():
            return  # Exit early if validation fails


        if self.initialinv.get() == '':
            print("Initial Investment none.")
        strategy_conditions = []
        parameters = {
            'Initial Investment': self.initialinv.get(),
            'Stop Loss': self.stoploss.get(),
            'Take Profit': self.takeprof.get()
        }
        for cond in self.conditions:
            if cond['indicator1'].get() == cond['indicator2'].get():
                self.update_error_message("Indicators in a condition cannot be the same.")
                return

        for cond in self.conditions:
            strategy_conditions.append({
                'indicator1': cond['indicator1'].get(),
                'condition': cond['condition'].get(),
                'indicator2': cond['indicator2'].get()
            })

        print("Strategy Conditions:", strategy_conditions)
        print("Parameters:", parameters)


        from Backtest import Backtest
        backtest = Backtest(self.user_id, self.df, strategy_conditions, parameters, self)
        success = backtest._execute_backtest()

        if not success:
            print("No trades were executed. Keeping Strategy Selection Window open.")
            self.notify_no_trades()

    def update_error_message(self, message):

        if self.error_label:
            self.error_label.destroy()  # Remove the previous label

        if message:
            self.error_label = CTkLabel(
                master=self.app,
                text=message,
                fg_color="transparent",
                text_color="red"
            )
            self.error_label.place(relx=0.5, rely=0.97, anchor=CENTER)

    def validate_inputs(self):

        error_messages = []

        # Validate Initial Investment
        try:
            initial_investment = float(self.initialinv.get())
            if initial_investment <= 0:
                error_messages.append("Initial Investment must be greater than 0.")
        except ValueError:
            error_messages.append("Initial Investment must be a valid number.")

        # Validate Stop Loss
        try:
            stop_loss = float(self.stoploss.get())
            if stop_loss <= 0 or stop_loss > 1:
                error_messages.append("Stop Loss must be between 0 and 1 (exclusive).")
        except ValueError:
            error_messages.append("Stop Loss must be a valid number.")

        # Validate Take Profit
        try:
            take_profit = float(self.takeprof.get())
            if take_profit <= 0 or take_profit > 1:
                error_messages.append("Take Profit must be between 0 and 1 (exclusive).")
        except ValueError:
            error_messages.append("Take Profit must be a valid number.")

        if error_messages:
            self.update_error_message("\n".join(error_messages))  # Show errors
            return False

        # Clear the error message if validation succeeds
        self.update_error_message("")
        return True

    def notify_no_trades(self):

        self.update_error_message("No trades were executed. Please adjust your strategy.")

    def back_to_mainmenu(self):
        self.app.destroy()
        from MainMenu import MainMenu
        mainmenu = MainMenu(self.user_id)
        mainmenu.run()

    def run(self):

        print("Inside StrategySelectionWindow.__init__()")

        self.app.mainloop()

s = StrategySelectionWindow(1)
s.run()