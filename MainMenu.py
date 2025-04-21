from customtkinter import CTk, CTkButton, CTkLabel, CENTER, set_appearance_mode


class MainMenu:
    def __init__(self, user_id):
        self.user_id = user_id
        print(f"Main Menu for User ID: {user_id}")

        # Create main menu window
        self.app = CTk()
        self.app.geometry('350x250')
        self.app.title("Main Menu")
        self.app.resizable(0, 0)
        set_appearance_mode("dark")


        self.create_ui()

    def create_ui(self):

        # Title label
        title = CTkLabel(self.app, text="Main Menu", width=200, height=50, fg_color="#C850C0")
        title.place(relx=0.5, rely=0.2, anchor=CENTER)

        # View Previous Runs button
        view_previous_runs_button = CTkButton(
            master=self.app,
            text="Previous Runs",
            corner_radius=32, width=25, fg_color="#C850C0",
            hover_color="#4158D0", border_width=1,
            command=self.view_previous_runs,
        )
        view_previous_runs_button.place(relx=0.3, rely=0.54, anchor=CENTER)

        # Proceed to Backtest button
        backtest_button = CTkButton(
            master=self.app,
            text="New Backtest",
            corner_radius=32, width=25, fg_color="#C850C0",
            hover_color="#4158D0", border_width=1,
            command=self.proceed_to_backtest,
        )
        backtest_button.place(relx=0.7, rely=0.54, anchor=CENTER)

        exit_button = CTkButton(
            master=self.app,
            text="Exit",
            corner_radius=32, width=25, fg_color="#C850C0",
            hover_color="#4158D0", border_width=1,
            command=self.exit,
        )
        exit_button.place(relx=0.5, rely=0.8, anchor=CENTER)

    def view_previous_runs(self):
        print("Viewing previous runs...")
        self.app.destroy()
        from PreviousRuns import PreviousRunsWindow
        PreviousRunsWindow(self.user_id).run()

    def proceed_to_backtest(self):
        print("Proceeding to strategy selection...")
        self.app.destroy()
        from StrategySelection import StrategySelectionWindow
        StrategySelectionWindow(self.user_id).run()

    def exit(self):
        print("Exiting application...")
        import sys
        sys.exit()


    def run(self):

        self.app.mainloop()

m = MainMenu(1)
m.run()