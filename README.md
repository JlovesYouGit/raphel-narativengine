# 3-Layer SHA-256 IP Masking System

A multi-language implementation of a sophisticated IP masking system that uses three layers of SHA-256 encryption to completely obscure IP addresses for network security.

## Architecture Overview

The system implements a **3-layer cascading SHA-256 encryption** approach:

```
Original IP → Layer1 (SHA256 + Salt1) → Layer2 (SHA256 + Salt2) → Layer3 (SHA256 + Salt3)
```

Each layer uses:
- **SHA-256 cryptographic hash function**
- **Unique salt values** for each layer
- **CPU-intensive operations** for security
- **Cascading dependency** (each layer depends on the previous)

## Security Features

- **Multi-layer encryption**: 3 sequential SHA-256 hashes
- **Salt-based protection**: Unique salts prevent rainbow table attacks
- **Cascading security**: Each layer depends on the previous hash
- **Network-side masking**: Encrypts IP before network transmission
- **CPU-intensive design**: Requires significant computational power to reverse

## Implementations

### 🟢 Node.js (JavaScript)
```bash
node ip_masker_node.js
```

### 🔵 Go
```bash
go run ip_masker_go.go
```

### 🟠 Rust
```bash
cargo run --bin ip_masker_rust
```

### 🔴 Java
```bash
javac IPMasker.java && java IPMasker
```

### 🟣 C#
```bash
dotnet run
```

## Quick Demo

Run all implementations:
```bash
chmod +x run_all.sh
./run_all.sh
```

## Technical Details

### Layer 1 Encryption
- Input: Original IP + Salt1
- Output: First SHA-256 hash
- Purpose: Initial obfuscation

### Layer 2 Encryption  
- Input: Layer1 hash + Salt2
- Output: Second SHA-256 hash
- Purpose: Intermediate encryption

### Layer 3 Encryption
- Input: Layer2 hash + Salt3
- Output: Final SHA-256 hash
- Purpose: Final protection layer

### Network Flow
```
[Original IP] → [Layer1] → [Layer2] → [Layer3] → [Internet]
     ↓           ↓        ↓        ↓
  192.168.1.1  abc123... def456... ghi789...
```

## Security Benefits

1. **Irreversible**: SHA-256 is a one-way function
2. **Collision-resistant**: Extremely unlikely to produce same hash
3. **Quantum-resistant**: SHA-256 remains secure against quantum attacks
4. **Multi-layer protection**: Even if one layer is compromised, others remain secure

## Use Cases

- **Anonymous networking**: Hide real IP addresses
- **Security research**: Test network detection systems
- **Privacy protection**: Prevent IP tracking
- **Educational purposes**: Demonstrate cryptographic principles

⚠️ **Disclaimer**: This system is for educational and research purposes only. Always comply with applicable laws and regulations when using network security tools.
