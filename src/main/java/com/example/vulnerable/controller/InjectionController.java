package com.example.vulnerable.controller;

import com.example.vulnerable.model.User;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.Query;
import org.springframework.expression.Expression;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.SimpleEvaluationContext;
import org.springframework.web.bind.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Collections;
import java.util.List;

@RestController
@RequestMapping("/api/injection")
public class InjectionController {

    private static final Logger logger = LoggerFactory.getLogger(InjectionController.class);

    @PersistenceContext
    private EntityManager entityManager;

    // 1. SQLi Fix: Parameterized Native Query
    @GetMapping("/sql/native")
    public List<User> findUsersNative(@RequestParam String name) {
        String query = "SELECT * FROM users WHERE username = :name";
        return entityManager.createNativeQuery(query, User.class)
                .setParameter("name", name)
                .getResultList();
    }

    // 2. SQLi Fix: Parameterized JPQL
    @GetMapping("/sql/jpql")
    public List<User> findUsersJPQL(@RequestParam String name) {
        String query = "SELECT u FROM User u WHERE u.username = :name";
        return entityManager.createQuery(query, User.class)
                .setParameter("name", name)
                .getResultList();
    }

    // 3. Command Injection Fix: ProcessBuilder with restricted commands
    @GetMapping("/command")
    public String executeCommand(@RequestParam String cmd) {
        // SECURE: Whitelist allowed commands and use ProcessBuilder
        if (!List.of("ls", "whoami", "date").contains(cmd)) {
            return "Command not allowed.";
        }

        StringBuilder output = new StringBuilder();
        try {
            ProcessBuilder pb = new ProcessBuilder(cmd);
            Process p = pb.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
        return output.toString();
    }

    // 4. SpEL Injection Fix: Use SimpleEvaluationContext (no access to Java
    // types/constructors)
    @GetMapping("/spel")
    public String evaluateSpEL(@RequestParam String expression) {
        try {
            SpelExpressionParser parser = new SpelExpressionParser();
            Expression exp = parser.parseExpression(expression);
            // SECURE: SimpleEvaluationContext prevents dangerous SpEL features
            Object value = exp.getValue(SimpleEvaluationContext.forReadOnlyDataBinding().build());
            return value != null ? value.toString() : "null";
        } catch (Exception e) {
            return "Error processed securely.";
        }
    }

    // 5. Log Injection Fix: Sanitize input (remove CRLF)
    @GetMapping("/log")
    public String logInput(@RequestParam String input) {
        // SECURE: Sanitize log input to prevent log forging
        String sanitized = input.replaceAll("[\n\r]", "_");
        logger.info("User requested log with sanitized input: " + sanitized);
        return "Logged safely: " + sanitized;
    }
}
