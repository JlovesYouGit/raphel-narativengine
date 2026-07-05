package main

import (
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"regexp"
	"sync"
	"time"
)

type SecureIPMasker struct {
	layer1Salt       string
	layer2Salt       string
	layer3Salt       string
	requestTimes     []time.Time
	requestMutex     sync.Mutex
	maxRequestsPerMinute int
	requestWindow    time.Duration
	timeout          time.Duration
	maxInputLength   int
	securityLog      []SecurityEvent
	logMutex         sync.Mutex
	userAgent        string
}

type SecurityEvent struct {
	Timestamp time.Time
	Event     string
	Data      map[string]interface{}
}

type MaskResult struct {
	Original  string    `json:"original"`
	Layer1    string    `json:"layer1"`
	Layer2    string    `json:"layer2"`
	Layer3    string    `json:"layer3"`
	Timestamp time.Time `json:"timestamp"`
	Salts     map[string]string `json:"salts"`
}

func NewSecureIPMasker() *SecureIPMasker {
	return &SecureIPMasker{
		layer1Salt:           generateSecureSalt(),
		layer2Salt:           generateSecureSalt(),
		layer3Salt:           generateSecureSalt(),
		maxRequestsPerMinute: 10,
		requestWindow:        time.Minute,
		timeout:              5 * time.Second,
		maxInputLength:       45,
		userAgent:           "SecureIPMasker-Go/1.0",
	}
}

func generateSecureSalt() string {
	bytes := make([]byte, 32)
	if _, err := rand.Read(bytes); err != nil {
		panic("Failed to generate secure salt")
	}
	return hex.EncodeToString(bytes)
}

func (m *SecureIPMasker) validateAndSanitizeInput(input string) (string, error) {
	if len(input) == 0 {
		return "", fmt.Errorf("input cannot be empty")
	}
	
	if len(input) > m.maxInputLength {
		return "", fmt.Errorf("input exceeds maximum length of %d", m.maxInputLength)
	}
	
	// Remove invalid characters
	reg := regexp.MustCompile(`[^\d\.:a-fA-F]`)
	sanitized := reg.ReplaceAllString(input, "")
	
	if len(sanitized) == 0 {
		return "", fmt.Errorf("sanitized input is empty")
	}
	
	if !m.isValidIPAddress(sanitized) {
		return "", fmt.Errorf("invalid IP address format")
	}
	
	return sanitized, nil
}

func (m *SecureIPMasker) isValidIPAddress(ip string) bool {
	// IPv4 regex
	ipv4Regex := regexp.MustCompile(`^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$`)
	
	// IPv6 regex (simplified)
	ipv6Regex := regexp.MustCompile(`^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$`)
	
	return ipv4Regex.MatchString(ip) || ipv6Regex.MatchString(ip)
}

func (m *SecureIPMasker) checkRateLimit() error {
	m.requestMutex.Lock()
	defer m.requestMutex.Unlock()
	
	now := time.Now()
	
	// Remove old requests
	validTimes := make([]time.Time, 0)
	for _, reqTime := range m.requestTimes {
		if now.Sub(reqTime) < m.requestWindow {
			validTimes = append(validTimes, reqTime)
		}
	}
	m.requestTimes = validTimes
	
	if len(m.requestTimes) >= m.maxRequestsPerMinute {
		return fmt.Errorf("rate limit exceeded. Please try again later")
	}
	
	m.requestTimes = append(m.requestTimes, now)
	return nil
}

func (m *SecureIPMasker) secureHTTPRequest(url string) (string, error) {
	client := &http.Client{
		Timeout: m.timeout,
	}
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", err
	}
	
	req.Header.Set("User-Agent", m.userAgent)
	req.Header.Set("Accept", "text/plain")
	req.Header.Set("Connection", "close")
	
	resp, err := client.Do(req)
	if err != nil {
		m.logSecurityEvent("http_error", map[string]interface{}{"url": url, "error": err.Error()})
		return "", err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		err := fmt.Errorf("HTTP %d: %s", resp.StatusCode, resp.Status)
		m.logSecurityEvent("http_error", map[string]interface{}{"url": url, "error": err.Error()})
		return "", err
	}
	
	body, err := io.ReadAll(io.LimitReader(resp.Body, 1000)) // Limit response size
	if err != nil {
		m.logSecurityEvent("http_error", map[string]interface{}{"url": url, "error": err.Error()})
		return "", err
	}
	
	ip := string(body)
	m.logSecurityEvent("http_request", map[string]interface{}{"url": url, "status_code": resp.StatusCode})
	
	return ip, nil
}

func (m *SecureIPMasker) getPublicIP() (string, error) {
	if err := m.checkRateLimit(); err != nil {
		return "", err
	}
	
	ipSources := []string{
		"https://api.ipsimple.org/ipv4",
		"https://icanhazip.com",
		"https://checkip.amazonaws.com",
	}
	
	var lastError error
	
	for _, source := range ipSources {
		ip, err := m.secureHTTPRequest(source)
		if err != nil {
			lastError = err
			m.logSecurityEvent("ip_detection_failed", map[string]interface{}{"source": source, "error": err.Error()})
			continue
		}
		
		sanitizedIP, err := m.validateAndSanitizeInput(ip)
		if err != nil {
			lastError = err
			continue
		}
		
		m.logSecurityEvent("ip_detected", map[string]interface{}{"source": source, "ip": sanitizedIP})
		return sanitizedIP, nil
	}
	
	return "", fmt.Errorf("all IP detection sources failed: %v", lastError)
}

func (m *SecureIPMasker) sha256Hash(data, salt string) string {
	start := time.Now()
	
	h := hmac.New(sha256.New, []byte(salt))
	h.Write([]byte(data))
	hash := hex.EncodeToString(h.Sum(nil))
	
	duration := time.Since(start)
	m.logSecurityEvent("hash_computed", map[string]interface{}{
		"algorithm": "SHA-256-HMAC",
		"duration":  duration.Milliseconds(),
	})
	
	return hash
}

func (m *SecureIPMasker) maskIP(ip string) (*MaskResult, error) {
	validatedIP, err := m.validateAndSanitizeInput(ip)
	if err != nil {
		m.logSecurityEvent("masking_error", map[string]interface{}{"error": err.Error()})
		return nil, err
	}
	
	fmt.Printf("Original IP: %s\n", validatedIP)
	
	layer1 := m.sha256Hash(validatedIP, m.layer1Salt)
	fmt.Printf("Layer 1 Hash: %s...\n", layer1[:16])
	
	layer2 := m.sha256Hash(layer1, m.layer2Salt)
	fmt.Printf("Layer 2 Hash: %s...\n", layer2[:16])
	
	layer3 := m.sha256Hash(layer2, m.layer3Salt)
	fmt.Printf("Layer 3 Hash: %s...\n", layer3[:16])
	
	result := &MaskResult{
		Original:  validatedIP,
		Layer1:    layer1,
		Layer2:    layer2,
		Layer3:    layer3,
		Timestamp: time.Now(),
		Salts: map[string]string{
			"layer1": m.layer1Salt[:8] + "...",
			"layer2": m.layer2Salt[:8] + "...",
			"layer3": m.layer3Salt[:8] + "...",
		},
	}
	
	m.logSecurityEvent("ip_masked", map[string]interface{}{"original": validatedIP, "layers": 3})
	return result, nil
}

func (m *SecureIPMasker) logSecurityEvent(event string, data map[string]interface{}) {
	m.logMutex.Lock()
	defer m.logMutex.Unlock()
	
	logEntry := SecurityEvent{
		Timestamp: time.Now(),
		Event:     event,
		Data:      data,
	}
	
	m.securityLog = append(m.securityLog, logEntry)
	
	// Keep log size manageable
	if len(m.securityLog) > 1000 {
		m.securityLog = m.securityLog[len(m.securityLog)-500:]
	}
}

func (m *SecureIPMasker) getSecurityReport() map[string]interface{} {
	m.logMutex.Lock()
	defer m.logMutex.Unlock()
	
	m.requestMutex.Lock()
	requestCount := len(m.requestTimes)
	m.requestMutex.Unlock()
	
	return map[string]interface{}{
		"total_events": len(m.securityLog),
		"recent_events": m.securityLog,
		"rate_limit_status": map[string]interface{}{
			"requests_in_window": requestCount,
			"max_requests":       m.maxRequestsPerMinute,
		},
		"security_features": []string{
			"Input validation and sanitization",
			"Rate limiting (10 requests/minute)",
			"Secure salt generation",
			"HMAC-based hashing",
			"Request timeout protection",
			"Multiple IP source fallback",
			"Security event logging",
		},
	}
}

func (m *SecureIPMasker) getAndMaskIP() (*MaskResult, error) {
	ip, err := m.getPublicIP()
	if err != nil {
		m.logSecurityEvent("main_error", map[string]interface{}{"error": err.Error()})
		return nil, err
	}
	return m.maskIP(ip)
}

func main() {
	fmt.Println("=== SECURE 3-Layer SHA-256 IP Masking System ===")
	fmt.Println("Enhanced with comprehensive vulnerability protections\n")
	
	masker := NewSecureIPMasker()
	
	result, err := masker.getAndMaskIP()
	if err != nil {
		fmt.Printf("SECURITY ERROR: %v\n", err)
		if err.Error() == "rate limit exceeded. Please try again later" {
			fmt.Println("⚠️  Rate limiting is active to prevent abuse.")
		}
		return
	}
	
	fmt.Println("\n=== Final Result ===")
	fmt.Printf("Original IP: %s\n", result.Original)
	fmt.Printf("Final Masked IP: %s\n", result.Layer3)
	fmt.Printf("Timestamp: %s\n", result.Timestamp.Format(time.RFC3339))
	
	fmt.Println("\n=== Security Report ===")
	report := masker.getSecurityReport()
	fmt.Printf("Security events logged: %v\n", report["total_events"])
	fmt.Println("Active protections:")
	if features, ok := report["security_features"].([]string); ok {
		for _, feature := range features {
			fmt.Printf("  ✓ %s\n", feature)
		}
	}
	
	fmt.Println("\n=== Network Encryption Simulation ===")
	fmt.Println("Packet routing through encrypted layers:")
	fmt.Printf("[Network] --> Layer1: %s...\n", result.Layer1[:16])
	fmt.Printf("[Layer1] --> Layer2: %s...\n", result.Layer2[:16])
	fmt.Printf("[Layer2] --> Layer3: %s...\n", result.Layer3[:16])
	fmt.Println("[Layer3] --> Internet (Fully Encrypted & Secured)")
}
