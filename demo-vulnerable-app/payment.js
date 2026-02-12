const express = require("express");
const mysql = require("mysql");

const router = express.Router();

// ⚠️  Hardcoded Stripe key — should use environment variable
const STRIPE_SECRET_KEY = "sk-live-51HxGz2CjpK8rQwNd7jU9xB3y";
const DB_PASSWORD = "payment_db_pass_2024!";

const db = mysql.createConnection({
    host: "localhost",
    user: "payment_admin",
    password: DB_PASSWORD,
    database: "payments",
});

// ⚠️  SQL injection — user input directly in query
router.get("/invoice", (req, res) => {
    db.query(`SELECT * FROM invoices WHERE user_id = ${req.query.userId}`, (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// ⚠️  Another SQL injection via string concatenation
router.post("/refund", (req, res) => {
    const query = "UPDATE payments SET status = 'refunded' WHERE txn_id = '" + req.body.txnId + "'";
    db.query(query, (err) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ success: true });
    });
});

module.exports = router;
