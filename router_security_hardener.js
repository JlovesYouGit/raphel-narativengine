const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class RouterSecurityHardener {
    constructor() {
        this.securityConfig = {
            // Network security
            firewall: {
                enabled: true,
                defaultPolicy: 'DENY',
                allowedPorts: [443, 80], // HTTPS, HTTP only
                blockedPorts: [23, 135, 139, 445, 3389], // Telnet, SMB, RDP
                inboundRules: [],
                outboundRules: []
            },
            
            // WiFi security
            wifi: {
                encryption: 'WPA3', // Best practice
                passwordLength: 12,
                passwordComplexity: true,
                ssidBroadcast: true, // Hidden SSIDs are less secure
                wpsEnabled: false,
                guestNetwork: {
                    enabled: false,
                    isolation: true,
                    bandwidthLimit: '50%'
                }
            },
            
            // Authentication security
            authentication: {
                adminPassword: {
                    minLength: 16,
                    requireUppercase: true,
                    requireLowercase: true,
                    requireNumbers: true,
                    requireSymbols: true,
                    changeInterval: 90 // days
                },
                sessionTimeout: 300, // 5 minutes
                maxAttempts: 3,
                lockoutDuration: 900, // 15 minutes
                twoFactorAuth: false // Future enhancement
            },
            
            // Remote management
            remoteManagement: {
                enabled: false,
                allowedIPs: [], // Whitelist only
                port: 443,
                certificateRequired: true
            },
            
            // Network services
            services: {
                upnp: false,
                dmz: false,
                natLoopback: false,
                dnsHijacking: false,
                ipv6: true
            },
            
            // Logging and monitoring
            logging: {
                enabled: true,
                level: 'INFO',
                retention: 30, // days
                logSize: 100, // MB
                remoteLogging: false,
                alertThresholds: {
                    failedLogins: 5,
                    bandwidthUsage: 90, // percent
                    newDevices: 10 // per hour
                }
            },
            
            // DNS security
            dns: {
                provider: 'CLOUDFLARE', // 1.1.1.1
                dnssec: true,
                overHttps: true,
                overTls: true,
                blocking: {
                    malware: true,
                    phishing: true,
                    ads: false
                }
            }
        };
    }

    generateSecureConfiguration() {
        console.log('🔧 Generating Secure Router Configuration...\n');
        
        const config = {
            timestamp: new Date().toISOString(),
            version: '1.0',
            security: this.securityConfig,
            generatedPasswords: this.generateSecurePasswords(),
            networkSegments: this.createNetworkSegments(),
            firewallRules: this.generateFirewallRules(),
            monitoring: this.setupMonitoring()
        };
        
        return config;
    }

    generateSecurePasswords() {
        const passwords = {
            admin: this.generateStrongPassword(16),
            wifi: this.generateStrongPassword(12),
            guest: this.generateStrongPassword(10)
        };
        
        console.log('🔐 Generated Secure Passwords:');
        console.log(`   Admin Password: ${passwords.admin}`);
        console.log(`   WiFi Password: ${passwords.wifi}`);
        console.log(`   Guest Password: ${passwords.guest}\n`);
        
        return passwords;
    }

    generateStrongPassword(length) {
        const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
        let password = '';
        
        // Ensure at least one of each required character type
        password += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[Math.floor(Math.random() * 26)];
        password += 'abcdefghijklmnopqrstuvwxyz'[Math.floor(Math.random() * 26)];
        password += '0123456789'[Math.floor(Math.random() * 10)];
        password += '!@#$%^&*()_+-=[]{}|;:,.<>?'[Math.floor(Math.random() * 24)];
        
        // Fill the rest
        for (let i = 4; i < length; i++) {
            password += charset[Math.floor(Math.random() * charset.length)];
        }
        
        // Shuffle the password
        return password.split('').sort(() => Math.random() - 0.5).join('');
    }

    createNetworkSegments() {
        return {
            trusted: {
                name: 'Trusted Devices',
                subnet: '192.168.1.0/24',
                devices: ['Computers', 'Smartphones', 'Tablets'],
                access: 'Full',
                isolation: false
            },
            iot: {
                name: 'IoT Devices',
                subnet: '192.168.10.0/24',
                devices: ['Smart TVs', 'Cameras', 'Speakers', 'Sensors'],
                access: 'Limited',
                isolation: true,
                blockedServices: ['internet-update', 'manufacturer-telemetry']
            },
            guest: {
                name: 'Guest Network',
                subnet: '192.168.100.0/24',
                devices: ['Visitor Devices'],
                access: 'Internet Only',
                isolation: true,
                bandwidthLimit: '50Mbps'
            },
            dmz: {
                name: 'DMZ Zone',
                subnet: '192.168.200.0/24',
                devices: ['Public Servers'],
                access: 'Specific Ports Only',
                isolation: true,
                inboundPorts: [80, 443]
            }
        };
    }

    generateFirewallRules() {
        return {
            inbound: [
                // Block all by default
                { action: 'DENY', source: 'any', destination: 'any', port: 'any', protocol: 'any' },
                
                // Allow established connections
                { action: 'ALLOW', source: 'any', destination: 'any', port: 'any', protocol: 'any', state: 'ESTABLISHED,RELATED' },
                
                // Allow DNS
                { action: 'ALLOW', source: 'any', destination: '1.1.1.1', port: '53', protocol: 'udp' },
                { action: 'ALLOW', source: 'any', destination: '8.8.8.8', port: '53', protocol: 'udp' },
                
                // Block dangerous ports
                { action: 'DENY', source: 'any', destination: 'any', port: '23', protocol: 'tcp', description: 'Block Telnet' },
                { action: 'DENY', source: 'any', destination: 'any', port: '135', protocol: 'tcp', description: 'Block RPC' },
                { action: 'DENY', source: 'any', destination: 'any', port: '139', protocol: 'tcp', description: 'Block NetBIOS' },
                { action: 'DENY', source: 'any', destination: 'any', port: '445', protocol: 'tcp', description: 'Block SMB' },
                { action: 'DENY', source: 'any', destination: 'any', port: '3389', protocol: 'tcp', description: 'Block RDP' }
            ],
            
            outbound: [
                // Allow most outbound traffic
                { action: 'ALLOW', source: 'any', destination: 'any', port: 'any', protocol: 'any' },
                
                // Block suspicious outbound
                { action: 'DENY', source: 'any', destination: 'any', port: '25', protocol: 'tcp', description: 'Block SMTP (spam)' },
                { action: 'DENY', source: 'iot', destination: 'any', port: 'any', protocol: 'any', description: 'Block IoT direct internet' }
            ],
            
            interSegment: [
                // Isolate network segments
                { action: 'DENY', source: 'guest', destination: 'trusted', port: 'any', protocol: 'any' },
                { action: 'DENY', source: 'guest', destination: 'iot', port: 'any', protocol: 'any' },
                { action: 'DENY', source: 'iot', destination: 'trusted', port: 'any', protocol: 'any' },
                { action: 'ALLOW', source: 'trusted', destination: 'iot', port: 'any', protocol: 'any' }
            ]
        };
    }

    setupMonitoring() {
        return {
            alerts: [
                {
                    name: 'Failed Login Attempts',
                    condition: 'failed_logins > 5',
                    action: 'block_ip_temporary',
                    duration: 300
                },
                {
                    name: 'New Device Connection',
                    condition: 'new_device_detected',
                    action: 'send_notification',
                    verification: 'required'
                },
                {
                    name: 'High Bandwidth Usage',
                    condition: 'bandwidth_usage > 90%',
                    action: 'throttle_bandwidth',
                    log_level: 'warning'
                },
                {
                    name: 'Port Scan Detected',
                    condition: 'port_scan_detected',
                    action: 'block_source_ip',
                    duration: 3600
                },
                {
                    name: 'Malware Traffic',
                    condition: 'malware_domain_accessed',
                    action: 'block_domain_and_alert',
                    quarantine: 'source_device'
                }
            ],
            
            logging: {
                events: [
                    'login_attempts',
                    'device_connections',
                    'firewall_blocks',
                    'bandwidth_usage',
                    'configuration_changes',
                    'firmware_updates'
                ],
                
                retention: {
                    logs: 30, // days
                    alerts: 90, // days
                    metrics: 365 // days
                }
            }
        };
    }

    createImplementationGuide() {
        return {
            step1: {
                title: 'Change Default Credentials',
                actions: [
                    'Log into router admin panel',
                    'Change admin password to generated strong password',
                    'Enable password complexity requirements',
                    'Set session timeout to 5 minutes'
                ],
                verification: 'Test login with new password only'
            },
            
            step2: {
                title: 'Configure WiFi Security',
                actions: [
                    'Set WiFi encryption to WPA3 or WPA2-AES',
                    'Change WiFi password to generated strong password',
                    'Disable WPS (Wi-Fi Protected Setup)',
                    'Enable SSID broadcast (hidden networks are less secure)',
                    'Consider creating guest network if needed'
                ],
                verification: 'Test WiFi connection with new password only'
            },
            
            step3: {
                title: 'Configure Firewall Rules',
                actions: [
                    'Enable router firewall',
                    'Set default policy to DENY',
                    'Block dangerous ports (23, 135, 139, 445, 3389)',
                    'Allow only necessary ports (80, 443)',
                    'Configure port forwarding only if required'
                ],
                verification: 'Test that blocked services are inaccessible'
            },
            
            step4: {
                title: 'Disable Dangerous Services',
                actions: [
                    'Disable UPnP (Universal Plug and Play)',
                    'Disable DMZ (Demilitarized Zone)',
                    'Disable remote management',
                    'Disable NAT loopback',
                    'Disable IPv6 if not used'
                ],
                verification: 'Confirm services are disabled in admin panel'
            },
            
            step5: {
                title: 'Configure DNS Security',
                actions: [
                    'Set DNS to 1.1.1.1 (Cloudflare) or 8.8.8.8 (Google)',
                    'Enable DNSSEC if available',
                    'Enable DNS over HTTPS/TLS if available',
                    'Consider enabling DNS filtering'
                ],
                verification: 'Check DNS settings and test resolution'
            },
            
            step6: {
                title: 'Update Firmware',
                actions: [
                    'Check current firmware version',
                    'Visit manufacturer website for latest version',
                    'Download and install firmware update',
                    'Verify router functionality after update'
                ],
                verification: 'Confirm firmware version is latest'
            },
            
            step7: {
                title: 'Enable Logging and Monitoring',
                actions: [
                    'Enable comprehensive logging',
                    'Set log retention to 30+ days',
                    'Configure email alerts for security events',
                    'Enable device connection logging',
                    'Set up bandwidth monitoring'
                ],
                verification: 'Check that logs are being generated'
            },
            
            step8: {
                title: 'Create Network Segments',
                actions: [
                    'Create separate VLAN for IoT devices',
                    'Configure guest network isolation',
                    'Set up DMZ for public servers if needed',
                    'Configure inter-segment firewall rules'
                ],
                verification: 'Test network isolation between segments'
            }
        };
    }

    generateConfigurationFiles() {
        const config = this.generateSecureConfiguration();
        const guide = this.createImplementationGuide();
        
        const files = {
            'router_security_config.json': JSON.stringify(config, null, 2),
            'implementation_guide.json': JSON.stringify(guide, null, 2),
            'firewall_rules.txt': this.formatFirewallRules(config.firewallRules),
            'security_checklist.md': this.generateSecurityChecklist(),
            'passwords.txt': this.generatePasswordFile(config.generatedPasswords)
        };
        
        return files;
    }

    formatFirewallRules(rules) {
        let output = '# Router Firewall Rules\n\n';
        
        output += '## Inbound Rules\n';
        rules.inbound.forEach((rule, index) => {
            output += `${index + 1}. ${rule.action} ${rule.source}:${rule.port} -> ${rule.destination} (${rule.protocol})`;
            if (rule.description) output += ` - ${rule.description}`;
            output += '\n';
        });
        
        output += '\n## Outbound Rules\n';
        rules.outbound.forEach((rule, index) => {
            output += `${index + 1}. ${rule.action} ${rule.source}:${rule.port} -> ${rule.destination} (${rule.protocol})`;
            if (rule.description) output += ` - ${rule.description}`;
            output += '\n';
        });
        
        return output;
    }

    generateSecurityChecklist() {
        return `# Router Security Hardening Checklist

## Immediate Actions (Do Now)
- [ ] Change default admin password
- [ ] Disable WPS and UPnP
- [ ] Update router firmware
- [ ] Disable remote management
- [ ] Enable WPA3/WPA2-AES encryption
- [ ] Set secure DNS (1.1.1.1 or 8.8.8.8)

## Advanced Configuration
- [ ] Configure firewall rules
- [ ] Set up network segmentation
- [ ] Enable logging and monitoring
- [ ] Create guest network isolation
- [ ] Configure intrusion detection
- [ ] Set up automatic backups

## Ongoing Maintenance
- [ ] Monthly firmware checks
- [ ] Quarterly password changes
- [ ] Regular log reviews
- [ ] Device inventory updates
- [ ] Security audit reviews

## Security Verification
- [ ] Test firewall rules
- [ ] Verify network isolation
- [ ] Confirm logging functionality
- [ ] Test alert notifications
- [ ] Validate backup restoration
`;
    }

    generatePasswordFile(passwords) {
        return `# Generated Secure Passwords
# Store this file securely and delete after use

Admin Password: ${passwords.admin}
WiFi Password: ${passwords.wifi}
Guest Password: ${passwords.guest}

Generated: ${new Date().toISOString()}
# Remember to change these passwords regularly
`;
    }

    async saveConfigurationFiles() {
        const files = this.generateConfigurationFiles();
        const savedFiles = [];
        
        for (const [filename, content] of Object.entries(files)) {
            const filepath = path.join(__dirname, filename);
            fs.writeFileSync(filepath, content);
            savedFiles.push(filepath);
        }
        
        return savedFiles;
    }
}

async function main() {
    console.log('🛡️  Router Security Hardening Tool\n');
    
    const hardener = new RouterSecurityHardener();
    
    try {
        // Generate secure configuration
        const config = hardener.generateSecureConfiguration();
        
        console.log('📊 Security Configuration Summary:');
        console.log(`   Firewall: ${config.security.firewall.enabled ? 'Enabled' : 'Disabled'}`);
        console.log(`   WiFi Encryption: ${config.security.wifi.encryption}`);
        console.log(`   UPnP: ${config.security.services.upnp ? 'Enabled' : 'Disabled'}`);
        console.log(`   Remote Management: ${config.security.remoteManagement.enabled ? 'Enabled' : 'Disabled'}`);
        console.log(`   DNS Provider: ${config.security.dns.provider}\n`);
        
        // Display implementation guide
        const guide = hardener.createImplementationGuide();
        console.log('🔧 Implementation Steps:');
        Object.keys(guide).forEach((step, index) => {
            console.log(`\n   Step ${index + 1}: ${guide[step].title}`);
            guide[step].actions.forEach(action => {
                console.log(`     • ${action}`);
            });
        });
        
        // Save configuration files
        const savedFiles = await hardener.saveConfigurationFiles();
        console.log('\n📁 Configuration Files Created:');
        savedFiles.forEach(file => {
            console.log(`   📄 ${file}`);
        });
        
        console.log('\n🔒 SECURITY HARDENING COMPLETE!');
        console.log('\nNext Steps:');
        console.log('1. Follow the implementation guide step by step');
        console.log('2. Use the generated passwords for your router');
        console.log('3. Apply the firewall rules in router admin panel');
        console.log('4. Test all security configurations');
        console.log('5. Store passwords securely and delete the password file');
        
        console.log('\n⚠️  IMPORTANT:');
        console.log('• Apply these changes during a maintenance window');
        console.log('• Have physical access to router before making changes');
        console.log('• Test connectivity after each major change');
        console.log('• Keep a backup of original settings');
        
    } catch (error) {
        console.error('Error generating configuration:', error.message);
    }
}

if (require.main === module) {
    main();
}

module.exports = RouterSecurityHardener;
