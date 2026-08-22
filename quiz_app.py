from datetime import datetime
import os           
from fpdf import FPDF
import time
import tkinter as tk
from tkinter import StringVar, ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
from database import DatabaseManager
from Style import BaseApp
import subprocess
import platform
import re

class QuizAPP(BaseApp):
    def __init__(self):
        super().__init__()  
        self.title("Quiz APP")
        self.geometry("1000x667")
        self.iconbitmap(r"F:\QuizApp\quiz_icon.ico")
        self.configure(bg="RoyalBlue4")
        self.__current_users = None
        self.current_quiz_questions = []
        self.current_question_index = 0
        self.user_answers = []
        self.score = 0
        self.last_cert_path = None
        self.test_start_time = 0
        self.__time_limit = 40 
        self.db = DatabaseManager()
        self.setup_background()
        self.main_menu()
        self.connection=mysql.connector.connect(**DB_CONFIG)
        if not self.db.connect():
            messagebox.showerror("Error", "Database connection failed.")
            return
        self.cursor=self.connection.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            role VARCHAR(50)
        )
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS quiz_scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            quiz_title VARCHAR(100) NOT NULL,
            score INT NOT NULL,
            total_questions INT NOT NULL,
            percentage FLOAT NOT NULL,
            date_taken DATETIME NOT NULL)
        """)
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            rating INT,
            review TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP)
        """)
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS certificates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                quiz_title VARCHAR(100),
                awarded_on DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)


        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", ('admin', 'admin123', 'Admin'))
            self.connection.commit()

            
    def main_menu(self):
        self.clear_screen()
        top_bar = tk.Frame(self, bg="blue", height=40)
        top_bar.pack(fill=tk.X)
        frame = tk.Frame(self, bg="floral white")
        frame.pack(expand=True, fill='both', padx=170, pady=50)        
        self.setup_robot(self.Help,frame)
        ttk.Label(frame, text="Welcome to Quiz App", style='Title.TLabel').pack(pady=50)


        tk.Button(top_bar,text='About',command=self.AboutApp,bg='red',fg='white',font=("Arial", 12),padx=10,pady=5).pack(side='right', padx=10)
        ttk.Button(frame, text="Sign Up",command=self.Sign_up).pack(pady=5)
        ttk.Button(frame, text="Login",  command=self.Login).pack(pady=5)
        ttk.Button(frame, text="Exit",command=self.exit_app).pack(pady=5)

    def Sign_up(self):
        self.clear_screen()
        frame = self.create_screen()

        ttk.Label(frame, text="Sign Up Page", style='Title.TLabel').pack(pady=30)

        # Username
        ttk.Label(frame, text="Username", style='Text.TLabel').pack(pady=(10, 0))
        username_entry = tk.Entry(frame, width=30, font=("Arial", 14),fg='red',bd=3,highlightthickness=2)
        username_entry.pack()
        username_error = tk.Label(frame, text="", fg="red", font=("Arial", 12))
        username_error.pack()

        def clear_username_error(e): username_error.config(text="")
        username_entry.bind("<KeyRelease>", clear_username_error)

        # Password
        ttk.Label(frame, text="Password", style='Text.TLabel').pack(pady=(10, 0))
        password_frame = tk.Frame(frame)
        password_frame.pack()
        password_var = tk.StringVar()
        password_entry = tk.Entry(password_frame, textvariable=password_var, show="*", width=28, font=("Arial", 14),fg='red',bd=3,highlightthickness=2)
        password_entry.pack(side='left')

        def toggle_password():
            if password_entry.cget('show') == '*':
                password_entry.config(show='')
                show_btn.config(text='👁️')
            else:
                password_entry.config(show='*')
                show_btn.config(text='🙈')

        show_btn = ttk.Button(password_frame, text='🙈', width=3, command=toggle_password)
        show_btn.pack(side='right')

        password_error = tk.Label(frame, text="", fg="red", font=("Arial", 12))
        password_error.pack()

        def clear_password_error(e): password_error.config(text="")
        password_entry.bind("<KeyRelease>", clear_password_error)

        # Role Dropdown
        ttk.Label(frame, text="Role", style='Text.TLabel').pack(pady=(10, 0))
        roles = ["User"]
        selected_role = tk.StringVar()
        role_dropdown = ttk.Combobox(frame, textvariable=selected_role, values=roles, state="readonly", font=("Arial", 14), width=28,foreground='red')
        role_dropdown.pack()
        role_error = tk.Label(frame, text="", fg="red", font=("Arial", 12))
        role_error.pack()

        def clear_role_error(e): role_error.config(text="")
        role_dropdown.bind("<<ComboboxSelected>>", clear_role_error)

        # Signup logic
        def Sign_up_check():
            username = username_entry.get().strip()
            password = password_var.get().strip()
            role = selected_role.get().strip()

            username_error.config(text="")
            password_error.config(text="")
            role_error.config(text="")

            valid = True
            if not username or not re.match("^[A-Za-z]+$", username):
                username_error.config(text="Username must contain only letters.")
                valid = False

            if not password:
                password_error.config(text="Password is required.")
                valid = False
            elif len(password) < 6 or not re.search("[A-Z]", password) or not re.search("[a-z]", password) or not re.search("[0-9]", password):
                password_error.config(text="Weak password: use A-Z, a-z, 0-9.")
                valid = False

            if not role:
                role_error.config(text="Please select a role.")
                valid = False

            if not valid:
                return

            self.cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            if self.cursor.fetchone():
                username_error.config(text="Username already exists.")
                return

            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
            self.connection.commit()
            self.speak(f"Dear {username}, your account is created for {role} role,Now you can login into your account")
            self.main_menu()

        # Button section
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Register", command=Sign_up_check, width=15).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=self.main_menu, width=15).grid(row=0, column=1, padx=10)


    def Login(self):
        self.clear_screen()
        frame = self.create_screen()

        ttk.Label(frame, text="Login Page", style='Title.TLabel').pack(pady=30)

        # Variables
        self.login_attempts = getattr(self, "login_attempts", 0)
        self.blocked = getattr(self, "blocked", False)

        # Username
        ttk.Label(frame, text="Username", style='Text.TLabel').pack()
        username_entry = tk.Entry(frame, width=30, font=("Arial", 14),fg='red',bd=3,highlightthickness=2)
        username_entry.pack()
        username_error = tk.Label(frame, text="", fg="red", font=("Arial", 12))
        username_error.pack()

        def clear_username_error(e): username_error.config(text="")
        username_entry.bind("<KeyRelease>", clear_username_error)

        # Password
        ttk.Label(frame, text="Password", style='Text.TLabel').pack(pady=(10, 0))
        password_frame = tk.Frame(frame)
        password_frame.pack()
        password_var = tk.StringVar()
        password_entry = tk.Entry(password_frame, textvariable=password_var, show="*", width=28, font=("Arial", 14),fg='red',bd=3,highlightthickness=2)
        password_entry.pack(side='left')

        def toggle_password():
            if password_entry.cget('show') == '*':
                password_entry.config(show='')
                toggle_btn.config(text='👁️')
            else:
                password_entry.config(show='*')
                toggle_btn.config(text='🙈')

        toggle_btn = ttk.Button(password_frame, text='🙈', width=3, command=toggle_password)
        toggle_btn.pack(side='right')

        password_error = tk.Label(frame, text="", fg="red", font=("Arial", 12))
        password_error.pack()

        def clear_password_error(e): password_error.config(text="")
        password_entry.bind("<KeyRelease>", clear_password_error)

        # Role Dropdown
        ttk.Label(frame, text="Role", style='Text.TLabel').pack(pady=(10, 0))
        roles = ["Admin", "User"]
        selected_role = tk.StringVar()
        role_dropdown = ttk.Combobox(frame, textvariable=selected_role, values=roles, state="readonly", font=("Arial", 14), width=28)
        role_dropdown.pack()
        role_error = tk.Label(frame, text="", fg="red", font=("Arial", 12))
        role_error.pack()

        def clear_role_error(e): role_error.config(text="")
        role_dropdown.bind("<<ComboboxSelected>>", clear_role_error)

        # Status message
        login_status = tk.Label(frame, text="", fg="red", font=("Arial", 12))
        login_status.pack(pady=(10, 0))

        # --- Countdown Block Timer ---
        def block_login():
            self.blocked = True
            self.login_attempts = 0
            remaining = [10]

            def countdown():
                if remaining[0] > 0:
                    login_status.config(text=f"Too many attempts. Try again in {remaining[0]} seconds.")
                    remaining[0] -= 1
                    login_status.after(1000, countdown)
                else:
                    self.blocked = False
                    login_status.config(text="Now you can login.")

            countdown()

        # --- Login Check Logic ---
        def Login_check():
            username = username_entry.get().strip()
            password = password_var.get().strip()
            role = selected_role.get().strip()

            # Reset error messages
            username_error.config(text="")
            password_error.config(text="")
            role_error.config(text="")
            login_status.config(text="")

            if self.blocked:
                login_status.config(text="Login is temporarily disabled. Please wait...")
                return

            valid = True
            if not username:
                username_error.config(text="Username is required.")
                valid = False
            if not password:
                password_error.config(text="Password is required.")
                valid = False
            if not role:
                role_error.config(text="Please select a role.")
                valid = False
            if not valid:
                return

            self.cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s AND role=%s", (username, password, role))
            result = self.cursor.fetchone()

            if result:
                self.login_attempts = 0
                self.__current_users = username
                if role == 'User':
                    self.User_Dashboard()
                elif role == 'Admin':
                    self.Admin_Dashboard()
            else:
                self.login_attempts += 1
                if self.login_attempts >= 3:
                    block_login()
                else:
                    login_status.config(text=f"Invalid credentials. Attempts left: {3 - self.login_attempts}")

        # --- Buttons ---
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Login", command=Login_check, width=15).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=self.main_menu, width=15).grid(row=0, column=1, padx=10)



    def User_Dashboard(self):
        self.clear_screen()
        frame = self.create_screen()
        username=self.__current_users

        title_label = ttk.Label(frame, text=f"Welcome Dear {username}!", style='Title.TLabel')
        title_label.pack(pady=50)
    
        
        ttk.Button(frame, text="Start Quiz",command= self.Welcome_Screen).pack(pady=5)
        ttk.Button(frame, text="leaderboard",command= self.show_quiz_selection).pack(pady=5)
        ttk.Button(frame, text="Ratings",command=self.check_review).pack(pady=5)
        ttk.Button(frame, text="Logout",command=self.main_menu).pack(pady=5)
        frame.after(100, lambda: self.speak(f"Welcome dear {username}, we hope you are feeling well today"))

    def Admin_Dashboard(self):
        self.clear_screen()
        top_bar = tk.Frame(self, bg="blue", height=40)
        top_bar.pack(fill=tk.X)
        frame = self.create_screen()

        title_label = ttk.Label(frame, text="Admin Dashboard", style='Title.TLabel')
        title_label.pack(pady=50)


        tk.Label(top_bar, text="Welcome Dear Admin!",fg='white',bg='blue',font=('Arial',12)).pack(side=tk.LEFT, padx=10)

        ttk.Button(frame, text="Recipient's",command=self.Recipients).pack(pady=5)
        ttk.Button(frame, text="User Score",command=self.show_quiz_selection).pack(pady=5)
        tk.Button(top_bar, text="Delete User",command=self.Recipients_Delete).pack(side=tk.RIGHT, padx=10, pady=10)
        tk.Button(top_bar, text="See certificates",command=self.open_certificate_viewer).pack(side=tk.RIGHT, padx=10, pady=10)
        ttk.Button(frame, text="Add Question",command=self.show_create_quiz).pack(pady=5)
        tk.Button(top_bar, text="Drop Table",command=self.table_drop).pack(side=tk.RIGHT, padx=10, pady=10)
        ttk.Button(frame, text="Logout",command=self.main_menu).pack(pady=5)
        self.speak(f"Welcome dear admin, we hope you are feeling well today")
    def table_drop(self):
        self.clear_screen()
        frame = self.create_screen()

        title_label = ttk.Label(frame, text="Drop Table", style='Title.TLabel')
        title_label.pack(pady=30)

        # Label for dropdown
        ttk.Label(frame, text="Select a table to drop:", style='Text.TLabel').pack(pady=10)

        # Try to fetch tables
        try:
            self.cursor.execute("SHOW TABLES FROM `quiz_data`")
            self.connection.commit()
            tables = self.cursor.fetchall()
            table_names = [table[0] for table in tables]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch tables:\n{e}")
            return

        # Dropdown to show table names
        table_combo = ttk.Combobox(frame, values=table_names, font=("Arial", 12), width=30)
        table_combo.pack(pady=10)

        # Drop button
        def drop_table():
            table_name = table_combo.get().strip()
            if not table_name:
                messagebox.showwarning("Input Error", "Please select a table name.")
                return

            confirm = messagebox.askyesno("Confirm Drop", f"Are you sure you want to drop the table '{table_name}'?")
            if not confirm:
                return

            try:
                self.cursor.execute(f"DROP TABLE IF EXISTS `quiz_data`.`{table_name}`")
                self.connection.commit()
                messagebox.showinfo("Success", f"Table '{table_name}' dropped successfully!")
                
                # Refresh dropdown
                self.cursor.execute("SHOW TABLES FROM `quiz_data`")
                new_tables = [t[0] for t in self.cursor.fetchall()]
                table_combo['values'] = new_tables
                table_combo.set("")

            except Exception as e:
                messagebox.showerror("Error", f"Could not drop table:\n{e}")

        # Buttons
        tk.Button(frame, text="Drop Table", font=("Arial", 12, "bold"),
                bg="red", fg="white", command=drop_table).pack(pady=20)

        ttk.Button(frame, text="Back", command=self.Admin_Dashboard).pack(pady=5)

    def Recipients(self):
        self.clear_screen()
        frame = self.create_screen()

        title_label = ttk.Label(frame, text="RECIPIENT'S", style='Title.TLabel')
        title_label.pack(pady=50)

        # Fetch all usernames from database where role is 'User'
        self.cursor.execute("SELECT username FROM users WHERE role = 'User'")
        self.connection.commit()
        users = self.cursor.fetchall()

        for index, user in enumerate(users, start=1):
            ttk.Label(frame, text=f"{index}. {user[0]}", style='TexT.TLabel').pack(anchor="center", fill='x', padx=20, pady=3)
        ttk.Button(frame, text="Back", command=self.Admin_Dashboard).pack(pady=5)


    def Recipent_score(self, quiz_title):
        """Show leaderboard for a selected quiz title"""
        self.clear_screen()
        frame = self.create_screen()

        ttk.Label(frame, text=f"Leaderboard - {quiz_title}", font=("Arial", 20)).pack(pady=10)

        try:
            query = """
            SELECT username, score, percentage
            FROM quiz_scores
            WHERE quiz_title = %s
            ORDER BY score DESC
            LIMIT 10
            """
            self.cursor.execute(query, (quiz_title,))
            self.connection.commit()
            results = self.cursor.fetchall()

            if not results:
                ttk.Label(frame, text="No scores yet for this quiz.", font=("Arial", 14)).pack(pady=20)
            else:
                for i, (username, score, percentage) in enumerate(results, start=1):
                    ttk.Label(frame, text=f"{i}. {username} - {score} ({percentage}%)", style='TexT.TLabel').pack(anchor="w", padx=30)

        except Error as e:
            ttk.Label(frame, text=f"Error loading leaderboard: {e}", foreground="red").pack(pady=10)

        ttk.Button(frame, text="Back", command=self.Message).pack(pady=5)
        ttk.Button(frame, text="Back", command=self.User_Dashboard).pack(pady=5)
    
    def Recipients_Delete(self):
        self.clear_screen()
        frame = self.create_screen()

        title_label = ttk.Label(frame, text="Recipient's", style='Title.TLabel')
        title_label.pack(pady=30)

        # Fetch all recipients
        self.cursor.execute("SELECT id, username FROM users WHERE role = 'User'")
        recipients = self.cursor.fetchall()

        if not recipients:
            ttk.Label(frame, text="No recipients found.", style='Text.TLabel').pack(pady=20)
            ttk.Button(frame, text="Back", command=self.Admin_Dashboard).pack(pady=5)
            return

        # Combobox to select user
        ttk.Label(frame, text="Select Recipient to Delete", style='Text.TLabel').pack()
        user_dict = {f"{username} (ID: {user_id})": user_id for user_id, username in recipients}
        selected_user = tk.StringVar()
        user_dropdown = ttk.Combobox(frame, textvariable=selected_user, values=list(user_dict.keys()), state="readonly", width=30)
        user_dropdown.pack(pady=10)

        # Delete button
        def delete_recipient():
            selected = selected_user.get()
            if not selected:
                messagebox.showerror("Error", "Please select a recipient.")
                return
            user_id = user_dict[selected]
            try:
                self.cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                self.connection.commit()
                messagebox.showinfo("Success", f"Recipient {selected} deleted.")
                self.speak(f"Recipient {selected} deleted from your database.")
                self.Recipients_Delete()  # Refresh the screen
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(frame, text="Delete", command=delete_recipient).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.Admin_Dashboard).pack(pady=5)

    def show_create_quiz(self):
        """Show the quiz creation interface"""
        self.clear_screen()
        frame = self.create_screen()
        
        # Title
        title_label = ttk.Label(frame, text="Create New Quiz", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Timer Label 
        timer_frame = tk.Frame(frame, bg='floral white')
        timer_frame.place(relx=1.0, x=-20, y=10, anchor='ne')  

        ttk.Label(timer_frame, text="Quiz Time (mins):", font=("Arial", 14)).pack(side='left', padx=5)

        self.quiz_time = tk.IntVar(value=10)
        time_spinbox = tk.Spinbox(
            timer_frame,
            from_=10,
            to=120,
            increment=10,
            textvariable=self.quiz_time,
            font=("Arial", 10),
            width=5,
            state="readonly"
        )
        time_spinbox.pack(side='left')
        
        # Quiz Title
        ttk.Label(frame, text="Quiz Title:", style='Title.TLabel').pack(anchor='center')
        self.quiz_title_entry = tk.Entry(frame, font=("Arial", 14), width=50)
        self.quiz_title_entry.pack(pady=5)
        
        # Questions container
        container = tk.Frame(frame, bg='floral white')
        container.pack(fill='both', expand=True, pady=10)
        
        # Create canvas 
        canvas = tk.Canvas(container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.questions_frame = tk.Frame(canvas, bg='white')
        
        # Configure scrolling
        self.questions_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.questions_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas 
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store references 
        self.question_widgets = []
        
        # Control buttons
        control_frame = tk.Frame(frame, bg='floral white')
        control_frame.pack(fill='x', pady=10)
        
        tk.Button(
            control_frame,
            text="Add Question",
            command=self.add_question_block,
            bg='blue',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            control_frame,
            text="Save Quiz",
            command=self.save_quiz,
            bg='green',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            control_frame,
            text="Back to Menu",
            command=self.Admin_Dashboard,
            bg='gray',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5
        ).pack(side='right', padx=5)
        
        # Add first question 
        self.add_question_block()
    
    def add_question_block(self):
        """Add a new question input block"""
        # Question block frame
        block = tk.Frame(self.questions_frame, bg='floral white', bd=2, relief=tk.RIDGE)
        block.pack(fill='x', padx=10, pady=10)
        
        # Question number
        question_num = len(self.question_widgets) + 1
        tk.Label(
            block,
            text=f"Question {question_num}",
            font=("Arial", 12, "bold"),
            bg='floral white'
        ).pack(anchor='w', padx=10, pady=5)
        
        # Question text
        ttk.Label(block, text="Question:", style='Title.TLabel').pack(anchor='w', padx=10)
        question_text = scrolledtext.ScrolledText(block, height=3, width=70, font=("Arial", 10))
        question_text.pack(padx=10, pady=2)
        
        # Options
        options = {}
        for opt in ['A', 'B', 'C', 'D']:
            tk.Label(block, text=f"Option {opt}:", bg='floral white', font=("Arial", 10)).pack(anchor='w', padx=10)
            option_entry = tk.Entry(block, width=70, font=("Arial", 10))
            option_entry.pack(padx=10, pady=2)
            options[opt.lower()] = option_entry
        
        # Correct answer
        ttk.Label(block, text="Correct Answer:", style='Title.TLabel').pack(anchor='w', padx=10)
        correct_combo = ttk.Combobox(
            block,
            values=["A", "B", "C", "D"],
            state="readonly",
            width=10,
            font=("Arial", 10)
        )
        correct_combo.pack(padx=10, pady=2, anchor='w')
        
        # Remove button
        remove_btn = tk.Button(
            block,
            text="Remove Question",
            command=lambda: self.remove_question_block(block, widget_dict),
            bg='red',
            fg='white',
            font=("Arial", 9)
        )
        remove_btn.pack(anchor='e', padx=10, pady=5)
        
        # Store widget references
        widget_dict = {
            'frame': block,
            'question': question_text,
            'option_a': options['a'],
            'option_b': options['b'],
            'option_c': options['c'],
            'option_d': options['d'],
            'correct': correct_combo
        }
        
        self.question_widgets.append(widget_dict)
    
    def remove_question_block(self, block, widget_dict):
        """Remove a question block"""
        if len(self.question_widgets) <= 1:
            messagebox.showwarning("Warning", "You must have at least one question!")
            return
        
        # Remove from list
        self.question_widgets.remove(widget_dict)
        # Destroy the frame
        block.destroy()
        
        # Update question numbers
        self.update_question_numbers()
    
    def update_question_numbers(self):
        """Update question numbers after removal"""
        for i, widget_dict in enumerate(self.question_widgets):
            # Find the question number label and update it
            for child in widget_dict['frame'].winfo_children():
                if isinstance(child, tk.Label) and "Question" in child.cget("text"):
                    child.config(text=f"Question {i + 1}")
                    break
    
    def save_quiz(self):
        """Save the quiz to database"""
        title = self.quiz_title_entry.get().strip()
        quiz_time = self.quiz_time.get()
        
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a quiz title.")
            return
        
        # Collect all questions
        questions = []
        for i, widgets in enumerate(self.question_widgets):
            question_text = widgets['question'].get("1.0", tk.END).strip()
            option_a = widgets['option_a'].get().strip()
            option_b = widgets['option_b'].get().strip()
            option_c = widgets['option_c'].get().strip()
            option_d = widgets['option_d'].get().strip()
            correct = widgets['correct'].get().strip()
            
            if not all([question_text, option_a, option_b, option_c, option_d, correct]):
                messagebox.showwarning(
                    "Incomplete Question",
                    f"Please fill in all fields for Question {i + 1}."
                )
                return
            
            questions.append({
                'question': question_text,
                'option_a': option_a,
                'option_b': option_b,
                'option_c': option_c,
                'option_d': option_d,
                'correct_option': correct
            })
        
        if not questions:
            messagebox.showwarning("No Questions", "Please add at least one question.")
            return
        
        # Save to database
        success, message = self.db.save_quiz(title, quiz_time, questions)
        if success:
            messagebox.showinfo("Success", message)
            self.Admin_Dashboard()
        else:
            messagebox.showerror("Error", message)
    
    


    def Welcome_Screen(self):
        self.clear_screen()
        container = tk.Frame(self, bg="floral white")
        container.pack(expand=True, fill='both', padx=50, pady=50)

        username = self.__current_users

        # Title (no animation)
        title_label = ttk.Label(container, text="Welcome to Digital Quiz System!", style='Title.TLabel')
        title_label.pack(pady=50)

        instr_frame = ttk.Frame(container, style='Text.TLabel')
        instr_frame.pack(pady=20)

        features = [
            f" Dear {username}! Read Instructions carefully ",
            " Some questions with increasing difficulty",
            " Focus on the Question then select correct answer",
            " Select the correct answer from almost 6 options",
            " Quiz is time based. It will auto-submit when time ends",
            " Each Question contains 5 marks. Get your score at the end",
            " Best of Luck for Quiz!"
        ]

        def animate_lines(index=0):
            if index < len(features):
                feature_text = features[index]
                label = ttk.Label(instr_frame, text="", style="Green.TLabel")
                label.pack(anchor='w', pady=5)
                self.animate_label_text(label, feature_text, delay=30)

                # Wait until this line finishes before next
                total_time = len(feature_text) * 30 + 200  # +200ms buffer
                self.after(total_time, lambda: animate_lines(index + 1))

        animate_lines()
        # self.speak(features)
        # Start animation from first line

        # Static button below
        start_button = ttk.Button(container, text="Start Quiz", command=self.Start_Quiz)
        start_button.pack(pady=30)



    def Start_Quiz(self):
        self.clear_screen()
        self.show_quiz_selection()
    
    def update_timer(self):
        if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
            elapsed = int(time.time() - self.test_start_time)
            remaining = max(0, self.__time_limit - elapsed)
            
            minutes = remaining // 60
            seconds = remaining % 60
            
            # Update timer display with color coding
            if remaining <= 60:  
                self.timer_label.config(style='Timer.TLabel', foreground='red')
            else:
                self.timer_label.config(style='Timer.TLabel', foreground='black')
                
            self.timer_label.config(text=f"Time Remaining: {minutes:02d}:{seconds:02d}")
            
            if remaining <= 0:
                self.show_results()
            else:
                self.after(1000, self.update_timer)
    
    def show_quiz_selection(self):
        """Show quiz selection interface"""
        self.clear_screen()
        frame = self.create_screen()
        
        # Title
        ttk.Label(
            frame,
            text="Select Quiz to Take",
            style='Title.TLabel'
        ).pack(pady=20)
        
        # Get quiz titles
        quiz_titles = self.db.get_quiz_titles()
        
        if not quiz_titles:
            ttk.Label(
                frame,
                text="No quizzes available at this time!",
                style='Text.TLabel'
            ).pack(pady=50)
        else:
            # Quiz selection listbox
            listbox_frame = tk.Frame(frame, bg='floral white')
            listbox_frame.pack(fill='both', expand=True, pady=20)
            
            scrollbar = tk.Scrollbar(listbox_frame)
            scrollbar.pack(side='right', fill='y')
            
            self.quiz_listbox = tk.Listbox(
                listbox_frame,
                font=("Arial", 12),
                yscrollcommand=scrollbar.set,
                selectmode=tk.SINGLE,
                bg='white',
                selectbackground='lightblue'
            )
            self.quiz_listbox.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=self.quiz_listbox.yview)
            
            
            for i, title in enumerate(quiz_titles):
                self.after(100 * i, lambda t=title: self.quiz_listbox.insert(tk.END, t))
            
           
            start_btn = tk.Button(
                frame,
                text="Start Quiz",
                command=self.start_quiz,
                bg='green',
                fg='white',
                font=("Arial", 14),
                padx=30,
                pady=10,
                activebackground='darkgreen',
                relief=tk.RAISED
            )
            start_btn.pack(pady=10)
            start_btn.bind("<Enter>", lambda e: start_btn.config(bg='darkgreen'))
            start_btn.bind("<Leave>", lambda e: start_btn.config(bg='green'))
            
            # Leaderboard button
            leaderboard_btn = tk.Button(
                frame,
                text="Leaderboard",
                command=lambda: self.Recipent_score(self.quiz_listbox.get(tk.ACTIVE)),
                bg='blue',
                fg='white',
                font=("Arial", 14),
                padx=30,
                pady=10,
                activebackground='darkblue'
            )
            leaderboard_btn.pack(pady=10)
            leaderboard_btn.bind("<Enter>", lambda e: leaderboard_btn.config(bg='darkblue'))
            leaderboard_btn.bind("<Leave>", lambda e: leaderboard_btn.config(bg='blue'))
        
        # Back button
        back_btn = tk.Button(
            frame,
            text="Back to Menu",
            command=self.User_Dashboard,
            bg='brown',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5,
            activebackground='darkred'
        )
        back_btn.pack(pady=10)
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg='darkred'))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg='brown'))
    
    def start_quiz(self):
        """Start the selected quiz"""
        selection = self.quiz_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a quiz to start.")
            return

        quiz_title = self.quiz_listbox.get(selection[0])
        questions, quiz_time = self.db.get_quiz_data(quiz_title)

        if not questions:
            messagebox.showerror("Error", "Quiz not found or has no questions.")
            return

        # Initialize quiz session
        self.current_quiz_questions = questions
        self.current_question_index = 0
        self.user_answers = []
        self.score = 0
        self.quiz_title = quiz_title
        self.__time_limit = quiz_time * 60  

        self.quiz_submitted = False
        self.test_start_time = time.time()
        self.show_question()
        self.update_timer()
        
    def animate_label_text(self, label, full_text, delay=50):
        label.config(text="")  # Start empty

        def step(index=0):
            if index <= len(full_text):
                label.config(text=full_text[:index])
                label.after(delay, lambda: step(index + 1))

        step()

    
    def show_question(self):
        if self.current_question_index >= len(self.current_quiz_questions):
            self.show_results()
            return

        self.clear_screen()
        frame = self.create_screen()

        # Timer (no animation)
        self.timer_label = ttk.Label(
            frame,
            text=f"Time Remaining: {self.__time_limit // 60:02d}:{self.__time_limit % 60:02d}",
            style='Timer.TLabel',
        )
        self.timer_label.pack(side='top', pady=10, anchor='center')

        question = self.current_quiz_questions[self.current_question_index]

        # Progress Info
        progress_text = f"Question {self.current_question_index + 1} of {len(self.current_quiz_questions)}"
        progress_label = tk.Label(
            frame,
            text=progress_text,
            font=("Arial", 12),
            bg='floral white',
            fg='black'
        )
        progress_label.pack(anchor='ne', padx=10, pady=5)

        # Quiz Title
        title_label = tk.Label(
            frame,
            text=f"Quiz: {self.quiz_title}",
            font=("Arial", 18, "bold"),
            bg='floral white',
            fg='navy'
        )
        title_label.pack(pady=10)

        # Question Text with Animation
        question_frame = tk.Frame(frame, bg='floral white')
        question_frame.pack(fill='x', pady=10, padx=10)

        question_label = tk.Label(
            question_frame,
            text="",
            font=("Arial", 14),
            bg='white',
            wraplength=700,
            justify='center',
            fg='black'
        )
        question_label.pack(padx=10, pady=10)

        self.animate_label_text(question_label, question['question'])

        # Options with delay animation
        self.selected_answer = tk.StringVar()
        options_frame = tk.Frame(frame, bg='floral white')
        options_frame.pack(fill='x', pady=10)

        self.style.configure('Option.TRadiobutton',
                            foreground='black',
                            background='floral white',
                            font=('Arial', 12))

        for i, (opt_letter, opt_key) in enumerate([('A', 'option_a'), ('B', 'option_b'), ('C', 'option_c'), ('D', 'option_d')]):
            def create_option(letter=opt_letter, key=opt_key, delay=i * 300):
                def delayed_add():
                    rb = ttk.Radiobutton(
                        options_frame,
                        text=f"{letter}. {question[key]}",
                        variable=self.selected_answer,
                        value=letter,
                        style='Option.TRadiobutton'
                    )
                    rb.pack(anchor='center', padx=40, pady=5)
                self.after(delay, delayed_add)

            create_option()

        # Navigation Buttons 
        nav_frame = tk.Frame(frame, bg='floral white')
        nav_frame.pack(fill='x', pady=20, padx=10)

        quit_btn = tk.Button(
            nav_frame,
            text="Quit Quiz",
            command=self.User_Dashboard,
            bg='red',
            fg='white',
            font=("Arial", 12),
            padx=10,
            pady=5,
            activebackground='darkred'
        )
        quit_btn.pack(side='left', padx=10)

        next_text = "Next Question" if self.current_question_index < len(self.current_quiz_questions) - 1 else "Finish Quiz"

        next_btn = tk.Button(
            nav_frame,
            text=next_text,
            command=self.next_question,
            bg='green',
            fg='white',
            font=("Arial", 12),
            padx=10,
            pady=5,
            activebackground='darkgreen'
        )
        next_btn.pack(side='right', padx=10)

    
    def next_question(self):
        if not self.selected_answer.get():
            messagebox.showwarning("No Answer", "Please select an answer before proceeding.")
            return

        correct_answer = self.current_quiz_questions[self.current_question_index]['correct_option']
        if self.selected_answer.get() == correct_answer:
            self.score += 1

        self.user_answers.append(self.selected_answer.get())

        # Move to next after short delay
        def delayed_next():
            self.current_question_index += 1
            self.show_question()

        self.after(500, delayed_next)


        
    def show_results(self):
        if getattr(self, 'quiz_submitted', False):
            return  # Quiz already submitted

        self.quiz_submitted = True
        self.clear_screen()

        top_bar = tk.Frame(self, bg="blue", height=40)
        top_bar.pack(fill=tk.X)
        frame = self.create_screen()

        username = self.__current_users
        quiz_title = self.quiz_title

        tk.Label(
            top_bar,
            text="Result Frame",
            font=("Arial", 18, "bold"),
            bg='blue',
            fg='white',
        ).pack(side='left', pady=10)

        ttk.Label(
            frame,
            text="Quiz Completed!",
            font=("Arial", 24, "bold"),
            style='Title.TLabel'
        ).pack(pady=30)

        # Score calculation
        total_questions = len(self.current_quiz_questions)
        score = self.score * 5  
        total_score = total_questions * 5
        percentage = (self.score / total_questions) * 100
        score_text = f"Your Score: {score} out of {total_score} ({percentage:.1f}%)"

        # Check if score already exists
        check_query = """
        SELECT * FROM quiz_scores 
        WHERE username = %s AND quiz_title = %s
        """
        self.cursor.execute(check_query, (username, self.quiz_title))
        existing_score = self.cursor.fetchone()
        self.cursor.close()

            # Use a new cursor for update/insert to avoid "Unread result" error
        new_cursor = self.connection.cursor()

        if existing_score:
            update_query = """
            UPDATE quiz_scores 
            SET score = %s, total_questions = %s, percentage = %s, date_taken = %s 
            WHERE username = %s AND quiz_title = %s
            """
            values = (
                self.score * 5,
                total_questions * 5,
                percentage,
                datetime.now(),
                username,
                self.quiz_title
            )
            new_cursor.execute(update_query, values)
        else:
            insert_query = """
            INSERT INTO quiz_scores 
            (username, quiz_title, score, total_questions, percentage, date_taken)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                username,
                self.quiz_title,
                self.score * 5,
                total_questions * 5,
                percentage,
                datetime.now()
            )
            new_cursor.execute(insert_query, values)

        self.connection.commit()
        new_cursor.close()

        ttk.Label(
            frame,
            text=score_text,
            style='Text.TLabel'
        ).pack(pady=20)
        
        # Performance message
        if percentage >= 80:
            self.generate_certificate(username, quiz_title, score, total_score)
            self.save_certificate(username, quiz_title)
            message = f"Dear {username}, Excellent work!"
            color = 'green'
            tk.Button(
                top_bar,
                text="View Certificate",
                command=self.view_certificate,
                bg='white',
                fg='blue',
                font=("Arial", 12, "bold"),
                padx=10,
                pady=5
            ).pack(side='right', padx=10)
        elif percentage >= 60:
            self.generate_certificate(username, quiz_title, score, total_score)
            self.save_certificate(username, quiz_title)
            message = f"Dear {username}, Good job!"
            color = 'yellow'
            
            tk.Button(
                top_bar,
                text="View Certificate",
                command=self.view_certificate,
                bg='white',
                fg='blue',
                font=("Arial", 12, "bold"),
                padx=10,
                pady=5
            ).pack(side='right', padx=10)

        else:
            message = f"Hard Luck {username}, Keep practicing!"
            color = 'red'
        
        tk.Label(
            frame,
            text=message,
            font=("Arial", 16),
            bg='floral white',
            fg=color
        ).pack(pady=10)
        
        # Detailed results
        results_frame = tk.Frame(frame, bg='white', bd=2, relief=tk.RIDGE)
        results_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            results_frame,
            text="Detailed Results",
            style='Title.TLabel'
        ).pack(pady=10)
        
        
        # Scrollable results
        canvas = tk.Canvas(results_frame, bg='floral white')
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='floral white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=False)
        scrollbar.pack(side="right", fill="y")
        
        # Show each question result
        for i, (question, user_answer) in enumerate(zip(self.current_quiz_questions, self.user_answers)):
            correct_answer = question['correct_option']
            is_correct = user_answer == correct_answer
            
            q_frame = tk.Frame(scrollable_frame, bg='floral white', bd=1, relief=tk.RIDGE)
            q_frame.pack(fill='x', padx=10, pady=5)
            
            # Question number and status
            status_text = "Correct" if is_correct else "Incorrect"
            status_color = 'green' if is_correct else 'red'
            
            tk.Label(q_frame,text=f"Question {i+1}: {status_text}",font=("Arial", 12, "bold"),bg='floral white',fg=status_color).pack(anchor='w', padx=10, pady=5)
            
            tk.Label(q_frame,text=f"Your answer: {user_answer}",font=("Arial", 10),bg='floral white').pack(anchor='w', padx=20)
            
            if not is_correct:
                tk.Label( q_frame,text=f"Correct answer: {correct_answer}",font=("Arial", 12), bg='floral white', fg='green').pack(anchor='w', padx=20)
    
        tk.Button(
            top_bar,
            text='Back',
            command=self.User_Dashboard,
            bg='red',
            fg='white',
            font=("Arial", 12),
            padx=10,
            pady=5
        ).pack(side='right', padx=10)
        
        tk.Button(
            top_bar,
            text="Restart",
            command=self.Welcome_Screen,
            bg='green',
            fg='white',
            font=("Arial", 12),
            padx=10,
            pady=5
        ).pack(side='right', padx=10)
        
        tk.Button(
            top_bar,
            text="Rate our app",
            command=self.Rating,
            bg='green',
            fg='white',
            font=("Arial", 12),
            padx=10,
            pady=5
        ).pack(side='right', padx=10)
    def exit_app(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.db.disconnect()
            self.destroy()

    def Message(self):
        """Exit the application"""
        if messagebox.askyesno("Message", "This Feature is for only admin. Are you sure you want to go?"):
            self.Admin_Dashboard()
    
    def AboutApp(self):
        self.clear_screen()

        # Main container
        container = tk.Frame(self, bg="floral white")
        container.pack(expand=True, fill='both', padx=160, pady=60)

        # Title
        title_label = ttk.Label(container, text="Chat with Robo", style='Title.TLabel')
        title_label.pack(pady=20)

        # Chat Canvas with Scrollbar
        canvas = tk.Canvas(container, bg="RoyalBlue4", highlightthickness=4,bd=5,relief=tk.SUNKEN)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        chat_frame = tk.Frame(canvas, bg="RoyalBlue4")

        chat_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=chat_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # FAQs
        faqs = {
            "What is this app about?": "- This app is a smart quiz platform designed to test your knowledge across various subjects.  It helps users learn interactively and tracks their performance.",
            "How this app work?": "- This app contain many features. There is Two type of account creation occur, one is Admin and other is Users. Admin can do seperate functions and users can do their seperate functions. All account data such as Username ,Password ,Scores ,Reviews & Ratings will be saved in Database",
            "Who can use this app?": "- Anyone — from students to professionals — can use this app. Whether you want to improve your general knowledge or prepare for exams, this app is for you! ",
            "How quiz system work?": "- Select a quiz from the dashboard, answer all the questions within the given time, and submit. Your score will be displayed immediately with feedback. You also recieved the certificate of selective subject quiz on some criteria",
            "Does app save my scores?": "- Yes, your quiz scores are saved under your account. You can view your performance history anytime after logging in. You also see the leaderboard of selective subject quiz.",
            "App support languages": "- Currently, the app is in English, but support for Urdu and more languages is planned in future updates.",
            "Who developed this app?": """- This app was developed by Imran Ghafoor, a passionate student of Artificial Intelligence, currently pursuing his Bachelor's in AI.
He is self-driven, creative, and always exploring the possibilities of combining technology and learning.
Imran believes in building smart systems that not only test knowledge but also inspire curiosity.
His goal is to become a skilled AI specialist and build solutions that serve the world.
This app is just the beginning — bigger things are on the way, In Shaa Allah."""
        }

        def print_question_buttons():
            # Destroy old button frame if exists
            nonlocal btn_frame, press_btn
            if btn_frame:
                btn_frame.destroy()
            if press_btn:
                press_btn.destroy()

            btn_frame = tk.Frame(chat_frame, bg="Green")
            btn_frame.pack(pady=10, fill='x')

            ttk.Label(btn_frame, text="Ask a question:", font=('Arial', 14, 'bold'), background='Green').pack(pady=5)

            for question in faqs:
                btn = ttk.Button(btn_frame, text=question,style='Question.TButton', command=lambda q=question: show_conversation(q))
                btn.pack(pady=4, padx=30, fill='x')

            canvas.yview_moveto(1.0)

        def show_conversation(question):
            nonlocal btn_frame, press_btn
            if btn_frame:
                btn_frame.destroy()
            if press_btn:
                press_btn.destroy()

            user_msg_frame = tk.Frame(chat_frame, bg='RoyalBlue4')
            user_msg_frame.pack(fill='x', pady=(10, 2), padx=10, anchor='e')  

            tk.Label(user_msg_frame,
                    text="You: " + question,
                    font=('Arial', 16, 'bold'),
                    bg='light green', fg='black',
                    wraplength=400,
                    justify='left',
                    padx=10, pady=5,
                    anchor='e').pack(anchor='e', padx=10)

            # === Robo Message (Left Aligned) ===
            robo_msg_frame = tk.Frame(chat_frame, bg='RoyalBlue4')
            robo_msg_frame.pack(fill='x', pady=(2, 10), padx=10, anchor='w')  

            tk.Label(robo_msg_frame,
                    text="Robo: " + faqs[question],
                    font=('Arial', 14),
                    bg='floral white', fg='blue',
                    wraplength=400,
                    justify='left',
                    padx=10, pady=5,
                    anchor='w').pack(anchor='w', padx=20)

            press_btn=ttk.Button(chat_frame, text="▶Press to Continue",style='Question.TButton',command=print_question_buttons)
            press_btn.pack(pady=(0, 15))
            canvas.yview_moveto(1.0)

        # Button frame (needs to be accessible in nested function)
        btn_frame = None
        press_btn = None
        print_question_buttons()
        ttk.Button(container, text="Back", command=self.main_menu).pack(pady=20)
        
    def Help(self):
        self.clear_screen()

        # Main container
        container = tk.Frame(self, bg="floral white")
        container.pack(expand=True, fill='both', padx=160, pady=60)

        # Title
        title_label = ttk.Label(container, text="Chat with Robo", style='Title.TLabel')
        title_label.pack(pady=20)

        # Chat Canvas with Scrollbar
        canvas = tk.Canvas(container, bg="RoyalBlue4", highlightthickness=4,bd=5,relief=tk.SUNKEN)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        chat_frame = tk.Frame(canvas, bg="RoyalBlue4")

        chat_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=chat_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # FAQs
        faqs = {
            "How to sign up?": "- Use a unique username and use alphabets only.\n- Password must be at least 6 characters and also use special letter #%$@.Make sure all fields\n are filled and role is selected .",
            "How to login?": "- Check your username and password again and again.\n- Make sure the selected role must match the signup role.\n- You have not access to login into Admin account",
            "Forgot password?": "- Currently, reset password is not available.\n- If you face any problem please contact to developer Imran Ghafoor,\n - Contact: Officialimran594@gmail.com",
            "Quiz not starting?": "- Make sure you have selected a quiz title \n which you want to take. Wait for the timer to start.",
            "Can I retake quiz?": "- Yes, quizzes can be retake. When you retake\n the same quiz your marks will updated to your profile.\n Then you can see the fresh leaderboard",
            "Can I recieve Certificate?": "-Yes, You will get a certificate of selected quiz \n if you get marks >= 60% in the quiz",
            "Contact Support": "- This is the official or personal Email of Imran Ghafoor\n Email: Officialimran594@gmail.com"
        }

        def print_question_buttons():
            # Destroy old button frame if exists
            nonlocal btn_frame, press_btn
            if btn_frame:
                btn_frame.destroy()
            if press_btn:
                press_btn.destroy()

            btn_frame = tk.Frame(chat_frame, bg="Green")
            btn_frame.pack(pady=10, fill='x')

            ttk.Label(btn_frame, text="Select a question:", font=('Arial', 14, 'bold'), background='Green').pack(pady=5)

            for question in faqs:
                btn = ttk.Button(btn_frame, text=question,style='Question.TButton', command=lambda q=question: show_conversation(q))
                btn.pack(pady=4, padx=30, fill='x')

            canvas.yview_moveto(1.0)

        def show_conversation(question):
            nonlocal btn_frame, press_btn
            if btn_frame:
                btn_frame.destroy()
            if press_btn:
                press_btn.destroy()

            user_msg_frame = tk.Frame(chat_frame, bg='RoyalBlue4')
            user_msg_frame.pack(fill='x', pady=(10, 2), padx=10, anchor='e')  # anchor right

            tk.Label(user_msg_frame,
                    text="You: " + question,
                    font=('Arial', 16, 'bold'),
                    bg='light green', fg='black',
                    wraplength=400,
                    justify='left',
                    padx=10, pady=5,
                    anchor='e').pack(anchor='e', padx=10)

            robo_msg_frame = tk.Frame(chat_frame, bg='RoyalBlue4')
            robo_msg_frame.pack(fill='x', pady=(2, 10), padx=10, anchor='w')  # anchor left

            tk.Label(robo_msg_frame,
                    text="Robo: " + faqs[question],
                    font=('Arial', 14),
                    bg='floral white', fg='blue',
                    wraplength=400,
                    justify='left',
                    padx=10, pady=5,
                    anchor='w').pack(anchor='w', padx=20)

            press_btn=ttk.Button(chat_frame, text="▶Press to Continue",style='Question.TButton', command=print_question_buttons)
            press_btn.pack(pady=(0, 15))
            canvas.yview_moveto(1.0)

        # Button frame (needs to be accessible in nested function)
        btn_frame = None
        press_btn = None
        print_question_buttons()

        # Back button at the bottom
        ttk.Button(container, text="Back", command=self.main_menu).pack(pady=20)

    def Rating(self):
        self.clear_screen()
        frame = self.create_screen()

        ttk.Label(frame, text="Rate our App", style='Title.TLabel', font=("Helvetica", 24)).pack(pady=5)

        container = tk.Frame(frame, bg='floral white')
        container.pack(fill='both', expand=True, pady=10)

        # Canvas and scrollbar
        canvas = tk.Canvas(container, bg='floral white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.questions_frame = tk.Frame(canvas, bg='floral white')
        canvas.create_window((0, 0), window=self.questions_frame, anchor='n')

        self.questions_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

       
        center_frame = tk.Frame(self.questions_frame, bg='floral white')
        center_frame.pack(pady=20)

        # All widgets go inside center_frame
        ttk.Label(center_frame, text="Your Name:", style='Text.TLabel').pack(pady=(10, 0))
        name_entry = ttk.Entry(center_frame, width=40)
        name_entry.pack(pady=5)

        ttk.Label(center_frame, text="Rate (1 to 5):", style='Text.TLabel').pack()
        rating_var = tk.IntVar()
        rating_combo = ttk.Combobox(center_frame, textvariable=rating_var, values=[1, 2, 3, 4, 5], width=5)
        rating_combo.pack(pady=5)

        ttk.Label(center_frame, text="Your Review:", style='Text.TLabel').pack()
        review_text = tk.Text(center_frame, height=5, width=50)
        review_text.pack(pady=5)

        status_label = ttk.Label(center_frame, text="", foreground='red')
        status_label.pack(pady=(5, 0))

        def submit_review():
            name = name_entry.get().strip()
            rating = rating_var.get()
            review = review_text.get("1.0", tk.END).strip()

            if not name or not rating or not review:
                status_label.config(text="Please fill in all fields.")
                return

            try:
                self.cursor.execute("INSERT INTO reviews (name, rating, review) VALUES (%s, %s, %s)",
                                    (name, rating, review))
                self.connection.commit()
                status_label.config(text="Thank you for your feedback!", foreground="green")
                name_entry.delete(0, tk.END)
                review_text.delete("1.0", tk.END)
                rating_combo.set('')
            except Exception as e:
                status_label.config(text="Error saving review. Try again.", foreground="red")
                print("DB Error:", e)

        button_frame = tk.Frame(center_frame, bg='white')
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Submit", command=submit_review).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Back", command=self.User_Dashboard).pack(side='left', padx=10)

    def get_reviews(self):
        try:
            query = "SELECT name, rating, review, created_at FROM reviews ORDER BY created_at DESC"
            self.cursor.execute(query)
            return self.cursor.fetchall()  # returns list of tuples
        except Error as e:
            print(f"Error fetching reviews: {e}")
            return []


    def check_review(self):
        self.clear_screen()
        top_bar = tk.Frame(self, bg="blue", height=40)
        top_bar.pack(fill=tk.X)
        
        tk.Button(
                top_bar,
                text='Back',
                command=self.User_Dashboard,
                bg='red',
                fg='white',
                font=("Arial", 12),
                padx=10,
                pady=5
            ).pack(side='right', padx=10)
        frame = self.create_screen()

        # Title Label
        ttk.Label(frame, text="User Reviews & Ratings", style='Title.TLabel', font=("Helvetica", 24)).pack(pady=10)
      
        # Get all reviews
        reviews = self.get_reviews()

        if not reviews:
            ttk.Label(
                frame,
                text="No reviews available yet.",
                style='Text.TLabel'
            ).pack(pady=50)
            return
        
        total_reviews = len(reviews)
        total_rating = sum([r[1] for r in reviews]) 
        avg_rating = round(total_rating / total_reviews, 1)

        # Show at top
        summary_frame = tk.Frame(frame, bg='floral white')
        summary_frame.pack(pady=(5, 15))

        ttk.Label(
            summary_frame,
            text=f"Average Rating: {avg_rating}★",
            font=("Helvetica", 14, "bold"),
            foreground="gold"
        ).pack()

        ttk.Label(
            summary_frame,
            text=f"{total_reviews} Reviews",
            font=("Helvetica", 14)
        ).pack()

        # Scrollable Frame Setup
        container = tk.Frame(frame, bg='floral white')
        container.pack(fill='both', expand=True, padx=20, pady=10)

        canvas = tk.Canvas(container, bg='white', highlightthickness=2,bd=2)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        review_frame = tk.Frame(canvas, bg='white')
        canvas.create_window((0, 0), window=review_frame, anchor='nw')

        review_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Loop through reviews and show
        for idx, (name, rating, review, created_at) in enumerate(reviews):
            card = tk.Frame(review_frame, bg="floral white", bd=1, relief="solid")
            card.pack(fill='x', padx=10, pady=5)

            # Reviewer name and date
            ttk.Label(
                card,
                text=f"{name} — {created_at.strftime('%Y-%m-%d %H:%M')}",
                font=("Arial", 12, "bold")
            ).pack(anchor='w', padx=10, pady=(5, 0))

            # Convert numeric rating to stars
            stars = '★' * rating + '☆' * (5 - rating)
            ttk.Label(
                card,
                text=f"Rating: {stars}",
                foreground="gold",
                font=("Arial", 14)
            ).pack(anchor='w', padx=10)

            # Review text
            ttk.Label(
                card,
                text=f"“{review}”",
                wraplength=600,
                font=("Arial", 12)
            ).pack(anchor='w', padx=10, pady=(0, 5))
            

    def generate_certificate(self, username, quiz_title, score, total_score):
        try:
            # Initialize PDF document
            pdf = FPDF('L', 'mm', 'A4')
            pdf.add_page()
            
            # Set certificate design parameters
            design = {
                'primary_color': (0, 102, 204),  # Blue
                'secondary_color': (50, 50, 50),   # Dark gray
                'border_margin': 15,
                'border_thickness': 1.5
            }
            
            # Add certificate components
            self._add_border(pdf, design)
            self._add_header(pdf, design)
            self._add_recipient(pdf, design, username)
            self._add_quiz_info(pdf, design, quiz_title, score, total_score)
            self._add_date(pdf, design)
            self._add_signature(pdf, design)
            
            # Save with unique filename
            return self._save_with_unique_name(pdf, username)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate certificate: {str(e)}")
            return None
    
    def _get_unique_filename(self, base_path, base_name, extension):
        """Generate a unique filename by appending numbers if needed."""
        counter = 1
        full_path = os.path.join(base_path, f"{base_name}{extension}")
        
        while os.path.exists(full_path):
            full_path = os.path.join(base_path, f"{base_name}_{counter}{extension}")
            counter += 1
            
        return full_path
    
    def _save_with_unique_name(self, pdf, username):
        """Save with unique filename and store the path"""
        try:
            cert_dir = os.path.join(os.getcwd(), "certificates")
            os.makedirs(cert_dir, exist_ok=True)
            
            safe_username = "".join(c if c.isalnum() else "_" for c in username)
            base_name = f"Certificate_{safe_username}"  # Fixed variable name here
            extension = ".pdf"
            
            # Find available filename
            full_path = self._get_unique_filename(cert_dir, base_name, extension)
            
            pdf.output(full_path)
            self.last_cert_path = full_path  # Store the path
            return full_path
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save certificate: {str(e)}")
            return None
    
    # [Rest of your helper methods remain exactly the same]
    def _add_border(self, pdf, design):
        """Add decorative border to the certificate."""
        pdf.set_draw_color(*design['primary_color'])
        pdf.set_line_width(design['border_thickness'])
        pdf.rect(
            design['border_margin'], 
            design['border_margin'], 
            pdf.w - 2*design['border_margin'], 
            pdf.h - 2*design['border_margin']
        )
    
    def _add_header(self, pdf, design):
        """Add certificate title and decorative line."""
        pdf.set_font("Helvetica", 'B', 32)
        pdf.set_text_color(*design['primary_color'])
        pdf.cell(0, 30, "CERTIFICATE OF COMPLETION", ln=1, align='C')
        
        # Add decorative line under title
        line_length = 120
        pdf.set_draw_color(*design['primary_color'])
        pdf.line(pdf.w/2 - line_length/2, 40, pdf.w/2 + line_length/2, 40)
    
    def _add_recipient(self, pdf, design, username):
        """Add recipient information."""
        pdf.set_font("Helvetica", '', 18)
        pdf.set_text_color(*design['secondary_color'])
        pdf.ln(30)
        pdf.cell(0, 10, "This certificate is awarded to:", ln=1, align='C')
        
        pdf.set_font("Helvetica", 'B', 28)
        pdf.set_text_color(*design['primary_color'])
        pdf.cell(0, 15, username.upper(), ln=1, align='C')
    
    def _add_quiz_info(self, pdf, design, quiz_title, score, total_score):
        """Add quiz information and score."""
        pdf.set_font("Helvetica", '', 18)
        pdf.set_text_color(*design['secondary_color'])
        pdf.cell(0, 10, "for successfully completing", ln=1, align='C')
        
        pdf.set_font("Helvetica", 'B', 22)
        pdf.cell(0, 15, quiz_title, ln=1, align='C')
        
        pdf.set_font("Helvetica", '', 18)
        pdf.cell(0, 10, f"with a score of {score}/{total_score}", ln=1, align='C')
    
    def _add_date(self, pdf, design):
        """Add current date."""
        pdf.ln(15)
        pdf.set_font("Helvetica", 'I', 16)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=1, align='C')
    
    def _add_signature(self, pdf, design):
        """Add signature line."""
        pdf.ln(20)
        signature_y = pdf.get_y()
        signature_text = "Imran Ghafoor"
        pdf.set_font("Helvetica", 'I', 14)
        pdf.set_text_color(*design['secondary_color'])
        
        text_width = pdf.get_string_width(signature_text)
        right_margin = 25
        x_position = pdf.w - text_width - right_margin
        pdf.set_xy(x_position, signature_y)
        pdf.cell(text_width, 10, signature_text)
        pdf.line(x_position, signature_y + 10, x_position + text_width, signature_y + 10)
        
    def view_certificate(self):
        """Open the last generated certificate using the system default viewer"""
        if not hasattr(self, 'last_cert_path') or not self.last_cert_path:
            messagebox.showerror("Error", "No certificate has been generated yet")
            return
        
        if not os.path.exists(self.last_cert_path):
            messagebox.showerror("Error", "Certificate file not found")
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(self.last_cert_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", self.last_cert_path], check=True)
            else:  # Linux and other Unix-like
                subprocess.run(["xdg-open", self.last_cert_path], check=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open certificate: {str(e)}")
    
    def save_certificate(self, username, quiz_title):
        try:
            insert_query = """
            INSERT INTO certificates (username, quiz_title)
            VALUES (%s, %s)
            """
            values = (username, quiz_title)
            self.cursor.execute(insert_query, values)
            self.connection.commit()
            self.connection.close()
        except Exception as e:
            print("Error saving certificate:", e) 
            
    def fetch_all_certificates(self):
        try:
            self.cursor.execute("SELECT username, quiz_title, awarded_on FROM certificates")
            rows = self.cursor.fetchall()
            self.connection.close()
            return rows
        except Exception as e:
            print("DB Error (All):", e)
            return []

    # Fetch certificates for a specific user
    def fetch_user_certificates(self,username):
        try:
            self.cursor.execute("SELECT username, quiz_title, awarded_on FROM certificates WHERE username = %s", (username,))
            self.connection.commit()
            rows = self.cursor.fetchall()
            self.connection.close()
            return rows
        except Exception as e:
            print("DB Error (User):", e)
            return []
    
    
    def open_certificate_viewer(self):
        self.clear_screen()
        frame = self.create_screen()

        # Heading
        tk.Label(
            frame,
            text="View Awarded Certificates",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#0055aa"
        ).pack(pady=10)

        # --- Top Frame for buttons + entry ---
        top_frame = tk.Frame(frame, bg="white")
        top_frame.pack(pady=5)

        entry_username = tk.Entry(top_frame, font=("Arial", 12), width=22)
        entry_username.grid(row=0, column=1, padx=5)
        entry_username.insert(0, "Enter username")

        # --- Table Frame with Scrollbar ---
        table_frame = tk.Frame(frame)
        table_frame.pack(padx=10, pady=15, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(
            table_frame,
            columns=("User", "Quiz", "Date"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        tree.heading("User", text="Username")
        tree.heading("Quiz", text="Quiz Title")
        tree.heading("Date", text="Awarded On")

        tree.column("User", width=150)
        tree.column("Quiz", width=300)
        tree.column("Date", width=200)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=tree.yview)

        # --- Function to update table ---
        def update_table(data):
            for item in tree.get_children():
                tree.delete(item)
            for row in data:
                tree.insert("", "end", values=row)

        # --- Button Commands ---
        def show_specific():
            username = entry_username.get().strip().lower()
            data = self.fetch_user_certificates(username)
            if not data:
                messagebox.showinfo("No Results", f"No certificates found for '{username}'.")
                return
            update_table(data)

        def show_all():
            data = self.fetch_all_certificates()
            update_table(data)


        # --- Buttons ---
        btn_specific = tk.Button(top_frame, text="See Specific User", command=show_specific)
        btn_specific.grid(row=0, column=0, padx=5)

        btn_all = tk.Button(top_frame, text="See All Certificates", command=show_all)
        btn_all.grid(row=0, column=2, padx=5)
        
        btn_all = tk.Button(top_frame, text="Back", command=self.Admin_Dashboard)
        btn_all.grid(row=0, column=3, padx=5)

        # Start with empty table
        update_table([])

