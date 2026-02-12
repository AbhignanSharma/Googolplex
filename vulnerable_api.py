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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
