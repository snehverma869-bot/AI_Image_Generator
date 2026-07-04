import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    prompt TEXT,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS prompt_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    prompt TEXT,
    favorite INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# Create a default admin account if it does not exist.
cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
if cursor.fetchone() is None:
    cursor.execute(
        "INSERT INTO users(username,password) VALUES (?, ?)",
        ("admin", "admin123")
    )
    conn.commit()