import os
import sqlite3
import pickle
import base64
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 🚩 VULNERABILITY 6: Insecure Deserialization (Critical)
# CWE-502: Deserialization of Untrusted Data
# Allows Remote Code Execution (RCE) via malicious pickle payloads.
@app.route("/api/v1/load-session")
def load_session():
    data = request.args.get("data")
    if data:
        decoded_data = base64.b64decode(data)
        session_obj = pickle.loads(decoded_data)
        return jsonify({"status": "Session loaded", "user": str(session_obj)})
    return "No data provided"

# 🚩 VULNERABILITY 7: Broken Access Control / IDOR (High)
# CWE-639: Authorization Bypass Through User-Controlled Key
# Allows any user to read internal system configs by changing the user_id.
@app.route("/api/v1/admin/config/<user_id>")
def get_admin_config(user_id):
    # Missing authentication and authorization checks
    config_store = {
        "admin": {"role": "superuser", "debug": True, "env": "prod"},
        "system": {"internal_ip": "10.0.0.5", "db_access": "RW"}
    }
    return jsonify(config_store.get(user_id, {"error": "User not found"}))

# 🚩 VULNERABILITY 8: Sensitive Data Leakage in Logs (Medium)
# CWE-532: Insertion of Sensitive Information into Log File
@app.route("/api/v1/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Intentionally logging the plaintext password - Security Risk!
    logging.info(f"Login attempt for user: {username} with password: {password}")

    return jsonify({"status": "Login processed"})

# 🚩 VULNERABILITY 9: SQL Injection (Critical)
# CWE-89: Improper Neutralization of Special Elements used in an SQL Command
@app.route("/api/v1/users/search")
def search_users():
    username = request.args.get("username")
    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    # Unsafe string formatting for SQL query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    results = cursor.fetchall()
    return jsonify({"results": results})

# 🚩 VULNERABILITY 10: OS Command Injection (Critical)
# CWE-78: Improper Neutralization of Special Elements used in an OS Command
@app.route("/api/v1/system/ping")
def ping_host():
    host = request.args.get("host")
    # Unsafe usage of os.system with user-controlled input
    command = f"ping -c 1 {host}"
    os.system(command)
    return jsonify({"status": "Ping executed", "command": command})

# 🚩 VULNERABILITY 11: Path Traversal (High)
# CWE-22: Improper Limitation of a Pathname to a Restricted Directory
@app.route("/api/v1/files/download")
def download_file():
    filename = request.args.get("filename")
    # Vulnerable to ../ path traversal
    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return "File not found", 404

# 🚩 VULNERABILITY 12: Reflected Cross-Site Scripting (XSS) (Medium)
# CWE-79: Improper Neutralization of Input During Web Page Generation
@app.route("/api/v1/hello")
def hello_user():
    name = request.args.get("name", "Guest")
    # Directly embedding user input in HTML response
    return f"<h1>Hello, {name}!</h1>"

if __name__ == "__main__":
    # 🚩 VULNERABILITY 13: Insecure Deployment (Low)
    # Debug mode enabled in production-like setting
    app.run(host='0.0.0.0', port=5000, debug=True)
