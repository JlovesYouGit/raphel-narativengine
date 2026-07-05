use std::collections::HashMap;
use std::error::Error;
use std::time::{SystemTime, UNIX_EPOCH};
use sha2::{Sha256, Digest};

struct IPMasker {
    layer1_salt: String,
    layer2_salt: String,
    layer3_salt: String,
}

#[derive(Debug)]
struct MaskResult {
    original: String,
    layer1: String,
    layer2: String,
    layer3: String,
    timestamp: u64,
}

impl IPMasker {
    fn new() -> Self {
        IPMasker {
            layer1_salt: "first-layer-salt-2025".to_string(),
            layer2_salt: "second-layer-salt-2025".to_string(),
            layer3_salt: "third-layer-salt-2025".to_string(),
        }
    }

    async fn get_public_ip(&self) -> Result<String, Box<dyn Error>> {
        let response = reqwest::get("https://api.ipsimple.org/ipv4").await?;
        let ip = response.text().await?;
        Ok(ip.trim().to_string())
    }

    fn sha256_hash(&self, data: &str, salt: &str) -> String {
        let input = format!("{}{}", data, salt);
        let mut hasher = Sha256::new();
        hasher.update(input.as_bytes());
        let result = hasher.finalize();
        hex::encode(result)
    }

    fn mask_ip(&self, ip: &str) -> MaskResult {
        println!("Original IP: {}", ip);

        let layer1 = self.sha256_hash(ip, &self.layer1_salt);
        println!("Layer 1 Hash: {}", layer1);

        let layer2 = self.sha256_hash(&layer1, &self.layer2_salt);
        println!("Layer 2 Hash: {}", layer2);

        let layer3 = self.sha256_hash(&layer2, &self.layer3_salt);
        println!("Layer 3 Hash: {}", layer3);

        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        MaskResult {
            original: ip.to_string(),
            layer1,
            layer2,
            layer3,
            timestamp,
        }
    }

    async fn get_and_mask_ip(&self) -> Result<MaskResult, Box<dyn Error>> {
        let ip = self.get_public_ip().await?;
        Ok(self.mask_ip(&ip))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let masker = IPMasker::new();

    println!("=== 3-Layer SHA-256 IP Masking System ===");
    println!("Detecting and masking current IP address...\n");

    let result = masker.get_and_mask_ip().await?;

    println!("\n=== Final Result ===");
    println!("Original IP: {}", result.original);
    println!("Final Masked IP: {}", result.layer3);
    println!("Timestamp: {}", result.timestamp);

    println!("\n=== Network Encryption Simulation ===");
    println!("Packet routing through encrypted layers:");
    println!("[Network] --> Layer1: {}...", &result.layer1[..16]);
    println!("[Layer1] --> Layer2: {}...", &result.layer2[..16]);
    println!("[Layer2] --> Layer3: {}...", &result.layer3[..16]);
    println!("[Layer3] --> Internet (Fully Encrypted)");

    Ok(())
}
