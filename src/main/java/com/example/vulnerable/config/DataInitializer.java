package com.example.vulnerable.config;

import com.example.vulnerable.model.User;
import com.example.vulnerable.model.Comment;
import com.example.vulnerable.repository.UserRepository;
import com.example.vulnerable.repository.CommentRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitializer {

    @Bean
    public CommandLineRunner initData(UserRepository userRepository, CommentRepository commentRepository) {
        return args -> {
            // Seed Users with sensitive data
            User admin = new User();
            admin.setUsername("admin");
            admin.setPassword("admin"); // Plain text
            admin.setRole("ADMIN");
            admin.setSsn("000-00-0000");
            admin.setCreditCard("1111-2222-3333-4444");
            userRepository.save(admin);

            User victim = new User();
            victim.setUsername("victim");
            victim.setPassword("password123");
            victim.setRole("USER");
            victim.setSsn("123-45-6789");
            victim.setCreditCard("4321-8765-4321-0987");
            userRepository.save(victim);

            // Seed Comments for XSS
            Comment c1 = new Comment();
            c1.setText("Hello World!");
            c1.setAuthor("user1");
            commentRepository.save(c1);

            Comment c2 = new Comment();
            c2.setText("<script>alert('XSS')</script>"); // Stored XSS payload
            c2.setAuthor("hacker");
            commentRepository.save(c2);
        };
    }
}
