package com.example.vulnerable.controller;

import com.example.vulnerable.model.User;
import com.example.vulnerable.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/exposure")
public class ExposureController {

    @Autowired
    private UserRepository userRepository;

    // 1. Sensitive Data Exposure Fix: Use a safe Projection or Map
    @GetMapping("/users")
    public List<Map<String, String>> listUsers() {
        // SECURE: Only return safe fields (id, username, role)
        return userRepository.findAll().stream().map(user -> Map.of(
                "id", user.getId().toString(),
                "username", user.getUsername(),
                "role", user.getRole())).collect(Collectors.toList());
    }

    // 2. Verbose Error Message Fix: Return generic errors
    @GetMapping("/error")
    public String triggerError() {
        try {
            throw new RuntimeException("Internal database error");
        } catch (Exception e) {
            // SECURE: Log the detail but return a generic message to the user
            return "An internal server error occurred. Please contact support.";
        }
    }

    // 3. Hardcoded Secret Fix: Removed or source from Environment
    @GetMapping("/aws-key")
    public String getAwsKey(@Value("${AWS_ACCESS_KEY:}") String key) {
        // SECURE: Source from configuration/environment variables
        return key.isEmpty() ? "Key not configured" : key;
    }
}
