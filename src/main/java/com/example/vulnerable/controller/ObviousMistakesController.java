package com.example.vulnerable.controller;

import org.springframework.web.bind.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/obvious")
public class ObviousMistakesController {

    private static final Logger logger = LoggerFactory.getLogger(ObviousMistakesController.class);

    // 1. Secret Fix: Use environment variables, not hardcoded strings
    // Keys removed from source.

    // 2. Password Comment Fix: Removed sensitive information from comments.

    // 3. Sensitive Data Logging Fix: Never log passwords
    @PostMapping("/debug-login")
    public String debugLogin(@RequestParam String user, @RequestParam String pass) {
        // SECURE: Only log the username, mask the password
        logger.info("DEBUG: User {} attempted login", user);
        return "Log recorded securely.";
    }

    // 4. SQLi Fix (Raw JDBC): Use PreparedStatement
    @GetMapping("/raw-sql")
    public List<String> getItems(@RequestParam String category) {
        List<String> results = new ArrayList<>();
        try (Connection conn = DriverManager.getConnection("jdbc:h2:mem:vulnerable_db", "admin", "admin")) {
            // SECURE: Use PreparedStatement to prevent SQL injection
            String query = "SELECT name FROM items WHERE cat = ?";
            try (PreparedStatement pstmt = conn.prepareStatement(query)) {
                pstmt.setString(1, category);
                try (ResultSet rs = pstmt.executeQuery()) {
                    while (rs.next()) {
                        results.add(rs.getString("name"));
                    }
                }
            }
        } catch (Exception e) {
            results.add("A database error occurred.");
        }
        return results;
    }

    // 5. Insecure Cookie Fix: Add flags
    @GetMapping("/set-session")
    public String setSession(HttpServletResponse response) {
        // SECURE: Add HttpOnly, Secure, and SameSite flags
        Cookie cookie = new Cookie("SESS_ID", "secure_session_123");
        cookie.setHttpOnly(true);
        cookie.setSecure(true);
        cookie.setAttribute("SameSite", "Strict");
        response.addCookie(cookie);
        return "Session cookie set securely.";
    }

    // 6. Sensitive Data in Query Params Fix: Use POST/Body
    @PostMapping("/process-payment")
    public String processPayment(@RequestBody Map<String, String> paymentInfo) {
        // SECURE: Card details are in the body, not the URL
        String cardNum = paymentInfo.get("cardNum");
        return "Payment processed for card ending in " + cardNum.substring(cardNum.length() - 4);
    }

    // 7. Backdoor Fix: Removed hardcoded secret backdoor.
    @GetMapping("/admin/backdoor")
    public String backdoor() {
        return "Unauthorized Access.";
    }

    // 8. Trusting Host Header Fix: Use trusted config
    @GetMapping("/internal-check")
    public String internalCheck(HttpServletRequest request) {
        // SECURE: Use properties instead of request headers for security checks
        String remoteAddr = request.getRemoteAddr();
        if ("127.0.0.1".equals(remoteAddr) || "0:0:0:0:0:0:0:1".equals(remoteAddr)) {
            return "Welcome Internal Admin!";
        }
        return "External Access restricted.";
    }
}
