import os
import sqlite3
import pickle
import base64
from flask import Flask, request
import subprocess # Added for Fix 3

app = Flask(__name__)

# 🚩 VULNERABILITY 1: Hardcoded Secret
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "fallback-dev-key-ONLY-FOR-DEV")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///users.db") # Changed to SQLite for consistency with the file, and using environment variable.

@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    # 🚩 VULNERABILITY 2: SQL Injection
    # Using string formatting for DB queries is a critical risk
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return str(cursor.fetchone())

@app.route("/execute")
def run_command():
    cmd = request.args.get("cmd")

    # CRITICAL: os.system() is highly vulnerable to command injection.
    # Use subprocess.run() with shell=False and pass arguments as a list.
    subprocess.run(["echo", cmd], check=True) # Executes 'echo' command safely.
    return "Command executed"

@app.route("/load")
def load_data():
    data = request.args.get("data")

    # CRITICAL: pickle.loads is inherently insecure with untrusted input and leads to Remote Code Execution (RCE).
    # This feature is disabled. If object deserialization is required, use a secure data format like JSON.
    # Example (if expecting JSON):
    # import json
    # decoded_str = base64.b64decode(data).decode('utf-8')
    # obj = json.loads(decoded_str)
    raise ValueError("Insecure deserialization using pickle is forbidden due to critical security risks.")

if __name__ == "__main__":
    app.run(debug=False) # Fix 5 applied