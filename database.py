from tkinter import messagebox,ttk
import tkinter as tk
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            self.create_tables()
            return True
        except Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            
            self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            role VARCHAR(50)
        )
        """)
            # Create quiz table
            create_quiz_table = """
            CREATE TABLE IF NOT EXISTS quizzes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) UNIQUE NOT NULL,
                time_limit INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Create questions table
            create_questions_table = """
            CREATE TABLE IF NOT EXISTS mcq_questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                quiz_id INT NOT NULL,
                question TEXT NOT NULL,
                option_a VARCHAR(500) NOT NULL,
                option_b VARCHAR(500) NOT NULL,
                option_c VARCHAR(500) NOT NULL,
                option_d VARCHAR(500) NOT NULL,
                correct_option CHAR(1) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
            )
            """
        
            self.cursor.execute(create_quiz_table)
            self.cursor.execute(create_questions_table)
            self.connection.commit()
            
        except Error as e:
            print(f"Error creating tables: {e}")

        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", ('admin', 'admin123', 'Admin'))
            self.connection.commit()
    
   
    
    def save_quiz(self, title, quiz_time, questions):
        """Save quiz with questions to database"""
        try:
            # First, insert the quiz with time_limit
            insert_quiz = "INSERT INTO quizzes (title, time_limit) VALUES (%s, %s)"
            self.cursor.execute(insert_quiz, (title, quiz_time))
            quiz_id = self.cursor.lastrowid
            
            # Then insert all questions
            insert_question = """
            INSERT INTO mcq_questions 
                (quiz_id, question, option_a, option_b, option_c, option_d, correct_option)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            for q in questions:
                self.cursor.execute(insert_question, (
                    quiz_id,
                    q['question'],
                    q['option_a'],
                    q['option_b'],
                    q['option_c'],
                    q['option_d'],
                    q['correct_option']
                ))
            
            self.connection.commit()
            return True, "Quiz saved successfully!"
            
        except mysql.connector.IntegrityError:
            self.connection.rollback()
            return False, "A quiz with this title already exists!"
        except Error as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
    
    def get_quiz_titles(self):
        """Get only quiz titles from DB (without time limits)"""
        try:
            query = "SELECT title FROM quizzes ORDER BY created_at DESC"
            self.cursor.execute(query)
            return [row[0] for row in self.cursor.fetchall()] 
        except Error as e:
            print(f"Error fetching quiz titles: {e}")
            return []

    def get_quiz_data(self, title):
        """Get complete quiz data including questions and time limit"""
        try:
            # First get the time limit
            time_query = "SELECT time_limit FROM quizzes WHERE title = %s"
            self.cursor.execute(time_query, (title,))
            time_result = self.cursor.fetchone()
            
            if not time_result:
                return [], 10  
            
            quiz_time = time_result[0]
            
           
            questions_query = """
            SELECT question, option_a, option_b, option_c, option_d, correct_option
            FROM mcq_questions
            WHERE quiz_id = (SELECT id FROM quizzes WHERE title = %s)
            ORDER BY id
            """
            self.cursor.execute(questions_query, (title,))
            question_rows = self.cursor.fetchall()
            
            questions = []
            for row in question_rows:
                questions.append({
                    'question': row[0],
                    'option_a': row[1],
                    'option_b': row[2],
                    'option_c': row[3],
                    'option_d': row[4],
                    'correct_option': row[5]
                })
            
            return questions, quiz_time
            
        except Error as e:
            print(f"Error fetching quiz data: {e}")
            return [], 10  

    def quiz_exists(self, title):
        """Check if quiz exists"""
        try:
            query = "SELECT COUNT(*) FROM quizzes WHERE title = %s"
            self.cursor.execute(query, (title,))
            count = self.cursor.fetchone()[0]
            return count > 0
        except Error as e:
            print(f"Error checking quiz existence: {e}")
            return False
        
   