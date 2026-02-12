package com.example.vulnerable.controller;

import org.springframework.web.bind.annotation.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.io.IOException;

@RestController
@RequestMapping("/api/stupid")
public class StupidMistakesController {

    // 1. Null Pointer Fix: Add null check
    @GetMapping("/null-risk")
    public String nullRisk(@RequestParam(required = false) String input) {
        // SECURE: Check for null/empty input
        if (input == null || input.isEmpty()) {
            return "Input is empty.";
        }
        return "Input length: " + input.length();
    }

    // 2. Hardcoded Password Fix: Removed.

    @GetMapping("/get-pass")
    public String getPass() {
        return "The secret is no longer here.";
    }

    // 3. Infinite Recursion Fix: Add logic to decrement or base case
    @GetMapping("/loop")
    public String loop(@RequestParam int n) {
        if (n <= 0)
            return "Done";
        // SECURE: Logic fixed to prevent stack overflow
        return "Processed " + n + " more times.";
    }

    // 4. Hardcoded File Path Fix: Sanitize and restrict to directory
    @GetMapping("/read-secret")
    public String readSecret(@RequestParam String fileName) throws IOException {
        // SECURE: Strip path components and ensure it's in the 'secrets' folder
        String safeName = Paths.get(fileName).getFileName().toString();
        Path path = Paths.get("src/main/resources/secrets").resolve(safeName).normalize();

        if (!path.startsWith(Paths.get("src/main/resources/secrets").toAbsolutePath().normalize())) {
            return "Access denied.";
        }
        return new String(Files.readAllBytes(path));
    }
}
