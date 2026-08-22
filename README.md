# Quiz Master 

A desktop-based quiz management and examination system built with **Python, Tkinter, and MySQL**.

Quiz Master allows administrators to create and manage MCQ-based quizzes while users can register, log in, attempt timed quizzes, view their scores, and compete through leaderboards.

> **Academic Project — 2nd Semester**

---

##  Overview

Quiz Master was developed as a semester project to demonstrate practical programming concepts including:

* Object-oriented programming
* GUI development
* Database connectivity
* User authentication
* CRUD operations
* Input validation
* Role-based access
* Quiz management
* Score calculation
* Timed assessments
* Text-to-speech interaction

The application uses **Tkinter** for the graphical interface and **MySQL** for persistent data storage.

---

##  Features

###  User Features

* User registration
* Secure login interface
* Role-based authentication
* Password visibility toggle
* Login attempt limitation
* Timed quizzes
* Multiple-choice questions
* Automatic score calculation
* Percentage calculation
* Leaderboard
* Quiz ratings/reviews
* Certificate generation
* Text-to-speech feedback
* Interactive Robo assistant

###  Admin Features

* Admin authentication
* Admin dashboard
* Create new quizzes
* Add MCQ questions
* Configure quiz time limits
* View registered users
* Delete users
* View user scores
* View certificates
* Manage quiz data

###  Interface

* Tkinter-based desktop GUI
* Custom styling
* Background image slideshow
* Interactive animated assistant
* Error and validation messages
* User-friendly navigation

---

##  Technology Stack

| Technology             | Purpose                      |
| ---------------------- | ---------------------------- |
| Python                 | Core application development |
| Tkinter                | Desktop GUI                  |
| MySQL                  | Database management          |
| MySQL Connector/Python | Python–MySQL communication   |
| Pillow                 | Image processing             |
| pyttsx3                | Text-to-speech               |
| FPDF2                  | Certificate/PDF generation   |
| Threading              | Background speech processing |

---

##  Project Structure

```text
QuizApp/
│
├── my_images/              # Application images and UI assets
│
├── config.py               # Database configuration
├── database.py             # Database connection and operations
├── main.py                 # Application entry point
├── quiz_app.py             # Main quiz application logic
├── Style.py                # UI styles and reusable GUI components
│
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignored files
└── README.md               # Project documentation
```

---

##  Database

Quiz Master uses **MySQL** as its relational database.

The application automatically creates the required tables when a database connection is established.

Main entities include:

* `users`
* `quizzes`
* `mcq_questions`
* `quiz_scores`
* Additional tables used by the application

### Database Relationship

```text
Users
  │
  └── Quiz Attempts
          │
          └── Scores

Quizzes
  │
  └── MCQ Questions
```

---

##  Requirements

Before running the application, make sure you have:

* Python 3.10+
* MySQL Server
* MySQL database
* Windows environment recommended

---

##  Installation

### 1. Clone the repository

```bash
git clone https://github.com/Imran-Ghafoor594/quiz-master.git
cd QuizApp
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

##  MySQL Configuration

Create a MySQL database:

```sql
CREATE DATABASE quiz_data;
```

Configure the application using environment variables rather than storing database credentials directly in the source code.

Example:

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=quiz_data
DB_PORT=3306
```

> Never commit real database passwords, API keys, or other credentials to GitHub.

---

##  Running the Application

After configuring MySQL:

```bash
python main.py
```

If your project uses `quiz_app.py` as the main entry point, run:

```bash
python quiz_app.py
```

---

##  Authentication

The application provides separate roles:

### Admin

Administrators can manage quizzes, users, scores, and other administrative functions.

### User

Users can register, log in, attempt quizzes, view results, and access leaderboard functionality.

---

##  Concepts Demonstrated

This project demonstrates several core programming concepts:

* Classes and objects
* Encapsulation
* Functions and modules
* Exception handling
* Event-driven programming
* Database CRUD operations
* SQL queries
* Input validation
* GUI programming
* File handling
* Threading
* Environment variables
* Basic authentication logic

---

##  Future Improvements

Possible improvements for future versions include:

* Password hashing using `bcrypt` or `argon2`
* Improved authentication architecture
* Environment-based configuration
* Responsive GUI design
* Question categories and difficulty levels
* Randomized questions
* Multiple quiz attempts
* Detailed performance analytics
* Admin statistics dashboard
* Export results to CSV/PDF
* Improved database schema
* Cross-platform support
* Automated testing
* Better project modularization

---

## Security Note

This project was developed for academic and educational purposes.

Before using it in a production environment, authentication and database security should be improved, particularly:

* Password hashing
* Credential management
* Session management
* Access control
* Database permissions
* Input validation
* Secure configuration

---

##  Author

**Imran Ghafoor**

AI Engineer | Python & Machine Learning Enthusiast

GitHub: `https://github.com/Imran-Ghafoor594`

---

## 📄 License

This project is available for educational and learning purposes.

```
```
