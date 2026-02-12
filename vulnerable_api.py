import os
import sqlite3
import pickle
import base64
from flask import Flask, request

app = Flask(__name__)

# 🚩 VULNERABILITY 1: Hardcoded Secret
SECRET_KEY = "super-secret-key-12345"
DATABASE_URL = "postgres://admin:Password123@localhost:5432/mydb"

@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    # 🚩 VULNERABILITY 2: SQL Injection
    # Using string formatting for DB queries is a critical risk
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return str(cursor.fetchone())

@app.route("/execute")
def run_command():
    cmd = request.args.get("cmd")

    # 🚩 VULNERABILITY 3: OS Command Injection
    # Directly passing user input to the shell
    os.system(f"echo {cmd}")
    return "Command executed"

@app.route("/load")
def load_data():
    data = request.args.get("data")

    # 🚩 VULNERABILITY 4: Insecure Deserialization
    # Using pickle on untrusted user data can lead to RCE
    decoded_data = base64.b64decode(data)
    obj = pickle.loads(decoded_data)
    return str(obj)

@app.route("/profile")
def view_profile():
    name = request.args.get("name", "Guest")

    # 🚩 VULNERABILITY 5: Reflected XSS
    # Directly rendering user input in HTML template without escaping
    return f"<h1>Welcome, {name}!</h1>"

@app.route("/read_log")
def read_log():
    filename = request.args.get("file")

    # 🚩 VULNERABILITY 6: Path Traversal
    # Allowing user to control file path can lead to reading sensitive files like /etc/passwd
    log_path = os.path.join("logs", filename)
    with open(log_path, "r") as f:
        return f.read()

@app.route("/fetch_url")
def fetch_external_url():
    target_url = request.args.get("url")

    # 🚩 VULNERABILITY 7: SSRF (Server-Side Request Forgery)
    # Fetching a URL provided by user without validation
    import requests
    response = requests.get(target_url)
    return response.text

@app.route("/api/admin/config/<user_id>")
def get_config(user_id):
    # 🚩 VULNERABILITY 8: Broken Access Control (IDOR)
    # No authentication or authorization check. Anyone can access any user's config by ID.
    return {"status": "success", "config": {"user": user_id, "role": "admin", "debug": True}}

if __name__ == "__main__":
    app.run(debug=True)
