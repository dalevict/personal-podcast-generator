import sqlite3
import json

DB_PATH = "podcast_app.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            interests TEXT
        )
    ''')
    
    # Create podcasts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            subject TEXT,
            filename TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

def save_user(username, interests):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Store interests as a JSON string for easy retrieval
    interests_json = json.dumps(interests)
    cursor.execute('''
        INSERT OR REPLACE INTO users (username, interests) 
        VALUES (?, ?)
    ''', (username, interests_json))
    conn.commit()
    conn.close()

def get_user_interests(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT interests FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0]) # Make sure this is parsed back into a list
    return []

def log_podcast(username, subject, filename):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO podcasts (username, subject, filename) 
        VALUES (?, ?, ?)
    ''', (username, subject, filename))
    conn.commit()
    conn.close()