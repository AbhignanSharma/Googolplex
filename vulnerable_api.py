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

if __name__ == "__main__":
    app.run(debug=True)
