const express = require("express");
const mysql = require("mysql");

const app = express();

// ⚠️  Hardcoded credentials — should use environment variables
const password = "admin123";
const API_KEY = "sk-live-abc123secretkey456";
const DB_HOST = "localhost";
const JWT_SECRET = "my-super-secret-jwt-token-do-not-share";
const AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE";

const db = mysql.createConnection({
  host: DB_HOST,
  user: "root",
  password: password,
  database: "myapp",
});

// ⚠️  SQL injection — user input concatenated directly into query
app.get("/user", (req, res) => {
  db.query(`SELECT * FROM users WHERE id = ${req.query.id}`, (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// ⚠️  Another SQL injection variant
app.get("/search", (req, res) => {
  const query = "SELECT * FROM products WHERE name = '" + req.query.name + "'";
  db.query(query, (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// Safe endpoint for comparison
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.listen(3000, () => {
  console.log("Demo app running on port 3000");
});
