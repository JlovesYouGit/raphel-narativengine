import std.net.*;
import java.security.*;
import java.time.*;
import java.io.*;

public class IPMasker {
    private final String layer1Salt = "first-layer-salt-2025";
    private final String layer2Salt = "second-layer-salt-2025";
    private final String layer3Salt = "third-layer-salt-2025";

    public static class MaskResult {
        public final String original;
        public final String layer1;
        public final String layer2;
        public final String layer3;
        public final LocalDateTime timestamp;

        public MaskResult(String original, String layer1, String layer2, String layer3) {
            this.original = original;
            this.layer1 = layer1;
            this.layer2 = layer2;
            this.layer3 = layer3;
            this.timestamp = LocalDateTime.now();
        }
    }

    public String getPublicIP() throws Exception {
        URL url = new URL("https://api.ipsimple.org/ipv4");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(conn.getInputStream()))) {
            String ip = reader.readLine();
            return ip.trim();
        }
    }

    public String sha256Hash(String data, String salt) throws NoSuchAlgorithmException {
        String input = data + salt;
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(input.getBytes());
        
        StringBuilder hexString = new StringBuilder();
        for (byte b : hash) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        return hexString.toString();
    }

    public MaskResult maskIP(String ip) throws NoSuchAlgorithmException {
        System.out.println("Original IP: " + ip);

        String layer1 = sha256Hash(ip, layer1Salt);
        System.out.println("Layer 1 Hash: " + layer1);

        String layer2 = sha256Hash(layer1, layer2Salt);
        System.out.println("Layer 2 Hash: " + layer2);

        String layer3 = sha256Hash(layer2, layer3Salt);
        System.out.println("Layer 3 Hash: " + layer3);

        return new MaskResult(ip, layer1, layer2, layer3);
    }

    public MaskResult getAndMaskIP() throws Exception {
        String ip = getPublicIP();
        return maskIP(ip);
    }

    public static void main(String[] args) {
        IPMasker masker = new IPMasker();

        System.out.println("=== 3-Layer SHA-256 IP Masking System ===");
        System.out.println("Detecting and masking current IP address...\n");

        try {
            MaskResult result = masker.getAndMaskIP();

            System.out.println("\n=== Final Result ===");
            System.out.println("Original IP: " + result.original);
            System.out.println("Final Masked IP: " + result.layer3);
            System.out.println("Timestamp: " + result.timestamp);

            System.out.println("\n=== Network Encryption Simulation ===");
            System.out.println("Packet routing through encrypted layers:");
            System.out.println("[Network] --> Layer1: " + result.layer1.substring(0, 16) + "...");
            System.out.println("[Layer1] --> Layer2: " + result.layer2.substring(0, 16) + "...");
            System.out.println("[Layer2] --> Layer3: " + result.layer3.substring(0, 16) + "...");
            System.out.println("[Layer3] --> Internet (Fully Encrypted)");

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
