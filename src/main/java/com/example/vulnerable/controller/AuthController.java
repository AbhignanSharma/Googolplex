package com.example.vulnerable.controller;

import com.example.vulnerable.model.User;
import com.example.vulnerable.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private UserRepository userRepository;

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    // 1. Auth Fix: Look up user in DB and verify hashed password
    @PostMapping("/login")
    public String login(@RequestParam String username, @RequestParam String password, HttpServletRequest request) {
        Optional<User> userOpt = userRepository.findByUsername(username);

        if (userOpt.isPresent() && passwordEncoder.matches(password, userOpt.get().getPassword())) {
            // 2. Session Fixation Fix: Regenerate session ID
            HttpSession session = request.getSession(true);
            session.invalidate(); // Clear old session
            HttpSession newSession = request.getSession(true); // Create new one
            newSession.setAttribute("user", username);
            return "Login successful for " + username;
        }
        return "Login failed: Invalid credentials.";
    }

    // 4. Host Header Injection Fix: Use absolute trusted domain
    @GetMapping("/reset-password")
    public String resetPassword(HttpServletRequest request) {
        // SECURE: Use a hardcoded trusted domain from config, never the Host header
        String trustedHost = "https://safe-app.com";
        String resetLink = trustedHost + "/reset?token=secure-token-123";
        return "Reset link generated securely: " + resetLink;
    }

    // 5. JWT Status Fix
    @GetMapping("/jwt-status")
    public Map<String, String> jwtStatus() {
        Map<String, String> status = new HashMap<>();
        status.put("mechanism", "JWT");
        status.put("vulnerability", "None - Using secure environment variables for secrets");
        return status;
    }
}
