import os
import sqlite3
from flask import Flask, request

app = Flask(__name__)

# 🚩 VULNERABILITY 1: Hardcoded Secret
SECRET_KEY = "super-secret-key-12345"

@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    # 🚩 VULNERABILITY 2: SQL Injection
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return str(cursor.fetchone())

if __name__ == "__main__":
    app.run(debug=True)
