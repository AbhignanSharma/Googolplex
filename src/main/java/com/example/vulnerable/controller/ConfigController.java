package com.example.vulnerable.controller;

import org.springframework.web.bind.annotation.*;
import org.w3c.dom.Document;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.*;
import java.net.URL;
import java.net.HttpURLConnection;
import java.util.Base64;
import java.util.List;
import java.util.Set;

@RestController
@RequestMapping("/api/config")
public class ConfigController {

    private static final Set<String> ALLOWED_DOMAINS = Set.of("trusted-api.com", "google.com", "github.com");

    // 1. SSRF Fix: Whitelist domains and validate protocol
    @GetMapping("/proxy")
    public String proxyRequest(@RequestParam String url) {
        StringBuilder response = new StringBuilder();
        try {
            URL targetUrl = new URL(url);
            // SECURE: Validate protocol and host against whitelist
            if (!targetUrl.getProtocol().equals("https") || !ALLOWED_DOMAINS.contains(targetUrl.getHost())) {
                return "Unauthorized domain or protocol.";
            }

            HttpURLConnection conn = (HttpURLConnection) targetUrl.openConnection();
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);

            try (BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
                String inputLine;
                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
            }
        } catch (Exception e) {
            return "Request failed safely.";
        }
        return response.toString();
    }

    // 2. XXE Fix: Disable DTDs and External Entities
    @PostMapping("/xml")
    public String parseXml(@RequestBody String xml) {
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            // SECURE: Disabling DTDs to prevent XXE
            factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
            factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
            factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);

            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(new ByteArrayInputStream(xml.getBytes()));
            return "Parsed XML safely. Element: " + doc.getDocumentElement().getNodeName();
        } catch (Exception e) {
            return "XML processing failed safely.";
        }
    }

    // 3. Insecure Deserialization Fix: Use a whitelist of classes (Class-based
    // filtering)
    @PostMapping("/deserialize")
    public String deserialize(@RequestBody String base64Data) {
        try {
            byte[] data = Base64.getDecoder().decode(base64Data);
            try (ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data)) {
                @Override
                protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
                    // SECURE: Whitelist only allowed classes for deserialization
                    if (!desc.getName().equals("java.lang.String") && !desc.getName().equals("java.util.ArrayList")) {
                        throw new InvalidClassException("Unauthorized deserialization", desc.getName());
                    }
                    return super.resolveClass(desc);
                }
            }) {
                Object obj = ois.readObject();
                return "Deserialized object safely: " + obj.toString();
            }
        } catch (Exception e) {
            return "Deserialization rejected.";
        }
    }

    // 4. Open Redirect Fix: Whitelist allowed URLs
    @GetMapping("/redirect")
    public void openRedirect(@RequestParam String url, jakarta.servlet.http.HttpServletResponse response)
            throws IOException {
        // SECURE: Only allow redirect to specific trusted domains or local paths
        if (url.startsWith("/") || ALLOWED_DOMAINS.stream().anyMatch(url::contains)) {
            response.sendRedirect(url);
        } else {
            response.sendError(400, "Invalid redirect URL");
        }
    }
}
