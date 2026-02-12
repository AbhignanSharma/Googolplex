import os
import sqlite3
import pickle
import base64
from flask import Flask, request, redirect, url_for
import subprocess
import json
from markupsafe import escape
from urllib.parse import urlparse
from ipaddress import ip_address, ip_network
import socket
import requests # Moved from inside function to here

app = Flask(__name__)

# 🚩 VULNERABILITY 1: Hardcoded Secret
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("FLASK_SECRET_KEY environment variable not set. This is a critical security risk.")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. This is a critical security risk.")

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

    # 🚩 VULNERABILITY 3: OS Command Injection
    # Directly passing user input to the shell
    if cmd: # Basic validation that cmd is not empty
        subprocess.run(["echo", cmd], check=True, text=True) # Executes 'echo <cmd>', not '<cmd>' as a shell command
    return "Command executed"

@app.route("/load")
def load_data():
    data = request.args.get("data")

    # 🚩 VULNERABILITY 4: Insecure Deserialization
    # Using pickle on untrusted user data can lead to RCE
    try:
        decoded_data = base64.b64decode(data).decode('utf-8')
        obj = json.loads(decoded_data)
    except (json.JSONDecodeError, UnicodeDecodeError, base64.binascii.Error) as e:
        return f"Error decoding or deserializing data: {e}", 400
    return str(obj)

@app.route("/profile")
def view_profile():
    name = request.args.get("name", "Guest")

    # 🚩 VULNERABILITY 5: Reflected XSS
    # Directly rendering user input in HTML template without escaping
    return f"<h1>Welcome, {escape(name)}!</h1>"

@app.route("/read_log")
def read_log():
    filename = request.args.get("file")

    # 🚩 VULNERABILITY 6: Path Traversal
    # Allowing user to control file path can lead to reading sensitive files like /etc/passwd
    base_log_dir = os.path.abspath("logs")
    if not os.path.exists(base_log_dir):
        os.makedirs(base_log_dir)

    requested_path = os.path.abspath(os.path.join(base_log_dir, filename))

    if not requested_path.startswith(base_log_dir):
        return "Access denied: Path traversal attempt detected.", 403

    if not os.path.isfile(requested_path):
        return "File not found or not a regular file.", 404

    with open(requested_path, "r") as f:
        return f.read()

@app.route("/fetch_url")
def fetch_external_url():
    target_url = request.args.get("url")

    # 🚩 VULNERABILITY 7: SSRF (Server-Side Request Forgery)
    # Fetching a URL provided by user without validation
    # Validate target_url against a whitelist or internal IP restrictions
    parsed_url = urlparse(target_url)
    if parsed_url.scheme not in ('http', 'https'):
        return "Invalid URL scheme.", 400

    # Robust check for private/internal IPs, including DNS resolution
    is_private_ip = False
    hostname = parsed_url.hostname
    if hostname:
        try:
            ip = ip_address(hostname)
            if ip.is_private or ip.is_loopback:
                is_private_ip = True
            elif ip in ip_network('169.254.0.0/16'): # Link-local including AWS metadata
                is_private_ip = True
        except ValueError: # Not an IP address, could be a hostname
            try:
                # Resolve hostname to IP addresses and check if any are private
                resolved_ips = socket.gethostbyname_ex(hostname)[2]
                for resolved_ip in resolved_ips:
                    ip = ip_address(resolved_ip)
                    if ip.is_private or ip.is_loopback or ip in ip_network('169.254.0.0/16'):
                        is_private_ip = True
                        break
            except socket.gaierror:
                pass # Hostname not resolvable, treat as external for this basic check

    if is_private_ip:
        return "Access to internal/reserved IPs or cloud metadata is forbidden.", 403

    try:
        response = requests.get(target_url, timeout=5) # Add a timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}", 400

@app.route("/api/admin/config/<user_id>")
def get_config(user_id):
    # 🚩 VULNERABILITY 8: Broken Access Control (IDOR)
    # No authentication or authorization check. Anyone can access any user\'s config by ID.
    return {"status": "error", "message": "Authentication and Authorization required to access user configurations."},
 401

@app.route("/redirect")
def open_redirect():
    # 🚩 VULNERABILITY 9: Open Redirect
    # Unvalidated user-supplied input in redirect target
    target = request.args.get("url")
    if target and urlparse(target).netloc == request.host:
        return redirect(target)
    elif target and not urlparse(target).netloc: # Is a relative path
        return redirect(target)
    else:
        # Fallback to a safe default page or show an error
        return redirect(url_for('view_profile')) # Redirect to a safe internal page (e.g., profile)

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")