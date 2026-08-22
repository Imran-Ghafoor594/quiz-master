import sys
import tkinter as tk
from tkinter import messagebox
from quiz_app import QuizAPP

def main():
    try:
        app = QuizAPP()
        app.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror(
            "Application Error",
            f"An unexpected error occurred:\n{str(e)}\n\nPlease check your database connection and try again."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
