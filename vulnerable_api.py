import os
import sqlite3
from flask import Flask, request

app = Flask(__name__)

# 🚩 VULNERABILITY 1: Hardcoded Secret (Medium)
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY") # Load from environment variable
# Production deployments should ensure ADMIN_API_KEY is set and handle its absence
ADMIN_API_KEY = "sg-demo-key-998877665544"

@app.route("/api/v1/user")
def get_user_data():
    user_id = request.args.get("id")

    # 🚩 VULNERABILITY 2: SQL Injection (High)
    # CWE-89: Improper Neutralization of Special Elements used in an SQL Command
    conn = sqlite3.connect("users.db")
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return str(cursor.fetchone())

@app.route("/api/v1/debug")
def debug_command():
    user_cmd = request.args.get("cmd")

    # 🚩 VULNERABILITY 3: OS Command Injection (Critical)
    # CWE-78: Improper Neutralization of Special Elements used in an OS Command
app.logger.info(f"Debug command attempted: {user_cmd}")
    os.system(f"echo Debugging: {user_cmd}")
    return "Command executed successfully"

@app.route("/api/v1/log")
def read_log_file():
    filename = request.args.get("file")
    # 🚩 VULNERABILITY 4: Path Traversal (High)
    # CWE-22: Improper Limitation of a Pathname to a Restricted Directory
    with open(os.path.join("logs", filename), "r") as f:
        return f.read()

@app.route("/api/v1/welcome")
def welcome_user():
    name = request.args.get("name")
    # 🚩 VULNERABILITY 5: Reflected XSS (Medium)
    # CWE-79: Improper Neutralization of Input During Web Page Generation
    return f"<h1>Welcome, {name}!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
