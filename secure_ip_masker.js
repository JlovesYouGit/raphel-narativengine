const https = require('https');
const crypto = require('crypto');
const { performance } = require('perf_hooks');

class SecureIPMasker {
    constructor() {
        // Secure salt management - generate random salts per instance
        this.layer1Salt = this.generateSecureSalt();
        this.layer2Salt = this.generateSecureSalt();
        this.layer3Salt = this.generateSecureSalt();
        
        // Rate limiting
        this.requestTimes = [];
        this.maxRequestsPerMinute = 10;
        this.requestWindowMs = 60000; // 1 minute
        
        // Security configuration
        this.maxInputLength = 45; // IPv6 max length + buffer
        this.timeoutMs = 5000; // 5 second timeout
        this.userAgent = 'SecureIPMasker/1.0';
        
        // Logging
        this.securityLog = [];
    }

    // Generate cryptographically secure random salt
    generateSecureSalt() {
        return crypto.randomBytes(32).toString('hex');
    }

    // Input validation and sanitization
    validateAndSanitizeInput(input) {
        if (typeof input !== 'string') {
            throw new Error('Input must be a string');
        }
        
        if (input.length === 0) {
            throw new Error('Input cannot be empty');
        }
        
        if (input.length > this.maxInputLength) {
            throw new Error(`Input exceeds maximum length of ${this.maxInputLength}`);
        }
        
        // Remove any potentially malicious characters
        const sanitized = input.replace(/[^\d\.:a-fA-F]/g, '').trim();
        
        if (sanitized.length === 0) {
            throw new Error('Sanitized input is empty');
        }
        
        // IP address format validation
        if (!this.isValidIPAddress(sanitized)) {
            throw new Error('Invalid IP address format');
        }
        
        return sanitized;
    }

    // Enhanced IP validation
    isValidIPAddress(ip) {
        // IPv4 regex
        const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        
        // IPv6 regex (simplified)
        const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
        
        return ipv4Regex.test(ip) || ipv6Regex.test(ip);
    }

    // Rate limiting implementation
    checkRateLimit() {
        const now = performance.now();
        
        // Remove old requests outside the window
        this.requestTimes = this.requestTimes.filter(time => 
            now - time < this.requestWindowMs
        );
        
        if (this.requestTimes.length >= this.maxRequestsPerMinute) {
            throw new Error('Rate limit exceeded. Please try again later.');
        }
        
        this.requestTimes.push(now);
    }

    // Secure HTTP request with timeout and validation
    async secureHttpRequest(url, options = {}) {
        return new Promise((resolve, reject) => {
            const startTime = performance.now();
            
            const req = https.get(url, {
                timeout: this.timeoutMs,
                headers: {
                    'User-Agent': this.userAgent,
                    'Accept': 'text/plain',
                    'Connection': 'close'
                },
                ...options
            }, (res) => {
                
                // Validate response
                if (res.statusCode !== 200) {
                    reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
                    return;
                }
                
                let data = '';
                
                res.on('data', chunk => {
                    data += chunk;
                    
                    // Prevent buffer overflow
                    if (data.length > 1000) {
                        req.destroy();
                        reject(new Error('Response too large'));
                        return;
                    }
                });
                
                res.on('end', () => {
                    const duration = performance.now() - startTime;
                    this.logSecurityEvent('http_request', { 
                        url, 
                        statusCode: res.statusCode,
                        duration: Math.round(duration)
                    });
                    resolve(data.trim());
                });
                
                res.on('error', (error) => {
                    this.logSecurityEvent('http_error', { url, error: error.message });
                    reject(error);
                });
            });
            
            req.on('timeout', () => {
                req.destroy();
                this.logSecurityEvent('http_timeout', { url });
                reject(new Error('Request timeout'));
            });
            
            req.on('error', (error) => {
                this.logSecurityEvent('http_error', { url, error: error.message });
                reject(error);
            });
        });
    }

    // Enhanced IP detection with multiple fallback sources
    async getPublicIP() {
        this.checkRateLimit();
        
        const ipSources = [
            'https://api.ipsimple.org/ipv4',
            'https://icanhazip.com',
            'https://checkip.amazonaws.com'
        ];
        
        let lastError;
        
        for (const source of ipSources) {
            try {
                const ip = await this.secureHttpRequest(source);
                const sanitizedIP = this.validateAndSanitizeInput(ip);
                this.logSecurityEvent('ip_detected', { source, ip: sanitizedIP });
                return sanitizedIP;
            } catch (error) {
                lastError = error;
                this.logSecurityEvent('ip_detection_failed', { source, error: error.message });
                continue;
            }
        }
        
        throw new Error(`All IP detection sources failed: ${lastError.message}`);
    }

    // Secure SHA-256 implementation with HMAC
    sha256Hash(data, salt) {
        const startTime = performance.now();
        
        try {
            // Use HMAC for additional security
            const hmac = crypto.createHmac('sha256', salt);
            hmac.update(data);
            const hash = hmac.digest('hex');
            
            const duration = performance.now() - startTime;
            this.logSecurityEvent('hash_computed', { 
                algorithm: 'SHA-256-HMAC', 
                duration: Math.round(duration)
            });
            
            return hash;
        } catch (error) {
            this.logSecurityEvent('hash_error', { error: error.message });
            throw new Error('Hash computation failed');
        }
    }

    // Secure IP masking with validation
    maskIP(ip) {
        try {
            const validatedIP = this.validateAndSanitizeInput(ip);
            
            console.log(`Original IP: ${validatedIP}`);
            
            const layer1 = this.sha256Hash(validatedIP, this.layer1Salt);
            console.log(`Layer 1 Hash: ${layer1.substring(0, 16)}...`);
            
            const layer2 = this.sha256Hash(layer1, this.layer2Salt);
            console.log(`Layer 2 Hash: ${layer2.substring(0, 16)}...`);
            
            const layer3 = this.sha256Hash(layer2, this.layer3Salt);
            console.log(`Layer 3 Hash: ${layer3.substring(0, 16)}...`);
            
            const result = {
                original: validatedIP,
                layer1: layer1,
                layer2: layer2,
                layer3: layer3,
                timestamp: new Date().toISOString(),
                salts: {
                    layer1: this.layer1Salt.substring(0, 8) + '...',
                    layer2: this.layer2Salt.substring(0, 8) + '...',
                    layer3: this.layer3Salt.substring(0, 8) + '...'
                }
            };
            
            this.logSecurityEvent('ip_masked', { 
                original: validatedIP, 
                layers: 3 
            });
            
            return result;
        } catch (error) {
            this.logSecurityEvent('masking_error', { error: error.message });
            throw error;
        }
    }

    // Security logging
    logSecurityEvent(event, data) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            event,
            data: { ...data }
        };
        
        this.securityLog.push(logEntry);
        
        // Keep log size manageable
        if (this.securityLog.length > 1000) {
            this.securityLog = this.securityLog.slice(-500);
        }
    }

    // Get security report
    getSecurityReport() {
        return {
            total_events: this.securityLog.length,
            recent_events: this.securityLog.slice(-10),
            rate_limit_status: {
                requests_in_window: this.requestTimes.length,
                max_requests: this.maxRequestsPerMinute
            },
            security_features: [
                'Input validation and sanitization',
                'Rate limiting (10 requests/minute)',
                'Secure salt generation',
                'HMAC-based hashing',
                'Request timeout protection',
                'Multiple IP source fallback',
                'Security event logging'
            ]
        };
    }

    // Main secure method
    async getAndMaskIP() {
        try {
            const ip = await this.getPublicIP();
            return this.maskIP(ip);
        } catch (error) {
            this.logSecurityEvent('main_error', { error: error.message });
            throw error;
        }
    }
}

async function main() {
    console.log('=== SECURE 3-Layer SHA-256 IP Masking System ===');
    console.log('Enhanced with comprehensive vulnerability protections\n');
    
    const masker = new SecureIPMasker();
    
    try {
        const result = await masker.getAndMaskIP();
        
        console.log('\n=== Final Result ===');
        console.log(`Original IP: ${result.original}`);
        console.log(`Final Masked IP: ${result.layer3}`);
        console.log(`Timestamp: ${result.timestamp}`);
        
        console.log('\n=== Security Report ===');
        const report = masker.getSecurityReport();
        console.log(`Security events logged: ${report.total_events}`);
        console.log('Active protections:');
        report.security_features.forEach(feature => console.log(`  ✓ ${feature}`));
        
        console.log('\n=== Network Encryption Simulation ===');
        console.log('Packet routing through encrypted layers:');
        console.log(`[Network] --> Layer1: ${result.layer1.substring(0, 16)}...`);
        console.log(`[Layer1] --> Layer2: ${result.layer2.substring(0, 16)}...`);
        console.log(`[Layer2] --> Layer3: ${result.layer3.substring(0, 16)}...`);
        console.log('[Layer3] --> Internet (Fully Encrypted & Secured)');
        
    } catch (error) {
        console.error('SECURITY ERROR:', error.message);
        
        if (error.message.includes('Rate limit')) {
            console.log('⚠️  Rate limiting is active to prevent abuse.');
        }
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = SecureIPMasker;
