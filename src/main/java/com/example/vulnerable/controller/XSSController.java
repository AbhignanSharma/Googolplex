package com.example.vulnerable.controller;

import com.example.vulnerable.model.Comment;
import com.example.vulnerable.repository.CommentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/xss")
public class XSSController {

    @Autowired
    private CommentRepository commentRepository;

    // 1. Reflected XSS
    @GetMapping("/reflected")
    public String reflectedXss(@RequestParam String name, Model model) {
        // VULNERABLE: Direct rendering of unsanitized input
        model.addAttribute("name", name);
        return "reflected";
    }

    // 2. Stored XSS
    @GetMapping("/comments")
    public String listComments(Model model) {
        model.addAttribute("comments", commentRepository.findAll());
        return "comments";
    }

    @PostMapping("/comments")
    public String addComment(@RequestParam String text) {
        Comment comment = new Comment();
        comment.setText(text); // VULNERABLE: Saving unsanitized input
        commentRepository.save(comment);
        return "redirect:/xss/comments";
    }

    // 3. DOM-based XSS (Demonstrated in the template)
    @GetMapping("/dom")
    public String domXss() {
        return "dom";
    }
}
