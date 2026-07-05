package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"time"
)

type IPMasker struct {
	layer1Salt string
	layer2Salt string
	layer3Salt string
}

type MaskResult struct {
	Original  string    `json:"original"`
	Layer1    string    `json:"layer1"`
	Layer2    string    `json:"layer2"`
	Layer3    string    `json:"layer3"`
	Timestamp time.Time `json:"timestamp"`
}

func NewIPMasker() *IPMasker {
	return &IPMasker{
		layer1Salt: "first-layer-salt-2025",
		layer2Salt: "second-layer-salt-2025",
		layer3Salt: "third-layer-salt-2025",
	}
}

func (m *IPMasker) getPublicIP() (string, error) {
	resp, err := http.Get("https://api.ipsimple.org/ipv4")
	if err != nil {
		return "", fmt.Errorf("failed to get IP: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %v", err)
	}

	return string(body), nil
}

func (m *IPMasker) sha256Hash(data, salt string) string {
	input := data + salt
	hash := sha256.Sum256([]byte(input))
	return hex.EncodeToString(hash[:])
}

func (m *IPMasker) MaskIP(ip string) *MaskResult {
	fmt.Printf("Original IP: %s\n", ip)

	layer1 := m.sha256Hash(ip, m.layer1Salt)
	fmt.Printf("Layer 1 Hash: %s\n", layer1)

	layer2 := m.sha256Hash(layer1, m.layer2Salt)
	fmt.Printf("Layer 2 Hash: %s\n", layer2)

	layer3 := m.sha256Hash(layer2, m.layer3Salt)
	fmt.Printf("Layer 3 Hash: %s\n", layer3)

	return &MaskResult{
		Original:  ip,
		Layer1:    layer1,
		Layer2:    layer2,
		Layer3:    layer3,
		Timestamp: time.Now(),
	}
}

func (m *IPMasker) GetAndMaskIP() (*MaskResult, error) {
	ip, err := m.getPublicIP()
	if err != nil {
		return nil, err
	}
	return m.MaskIP(ip), nil
}

func main() {
	masker := NewIPMasker()

	fmt.Println("=== 3-Layer SHA-256 IP Masking System ===")
	fmt.Println("Detecting and masking current IP address...\n")

	result, err := masker.GetAndMaskIP()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	fmt.Println("\n=== Final Result ===")
	fmt.Printf("Original IP: %s\n", result.Original)
	fmt.Printf("Final Masked IP: %s\n", result.Layer3)
	fmt.Printf("Timestamp: %s\n", result.Timestamp.Format(time.RFC3339))

	fmt.Println("\n=== Network Encryption Simulation ===")
	fmt.Println("Packet routing through encrypted layers:")
	fmt.Printf("[Network] --> Layer1: %s...\n", result.Layer1[:16])
	fmt.Printf("[Layer1] --> Layer2: %s...\n", result.Layer2[:16])
	fmt.Printf("[Layer2] --> Layer3: %s...\n", result.Layer3[:16])
	fmt.Println("[Layer3] --> Internet (Fully Encrypted)")
}
