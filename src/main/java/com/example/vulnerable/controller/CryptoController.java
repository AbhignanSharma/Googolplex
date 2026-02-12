package com.example.vulnerable.controller;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;
import java.security.SecureRandom;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.util.Base64;

@RestController
@RequestMapping("/api/crypto")
public class CryptoController {

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();
    private final SecureRandom secureRandom = new SecureRandom();

    // 1. Weak Hashing (MD5) Fix: Use BCrypt
    @GetMapping("/hash")
    public String secureHash(@RequestParam String input) {
        // SECURE: BCrypt is a slow, salted hash function suitable for passwords
        return passwordEncoder.encode(input);
    }

    // 2. Insecure Randomness Fix: Use SecureRandom
    @GetMapping("/token")
    public String generateToken() {
        // SECURE: SecureRandom is cryptographically strong
        byte[] bytes = new byte[32];
        secureRandom.nextBytes(bytes);
        return "Secure Token: " + Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    // 3. Hardcoded Encryption Key Fix: Use a generated key or one from secure
    // config
    @GetMapping("/encrypt")
    public String encrypt(@RequestParam String text) {
        try {
            // SECURE: Use AES/GCM/NoPadding for Authenticated Encryption
            KeyGenerator keyGen = KeyGenerator.getInstance("AES");
            keyGen.init(256);
            SecretKey key = keyGen.generateKey();

            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            byte[] iv = new byte[12];
            secureRandom.nextBytes(iv);
            GCMParameterSpec spec = new GCMParameterSpec(128, iv);

            cipher.init(Cipher.ENCRYPT_MODE, key, spec);
            byte[] cipherText = cipher.doFinal(text.getBytes());

            // Combine IV and CipherText
            byte[] combined = new byte[iv.length + cipherText.length];
            System.arraycopy(iv, 0, combined, 0, iv.length);
            System.arraycopy(cipherText, 0, combined, iv.length, cipherText.length);

            return Base64.getEncoder().encodeToString(combined);
        } catch (Exception e) {
            return "Encryption failed securely.";
        }
    }
}
