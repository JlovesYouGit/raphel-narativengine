#!/bin/bash

echo "=== 3-Layer SHA-256 IP Masking System - Multi-Language Demo ==="
echo

# Function to run Node.js version
run_nodejs() {
    echo "--- Node.js Implementation ---"
    if command -v node &> /dev/null; then
        echo "Running Node.js IP Masker..."
        node ip_masker_node.js
        echo
    else
        echo "Node.js not found. Skipping..."
    fi
}

# Function to run Go version
run_go() {
    echo "--- Go Implementation ---"
    if command -v go &> /dev/null; then
        echo "Compiling and running Go IP Masker..."
        go run ip_masker_go.go
        echo
    else
        echo "Go not found. Skipping..."
    fi
}

# Function to run Rust version
run_rust() {
    echo "--- Rust Implementation ---"
    if command -v cargo &> /dev/null; then
        echo "Compiling and running Rust IP Masker..."
        # Add dependencies to Cargo.toml if needed
        if [ ! -f Cargo.toml ]; then
            echo '[dependencies]
tokio = { version = "1.0", features = ["full"] }
reqwest = { version = "0.11", features = ["json"] }
sha2 = "0.10"
hex = "0.4"' > Cargo.toml
        fi
        cargo run --bin ip_masker_rust 2>/dev/null || echo "Rust compilation failed - dependencies may need to be installed"
        echo
    else
        echo "Rust/Cargo not found. Skipping..."
    fi
}

# Function to run Java version
run_java() {
    echo "--- Java Implementation ---"
    if command -v java &> /dev/null; then
        echo "Compiling and running Java IP Masker..."
        javac IPMasker.java
        java IPMasker
        echo
    else
        echo "Java not found. Skipping..."
    fi
}

# Function to run C# version
run_csharp() {
    echo "--- C# Implementation ---"
    if command -v dotnet &> /dev/null; then
        echo "Running C# IP Masker..."
        dotnet run --project . 2>/dev/null || echo "C# project setup required"
        echo
    else
        echo ".NET Core not found. Skipping..."
    fi
}

# Main execution
echo "Checking available language runtimes..."
echo

run_nodejs
run_go
run_rust
run_java
run_csharp

echo "=== Demo Complete ==="
echo "All implementations use 3-layer SHA-256 encryption:"
echo "Layer 1: IP + Salt1 -> SHA256"
echo "Layer 2: Layer1 + Salt2 -> SHA256" 
echo "Layer 3: Layer2 + Salt3 -> SHA256"
echo
echo "This creates a cascading encryption effect where each layer"
echo "depends on the previous one, making it computationally infeasible"
echo "to reverse-engineer the original IP address."
