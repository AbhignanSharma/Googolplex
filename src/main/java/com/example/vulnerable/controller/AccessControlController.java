package com.example.vulnerable.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.IOException;

@RestController
@RequestMapping("/api/access")
public class AccessControlController {

    // 1. IDOR Fix: Verify ownership (Simplified simulation)
    @GetMapping("/user/{id}/profile")
    public String getUserProfile(@PathVariable String id, Authentication auth) {
        // SECURE: Only allow users to access their own profile
        if (auth == null || !auth.getName().equals(id) && !auth.getAuthorities().toString().contains("ROLE_ADMIN")) {
            return "Unauthorized: You can only view your own profile.";
        }
        return "Profile data for user " + id + " : {ssn: '123-456-789', creditCard: 'xxxx-xxxx-xxxx-1234'}";
    }

    // 2. Path Traversal (Read) Fix: Validate filename and restricted to home
    @GetMapping("/files/download")
    public byte[] downloadFile(@RequestParam String filename) throws IOException {
        // SECURE: Strip path components and ensure it's within the 'uploads' directory
        String safeName = Paths.get(filename).getFileName().toString();
        Path path = Paths.get("uploads").resolve(safeName).normalize();

        if (!path.startsWith(Paths.get("uploads").toAbsolutePath().normalize())) {
            throw new SecurityException("Illegal file access attempt");
        }
        return Files.readAllBytes(path);
    }

    // 3. Path Traversal (Write) Fix
    @PostMapping("/files/upload")
    public String uploadFile(@RequestParam String filename, @RequestBody String content) throws IOException {
        String safeName = Paths.get(filename).getFileName().toString();
        Path path = Paths.get("uploads").resolve(safeName).normalize();

        Files.write(path, content.getBytes());
        return "File uploaded safely: " + safeName;
    }

    // 4. Broken Function Level Access Control Fix
    @GetMapping("/admin/users")
    @PreAuthorize("hasRole('ADMIN')")
    public String listAllUsers() {
        return "Listing all users... [Secure Admin Access Only]";
    }
}
