from customtkinter import *
import sqlite3
from datetime import date, datetime
from PIL import Image, ImageTk
import re
from StrategySelection import StrategySelectionWindow


emailregex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$' # Simple regex for email validation
passwordregex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
app=CTk()


conn = sqlite3.connect('database.db')

cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            fname text NOT NULL,
            lname text NOT NULL,
            email text NOT NULL,
            password text NOT NULL,
            created_date text NOT NULL,
            created_time text NOT NULL
            );""")

cursor.execute(
    """CREATE TABLE IF NOT EXISTS previousRuns (
            id INTEGER PRIMARY KEY,
            date text NOT NULL,
            time text NOT NULL,
            stock_data text NOT NULL,
            conditions text NOT NULL,
            parameters text NOT NULL,
            trades_data text NOT NULL,
            results_data text NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
            );""")
conn.commit()

caLbl = None
def createAccountForm():# Opens a new window (frontmost) for the user to enter details for new account, which will then be saved to database.
    def accountToDb():
        global caLbl
        if caLbl is not None:
            caLbl.destroy()
        temp = datetime.now()
        currentDate = temp.strftime("%m/%d/%Y") #For saving to database
        currentTime = temp.strftime("%H:%M:%S")
        if caFname.get() == "" or caLname.get() == "" or caEmail.get() == "" or caPassword.get() == "":
            caLbl = CTkLabel(cawindow, text="Fields cannot be empty.", fg_color="transparent", text_color="red")
            caLbl.place(relx=0.5, rely=0.25, anchor=CENTER)
        elif re.match(emailregex, caEmail.get()) is None:
            caLbl = CTkLabel(cawindow, text="Please enter a valid email.", fg_color="transparent", text_color="red")
            caLbl.place(relx=0.5, rely=0.25, anchor=CENTER)
        elif re.match(passwordregex, caPassword.get()) is None:
            caLbl = CTkLabel(cawindow, text="Password must contain uppercase and lowercase \nletters, numbers and special characters.", fg_color="transparent", text_color="red")
            caLbl.place(relx=0.5, rely=0.25, anchor=CENTER)
        elif caPassword.get() != caPassword2.get():
            caLbl = CTkLabel(cawindow,text="Passwords must match.",fg_color="transparent", text_color="red")
            caLbl.place(relx=0.5, rely=0.25, anchor=CENTER)
        else:
            cursor.execute("""INSERT INTO users (fname, lname, email, password, created_date, created_time) 
                       VALUES(?, ?, ?,?, ?, ?)""",
                       (caFname.get(), caLname.get(), caEmail.get(), caPassword.get(), currentDate, currentTime))
            conn.commit()
            caLbl = CTkLabel(cawindow, text="Successfully created account! Please proceed to login.", fg_color="transparent", text_color="green")
            caLbl.place(relx=0.5, rely=0.25, anchor=CENTER)
    cawindow = CTkToplevel(app)
    cawindow.attributes('-topmost', True)
    cawindow.geometry('375x425')
    cawindow.resizable(0, 0)
    label = CTkLabel(master=cawindow, text="ITT", fg_color="#C850C0", width=100, height=50)
    label.place(relx=0.5, rely=0.13, anchor=CENTER)

    cawindow.title("Create Account")
    caFname = CTkEntry(master=cawindow, placeholder_text="First name...", width=300, text_color="#FFCC70")
    caFname.place(relx=0.1, rely=0.3)
    caLname = CTkEntry(master=cawindow, placeholder_text="Last name...", width=300, text_color="#FFCC70")
    caLname.place(relx=0.1, rely=0.4)
    caEmail = CTkEntry(master=cawindow, placeholder_text="Your Email...", width=300, text_color="#FFCC70")
    caEmail.place(relx=0.1, rely=0.5)
    caPassword = CTkEntry(master=cawindow, show="*", placeholder_text="Create Password...", width=300, text_color="#FFCC70")
    caPassword.place(relx=0.1, rely=0.6)
    caPassword2 = CTkEntry(master=cawindow, show="*", placeholder_text="Re-enter Password...", width=300, text_color="#FFCC70")
    caPassword2.place(relx=0.1, rely=0.7)
    caProceedBtn = CTkButton(master=cawindow, text="Proceed", corner_radius=32, fg_color="#C850C0", hover_color=("#4158D0"), border_width=2, command=accountToDb)
    caProceedBtn.place(relx=0.5, rely=0.875, anchor=CENTER)


#Below is the code for the login window

app.geometry('375x325')
app.title("ITT")
app.resizable(0,0)
set_appearance_mode("dark")
label = CTkLabel(master=app, text="ITT", fg_color="#C850C0", width=100, height=50)
label.place(relx=0.5, rely=0.16, anchor=CENTER)


def openMainMenu(email):
    from MainMenu import MainMenu
    user_id = cursor.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    user_id = user_id[0]
    main_menu = MainMenu(user_id)  # Initialize the Main Menu
    main_menu.run()  # Run the Main Menu


loginlbl=None # for error label
def loginfunc():
    global loginlbl
    # Clear the previous error label if it exists
    if loginlbl is not None:
        loginlbl.destroy()

    email_input = email.get()
    password_input = password.get()

    # Check for empty fields
    if email_input == "" or password_input == "":
        loginlbl = CTkLabel(app, text="Fields cannot be empty.", fg_color="transparent", text_color="red")
        loginlbl.place(relx=0.5, rely=0.925, anchor=CENTER)
        return
    # Check for valid email
    if re.match(emailregex, email_input) is None:
        loginlbl = CTkLabel(app, text="Please enter a valid email.", fg_color="transparent", text_color="red")
        loginlbl.place(relx=0.5, rely=0.925, anchor=CENTER)
        return
    # Retrieve user from the database
    user = cursor.execute("SELECT password FROM users WHERE email = ?", (email_input,)).fetchone()
    # Check if user exists
    if user is None:
        loginlbl = CTkLabel(app, text="Invalid email or password!", fg_color="transparent", text_color="red")
        loginlbl.place(relx=0.5, rely=0.925, anchor=CENTER)
        return
    # Check if the password matches
    if password_input == user[0]:
        loginlbl = CTkLabel(app, text="Logged in successfully!", fg_color="transparent", text_color="green")
        loginlbl.place(relx=0.5, rely=0.925, anchor=CENTER)
        app.destroy()
        openMainMenu(email_input)  # Open the main menu
    else:
        loginlbl = CTkLabel(app, text="Invalid email or password!", fg_color="transparent", text_color="red")
        loginlbl.place(relx=0.5, rely=0.925, anchor=CENTER)


email = CTkEntry(master=app, placeholder_text="Your Email...", width=300, text_color="#FFCC70")
email.place(relx=0.1, rely=0.325)
password = CTkEntry(master=app, show="*", placeholder_text="Your Password...", width=250, text_color="#FFCC70")
password.place(relx=0.1, rely=0.45)

eo = Image.open(r"eye.png") # images for the show/hide password button.
eyeopen = ImageTk.PhotoImage(eo)
ec = Image.open(r"eye-line.png")
eyeclosed = ImageTk.PhotoImage(ec)

passVis=False
def togFunc():
    global passVis
    print(f"Current state: {passVis}")
    if passVis:
        toggle_btn.configure(image=eyeopen)
        password.configure(show="*")
        passVis = False
    else:
        toggle_btn.configure(image=eyeclosed)
        password.configure(show="")
        passVis = True

toggle_btn = CTkButton(master=app, text = "", width=25, image=eyeopen, fg_color="#C850C0", hover_color=("#4158D0"), command=togFunc)
toggle_btn.place(relx=0.79, rely=0.45)

loginBtn = CTkButton(master=app, text="Login", corner_radius=32, fg_color="#C850C0", hover_color=("#4158D0"), border_width=2, command=loginfunc)
loginBtn.place(relx=0.5, rely=0.675, anchor=CENTER)

createaccbtn = CTkButton(master=app, text="Create Account", corner_radius=32, fg_color="#C850C0", hover_color=("#4158D0"), border_width=2, command=createAccountForm)
createaccbtn.place(relx=0.5, rely=0.8, anchor=CENTER)

app.mainloop()