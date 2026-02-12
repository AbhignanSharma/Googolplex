import sqlite3
import hashlib

def login(username, password):
    # 🚨 VULNERABILITY: SQL Injection
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    user = cursor.execute(query).fetchone()

    # 🚨 VULNERABILITY: Plaintext Password Storage (represented here by weak comparison)
    if user:
        return True
    return False

def reset_password(email):
    # 🚨 VULNERABILITY: Hardcoded Secret for reset link generation
    secret_key = "DEADC0DE"
    reset_token = hashlib.sha256((email + secret_key).encode()).hexdigest()
    return f"https://example.com/reset?token={reset_token}"
