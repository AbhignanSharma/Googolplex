import os
import sqlite3
import pickle
import base64
from flask import Flask, request

app = Flask(__name__)

# 🔶 VULNERABILITY 1: Hardcoded Secret
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "fallback-in-dev-only")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db") # Fallback to SQLite for local dev

@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    # 🔶 VULNERABILITY 2: SQL Injection
    # Using string formatting for DB queries is a critical risk
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Use parameterized queries to prevent SQL Injection
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return str(cursor.fetchone())

@app.route("/execute")
def run_command():
    import subprocess
    cmd = request.args.get("cmd")

    # 🔶 VULNERABILITY 3: OS Command Injection
    # Directly passing user input to the shell
    # Use subprocess.run with shell=False and command as a list to prevent OS command injection
    # This example only echoes the command, for real commands, ensure strict whitelisting.
    try:
        result = subprocess.run(["echo", cmd], capture_output=True, text=True, check=True)
        return f"Command executed: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.stderr}", 500

@app.route("/load")
def load_data():
    data = request.args.get("data")

    # 🔶 VULNERABILITY 4: Insecure Deserialization
    # Using pickle on untrusted user data can lead to RCE
    # Insecure Deserialization via pickle.loads() is a critical RCE vulnerability.
    # NEVER deserialize untrusted data with pickle.
    # Replacing with a strict error as safe deserialization of arbitrary objects is not possible.
    # If deserialization is truly needed, use a secure format like JSON (with object_hook for specific types)
    # and strictly validate input.
    raise ValueError("Insecure deserialization of untrusted data is prohibited.")

@app.route("/profile")
def view_profile():
    from markupsafe import escape
    name = request.args.get("name", "Guest")

    # 🔶 VULNERABILITY 5: Reflected XSS
    # Directly rendering user input in HTML template without escaping
    # HTML-escape user input to prevent XSS
    return f"<h1>Welcome, {escape(name)}!</h1>"

@app.route("/read_log")
def read_log():
    from werkzeug.utils import safe_join
    from flask import abort
    filename = request.args.get("file")

    # 🔶 VULNERABILITY 6: Path Traversal
    # Allowing user to control file path can lead to reading sensitive files like /etc/passwd
    # Use safe_join to ensure the filename stays within the "logs" directory
    log_path = safe_join("logs", filename)
    if log_path is None:
        abort(400, "Invalid filename provided.")
    try:
        with open(log_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        abort(404, "Log file not found.")

@app.route("/fetch_url")
def fetch_external_url():
    import requests
    import urllib.parse
    import ipaddress
    import socket
    target_url = request.args.get("url")

    # 🔶 VULNERABILITY 7: SSRF (Server-Side Request Forgery)
    # Fetching a URL provided by user without validation
    # Basic URL validation to prevent common SSRF vectors
    parsed_url = urllib.parse.urlparse(target_url)
    if parsed_url.scheme not in ['http', 'https']:
        return "Invalid scheme", 400
    try:
        # Resolve hostname to check against private IP ranges
        hostname = parsed_url.hostname
        if hostname == 'localhost' or hostname == '127.0.0.1':
            return "Access to localhost is forbidden", 403
        for res_ip in socket.gethostbyname_ex(hostname)[2]:
            ip = ipaddress.ip_address(res_ip)
            if ip.is_private or ip.is_loopback:
                return "Access to private/loopback IPs is forbidden", 403
    except (socket.gaierror, ValueError):
        return "Invalid URL hostname", 400
    
    response = requests.get(target_url)
    return response.text

@app.route("/api/admin/config/<user_id>")
def get_config(user_id):
    from flask import jsonify

    # 🔶 VULNERABILITY 8: Broken Access Control (IDOR)
    # No authentication or authorization check. Anyone can access any user\'s config by ID.
    # Placeholder for actual authentication and authorization
    # In a real application, implement @login_required decorator and check user roles/permissions.
    # Example: if not current_user.is_authenticated or not current_user.is_admin:
    # return jsonify({"error": "Unauthorized"}), 401
    # Example: if user_id != str(current_user.id) and not current_user.is_admin:
    # return jsonify({"error": "Forbidden"}), 403
    
    # For this minimal fix, we deny access to any user_id by default as no auth is available.
    return jsonify({"error": "Authentication and Authorization Required"}), 401

if __name__ == "__main__":
    # Disable debug mode for production deployments to prevent RCE
    # Use an environment variable to control debug mode, defaulting to False for safety
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
