# Secure App - Hardened Spring Boot Case Study

This project is the **Secure Version** of the vulnerable application project. It has been hardened to fix over **60 security vulnerabilities**, serving as a reference implementation for secure coding practices in Spring Boot.

## 🚀 Getting Started

1.  **Clone/Open** the project in your IDE.
2.  **Build** using Maven: `mvn clean install`
3.  **Run**: `mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=8081`
    *Note: This app runs on port **8081** by default to allow side-by-side comparison with the vulnerable version.*
4.  **H2 Console**: Disabled in production properties for security.

## 🛡️ Security Hardening Overview

### 1. General Infrastructure
- **Port 8081**: Configured to avoid conflict with the vulnerable app.
- **CSRF Protection**: Enabled globally.
- **Strict CORS**: Restricted to specific trusted domains.
- **Password Hashing**: Upgraded all authentication to use **BCrypt**.

### 2. Injection Prevention
- **SQL Injection**: Replaced all string concatenation with **Parameterized Queries** and **PreparedStatement**.
- **Command Injection**: Implemented a **Whitelist** of allowed commands and used `ProcessBuilder`.
- **SpEL Injection**: Switched to `SimpleEvaluationContext` for limited, safe evaluation.
- **Log Injection**: Sanitized all user inputs by removing newline characters before logging.

### 3. Cross-Site Scripting (XSS)
- **Auto-Escaping**: Updated Thymeleaf templates to use `th:text` (escaping) instead of `th:utext`.
- **DOM Sanitization**: Replaced `innerHTML` with `textContent` in JavaScript.

### 4. Broken Access Control
- **IDOR**: Implemented ownership checks by verifying the authenticated user against the requested resource ID.
- **Path Traversal**: Sanitized filenames using `Paths.get().getFileName()` and validated that paths remain within the `uploads/` directory.
- **RBAC**: Added `@PreAuthorize("hasRole('ADMIN')")` to sensitive endpoints.

### 5. Cryptography & Data Protection
- **Strong Hashing**: MD5 replaced with BCrypt.
- **Secure Randomness**: `SecureRandom` used for all token and crypto operations.
- **Authenticated Encryption**: Upgraded AES to `AES/GCM/NoPadding` with securely generated keys.
- **PII Filtering**: Sensitive fields (SSN, Passwords) are filtered out using DTOs or Map-based projections.

### 6. Misconfiguration & Logic
- **SSRF/Redirects**: Implemented a rigid **Whitelist** for target domains.
- **XXE**: Disabled DTDs and External Entities in XML parsers.
- **Deserialization**: Implemented class-based whitelisting for `ObjectInputStream`.
- **Race Condition**: Synchronized shared state to prevent multi-threading logic errors.
- **Default Creds**: Removed all hardcoded credentials; replaced with dynamic lookup.

## 🎯 Comparison
Use this application to verify the efficacy of your "Security Guardian" agent. It should detect high security parity when comparing the `vulnerable-app` logic against this `secure-app`.
