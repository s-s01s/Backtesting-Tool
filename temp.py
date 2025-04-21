from customtkinter import CTk, CTkButton, CTkLabel, CENTER, set_appearance_mode


class MainMenu():
    def __init__(self):

        # Create main menu window
        self.app = CTk()
        self.app.geometry('400x300')
        self.app.title("Main Menu")
        self.app.resizable(0, 0)
        set_appearance_mode("dark")

        self.create_ui()

    def create_ui(self):
        """
        Create UI components for the main menu.
        """
        # Title label
        title = CTkLabel(self.app, text="Main Menu", width=200, height=50, fg_color="#C850C0")
        title.place(relx=0.5, rely=0.2, anchor=CENTER)

        # View Previous Runs button
        view_previous_runs_button = CTkButton(
            master=self.app,
            text="View Previous Runs",
            corner_radius=10,
            width=200,
            command=self.view_previous_runs,
        )
        view_previous_runs_button.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Proceed to Backtest button
        backtest_button = CTkButton(
            master=self.app,
            text="Proceed to Backtest",
            corner_radius=10,
            width=200,
            command=self.proceed_to_backtest,
        )
        backtest_button.place(relx=0.5, rely=0.7, anchor=CENTER)



    def proceed_to_backtest(self):

        self.app.destroy()
        from StrategySelection import StrategySelectionWindow
        print("Proceeding to strategy selection...")
        strat = StrategySelectionWindow(self.user_id)
        strat.run()

    def run(self):

        self.app.mainloop()


m = MainMenu()
m.run()