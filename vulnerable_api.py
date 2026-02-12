from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

# 🚩 VULNERABILITY 1: Hardcoded Secret (Medium)
# Secrets should be in environment variables, not in code.
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY") # Load from environment variable
# Production deployments should ensure ADMIN_API_KEY is set and handle its absence

@app.route("/api/v1/user")
def get_user_data():
    user_id = request.args.get("id")

    # 🚩 VULNERABILITY 2: SQL Injection (High)
    # CWE-89: Improper Neutralization of Special Elements used in an SQL Command
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Use parameterized queries to prevent SQL injection
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return str(cursor.fetchone())

@app.route("/api/v1/debug")
def debug_command():
    user_cmd = request.args.get("cmd")

    # 🚩 VULNERABILITY 3: OS Command Injection (Critical)
    # CWE-78: Improper Neutralization of Special Elements used in an OS Command
    # This allows Remote Code Execution (RCE) on the server.
    # Log the command instead of executing it to prevent OS Command Injection
    # If actual OS command execution is needed, use subprocess.run with a strict whitelist and shell=False
    app.logger.info(f"Debug command attempted: {user_cmd}")
    return "Command executed successfully"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)