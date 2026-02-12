import os
import sqlite3
import pickle
import base64
import logging
import subprocess
import pathlib
from markupsafe import escape
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
        # Fix for Insecure Deserialization: Block deserialization of untrusted data
        return jsonify({"status": "Deserialization blocked", "error": "Insecure deserialization is not allowed"})
    return "No data provided"

# 🚩 VULNERABILITY 7: Broken Access Control / IDOR (High)
# CWE-639: Authorization Bypass Through User-Controlled Key
# Allows any user to read internal system configs by changing the user_id.
@app.route("/api/v1/admin/config/<user_id>")
def get_admin_config(user_id):
    # Fix for Broken Access Control: Implement proper authentication and authorization checks
    # TODO: Implement proper authentication and authorization checks
    if user_id != 'admin': # Example: only 'admin' can access certain configs
        return jsonify({"error": "Unauthorized access"}), 403
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

    # Fix for Sensitive Data Leakage in Logs: Do not log plaintext passwords
    logging.info(f"Login attempt for user: {username}")

    return jsonify({"status": "Login processed"})

# 🚩 VULNERABILITY 9: SQL Injection (Critical)
# CWE-89: Improper Neutralization of Special Elements used in an SQL Command
@app.route("/api/v1/users/search")
def search_users():
    username = request.args.get("username")
    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    # Fix for SQL Injection: Use parameterized queries
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    results = cursor.fetchall()
    return jsonify({"results": results})

# 🚩 VULNERABILITY 10: OS Command Injection (Critical)
# CWE-78: Improper Neutralization of Special Elements used in an OS Command
@app.route("/api/v1/system/ping")
def ping_host():
    host = request.args.get("host")
    # Fix for OS Command Injection: Use subprocess.run with shell=False
    try:
        subprocess.run(["ping", "-c", "1", host], check=True)
        return jsonify({"status": "Ping executed successfully", "host": host})
    except subprocess.CalledProcessError:
        return jsonify({"status": "Ping failed", "host": host}), 500

# 🚩 VULNERABILITY 11: Path Traversal (High)
# CWE-22: Improper Limitation of a Pathname to a Restricted Directory
@app.route("/api/v1/files/download")
def download_file():
    filename = request.args.get("filename")
    # Fix for Path Traversal: Canonicalize path and ensure it's within allowed directory
    base_dir = pathlib.Path("uploads").resolve()
    requested_path = (base_dir / filename).resolve()
    if not requested_path.is_relative_to(base_dir):
        return "Access Denied", 403
    if requested_path.exists() and requested_path.is_file():
        with open(requested_path, "r") as f:
            return f.read()
    return "File not found", 404

# 🚩 VULNERABILITY 12: Reflected Cross-Site Scripting (XSS) (Medium)
# CWE-79: Improper Neutralization of Input During Web Page Generation
@app.route("/api/v1/hello")
def hello_user():
    name = request.args.get("name", "Guest")
    # Fix for Reflected Cross-Site Scripting (XSS): HTML escape user input
    return f"<h1>Hello, {escape(name)}!</h1>"

if __name__ == "__main__":
    # 🚩 VULNERABILITY 13: Insecure Deployment (Low)
    # Debug mode enabled in production-like setting
    # Fix for Insecure Deployment: Disable debug mode in production
    app.run(host='0.0.0.0', port=5000)