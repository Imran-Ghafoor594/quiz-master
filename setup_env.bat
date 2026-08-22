@echo off
:: ==========================================
:: VIRTUAL ENV SETUP - CUSTOMIZED FOR IMRAN
:: Project Path: F:\QuizApp
:: Python Path: C:\Users\Imran Ghafoor\AppData\Local\Microsoft\WindowsApps\python.exe
:: ==========================================

:: Go to project folder
F:
cd \QuizApp

:: Create virtual environment
echo 🔧 Creating virtual environment in F:\QuizApp...
"C:\Users\Imran Ghafoor\AppData\Local\Microsoft\WindowsApps\python.exe" -m venv venv

:: Activate virtual environment
call venv\Scripts\activate

:: Install required libraries
echo 📦 Installing required libraries...
pip install pyttsx3 pillow mysql-connector-python

:: Save installed libraries
pip freeze > requirements.txt

echo.
echo ✅ Environment ready in F:\QuizApp
echo 🔹 Activate later with: venv\Scripts\activate
pause
