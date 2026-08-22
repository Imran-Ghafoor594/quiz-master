import os

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'quiz_data'),
    'buffered': os.getenv('DB_BUFFERED',True),
    'port': int(os.getenv('DB_PORT', '3306'))
}
