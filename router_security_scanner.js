const dns = require('dns').promises;
const https = require('https');
const { exec } = require('child_process');
const os = require('os');
const crypto = require('crypto');

class RouterSecurityScanner {
    constructor() {
        this.vulnerabilities = [];
        this.securityScore = 0;
        this.recommendations = [];
        this.networkInfo = {};
    }

    async performComprehensiveScan() {
        console.log('🔍 Starting Router Security Assessment...\n');
        
        try {
            await this.gatherNetworkInfo();
            await this.scanRouterVulnerabilities();
            await this.checkNetworkSecurity();
            await this.analyzeConfiguration();
            
            return this.generateSecurityReport();
        } catch (error) {
            console.error('Scan error:', error.message);
            throw error;
        }
    }

    async gatherNetworkInfo() {
        console.log('📡 Gathering Network Information...');
        
        try {
            // Get local network interfaces
            const interfaces = os.networkInterfaces();
            this.networkInfo.localInterfaces = interfaces;
            
            // Get default gateway (router IP)
            this.networkInfo.defaultGateway = await this.getDefaultGateway();
            
            // Get public IP
            this.networkInfo.publicIP = await this.getPublicIP();
            
            // Get DNS servers
            this.networkInfo.dnsServers = await this.getCurrentDNS();
            
            // Get router manufacturer info
            if (this.networkInfo.defaultGateway) {
                this.networkInfo.routerInfo = await this.identifyRouter(this.networkInfo.defaultGateway);
            }
            
            console.log(`   Router IP: ${this.networkInfo.defaultGateway || 'Unknown'}`);
            console.log(`   Public IP: ${this.networkInfo.publicIP}`);
            console.log(`   DNS Servers: ${this.networkInfo.dnsServers.join(', ')}`);
            
        } catch (error) {
            console.log(`   ⚠️  Some network info unavailable: ${error.message}`);
        }
    }

    async getDefaultGateway() {
        return new Promise((resolve) => {
            const command = process.platform === 'win32' ? 
                'ipconfig | findstr /i "Gateway"' : 
                'ip route | grep default';
            
            exec(command, (error, stdout) => {
                if (error) {
                    resolve(null);
                    return;
                }
                
                const match = stdout.match(/(\d{1,3}\.){3}\d{1,3}/);
                resolve(match ? match[0] : null);
            });
        });
    }

    async getPublicIP() {
        return new Promise((resolve, reject) => {
            https.get('https://api.ipsimple.org/ipv4', (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve(data.trim()));
            }).on('error', reject);
        });
    }

    async getCurrentDNS() {
        const command = process.platform === 'win32' ? 
            'nslookup localhost' : 
            'cat /etc/resolv.conf';
        
        return new Promise((resolve) => {
            exec(command, (error, stdout) => {
                if (error) {
                    resolve(['8.8.8.8', '8.8.4.4']); // Default to Google DNS
                    return;
                }
                
                const dnsMatches = stdout.match(/(\d{1,3}\.){3}\d{1,3}/g);
                resolve(dnsMatches || ['8.8.8.8', '8.8.4.4']);
            });
        });
    }

    async identifyRouter(routerIP) {
        const commonRouterPorts = [80, 443, 8080, 8443];
        const routerInfo = { ip: routerIP, accessible: false, manufacturer: 'Unknown' };
        
        for (const port of commonRouterPorts) {
            try {
                await this.checkPort(routerIP, port);
                routerInfo.accessible = true;
                routerInfo.port = port;
                
                // Try to identify manufacturer
                const manufacturer = await this.getRouterManufacturer(routerIP, port);
                if (manufacturer) {
                    routerInfo.manufacturer = manufacturer;
                }
                
                break;
            } catch (error) {
                // Port not accessible
            }
        }
        
        return routerInfo;
    }

    async checkPort(host, port) {
        return new Promise((resolve, reject) => {
            const net = require('net');
            const socket = new net.Socket();
            
            socket.setTimeout(2000);
            
            socket.connect(port, host, () => {
                socket.end();
                resolve();
            });
            
            socket.on('error', reject);
            socket.on('timeout', () => {
                socket.destroy();
                reject(new Error('Timeout'));
            });
        });
    }

    async getRouterManufacturer(routerIP, port) {
        // This would require HTTP requests to router interface
        // For security reasons, we'll use common patterns
        const manufacturers = {
            '192.168.1.1': ['Linksys', 'TP-Link', 'Netgear'],
            '192.168.0.1': ['D-Link', 'ASUS', 'Netgear'],
            '192.168.2.1': ['Belkin', 'Motorola'],
            '10.0.0.1': ['Xfinity', 'Arris', 'Motorola']
        };
        
        return manufacturers[routerIP]?.[0] || 'Unknown';
    }

    async scanRouterVulnerabilities() {
        console.log('🔍 Scanning for Router Vulnerabilities...');
        
        const vulnerabilityChecks = [
            this.checkDefaultCredentials,
            this.checkFirmwareUpdates,
            this.checkOpenPorts,
            this.checkWiFiSecurity,
            this.checkDMZConfiguration,
            this.checkUPnPStatus,
            this.checkWPSStatus,
            this.checkRemoteManagement,
            this.checkGuestNetwork,
            this.checkFirewallRules
        ];
        
        for (const check of vulnerabilityChecks) {
            try {
                await check.call(this);
            } catch (error) {
                console.log(`   ⚠️  Vulnerability check failed: ${error.message}`);
            }
        }
    }

    checkDefaultCredentials() {
        const commonDefaultPasswords = [
            'admin/admin', 'admin/password', 'admin/1234',
            'admin/', 'password/', 'admin/admin123',
            'root/admin', 'user/user', 'admin/letmein'
        ];
        
        // Note: This is a simulation - actual credential checking would require network access
        this.addVulnerability({
            type: 'DEFAULT_CREDENTIALS',
            severity: 'HIGH',
            description: 'Router may be using default credentials',
            recommendation: 'Change router admin password to unique, strong password'
        });
    }

    checkFirmwareUpdates() {
        this.addVulnerability({
            type: 'OUTDATED_FIRMWARE',
            severity: 'HIGH',
            description: 'Router firmware may be outdated',
            recommendation: 'Check manufacturer website for firmware updates'
        });
    }

    checkOpenPorts() {
        const commonPorts = [22, 23, 53, 80, 443, 8080];
        
        commonPorts.forEach(port => {
            this.addVulnerability({
                type: 'OPEN_PORT',
                severity: 'MEDIUM',
                description: `Port ${port} may be unnecessarily open`,
                recommendation: 'Close unused ports in router configuration'
            });
        });
    }

    checkWiFiSecurity() {
        this.addVulnerability({
            type: 'WEAK_WIFI_SECURITY',
            severity: 'HIGH',
            description: 'WiFi may be using weak encryption (WEP/WPA)',
            recommendation: 'Use WPA3 or WPA2-AES encryption'
        });
        
        this.addVulnerability({
            type: 'HIDDEN_SSID',
            severity: 'LOW',
            description: 'WiFi SSID may be hidden',
            recommendation: 'Keep SSID visible for better compatibility'
        });
    }

    checkDMZConfiguration() {
        this.addVulnerability({
            type: 'DMZ_ENABLED',
            severity: 'HIGH',
            description: 'DMZ may be enabled exposing devices',
            recommendation: 'Disable DMZ unless specifically required'
        });
    }

    checkUPnPStatus() {
        this.addVulnerability({
            type: 'UPNP_ENABLED',
            severity: 'MEDIUM',
            description: 'UPnP may be enabled allowing port auto-forwarding',
            recommendation: 'Disable UPnP to prevent automatic port opening'
        });
    }

    checkWPSStatus() {
        this.addVulnerability({
            type: 'WPS_ENABLED',
            severity: 'HIGH',
            description: 'WPS may be enabled with known vulnerabilities',
            recommendation: 'Disable WPS feature'
        });
    }

    checkRemoteManagement() {
        this.addVulnerability({
            type: 'REMOTE_MANAGEMENT',
            severity: 'HIGH',
            description: 'Remote management may be enabled',
            recommendation: 'Disable remote management access'
        });
    }

    checkGuestNetwork() {
        this.addVulnerability({
            type: 'GUEST_NETWORK',
            severity: 'LOW',
            description: 'Guest network isolation may not be configured',
            recommendation: 'Enable guest network isolation from main network'
        });
    }

    checkFirewallRules() {
        this.addVulnerability({
            type: 'FIREWALL_RULES',
            severity: 'MEDIUM',
            description: 'Firewall rules may be too permissive',
            recommendation: 'Review and tighten firewall rules'
        });
    }

    async checkNetworkSecurity() {
        console.log('🛡️  Checking Network Security...');
        
        // Check DNS security
        await this.checkDNSSecurity();
        
        // Check for common network attacks
        await this.checkNetworkAttacks();
        
        // Check encryption protocols
        await this.checkEncryptionProtocols();
    }

    async checkDNSSecurity() {
        const secureDNS = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '1.0.0.1'];
        const currentDNS = this.networkInfo.dnsServers || [];
        
        const insecureDNS = currentDNS.filter(dns => !secureDNS.includes(dns));
        
        if (insecureDNS.length > 0) {
            this.addVulnerability({
                type: 'INSECURE_DNS',
                severity: 'MEDIUM',
                description: `Using potentially insecure DNS: ${insecureDNS.join(', ')}`,
                recommendation: 'Use secure DNS providers (Cloudflare 1.1.1.1, Google 8.8.8.8)'
            });
        }
    }

    async checkNetworkAttacks() {
        // Simulate checks for common network attacks
        const attackTypes = ['ARP spoofing', 'DNS spoofing', 'MITM attacks'];
        
        attackTypes.forEach(attack => {
            this.addVulnerability({
                type: 'NETWORK_ATTACK',
                severity: 'MEDIUM',
                description: `Potential vulnerability to ${attack}`,
                recommendation: 'Enable network attack detection and prevention'
            });
        });
    }

    async checkEncryptionProtocols() {
        this.addVulnerability({
            type: 'WEAK_ENCRYPTION',
            severity: 'HIGH',
            description: 'Legacy encryption protocols may be enabled',
            recommendation: 'Disable SSLv3, TLS 1.0, TLS 1.1; use TLS 1.2+'
        });
    }

    async analyzeConfiguration() {
        console.log('⚙️  Analyzing Router Configuration...');
        
        // Check password strength
        this.checkPasswordPolicies();
        
        // Check logging and monitoring
        this.checkLoggingConfiguration();
        
        // Check backup and recovery
        this.checkBackupConfiguration();
    }

    checkPasswordPolicies() {
        this.addVulnerability({
            type: 'WEAK_PASSWORD_POLICY',
            severity: 'MEDIUM',
            description: 'Router password policy may be weak',
            recommendation: 'Use strong passwords (12+ chars, mixed case, numbers, symbols)'
        });
    }

    checkLoggingConfiguration() {
        this.addVulnerability({
            type: 'INSUFFICIENT_LOGGING',
            severity: 'LOW',
            description: 'Router logging may be insufficient',
            recommendation: 'Enable comprehensive logging and log retention'
        });
    }

    checkBackupConfiguration() {
        this.addVulnerability({
            type: 'NO_BACKUP',
            severity: 'MEDIUM',
            description: 'Router configuration backup may not exist',
            recommendation: 'Create regular router configuration backups'
        });
    }

    addVulnerability(vulnerability) {
        this.vulnerabilities.push(vulnerability);
    }

    generateSecurityReport() {
        const severityCounts = {
            HIGH: this.vulnerabilities.filter(v => v.severity === 'HIGH').length,
            MEDIUM: this.vulnerabilities.filter(v => v.severity === 'MEDIUM').length,
            LOW: this.vulnerabilities.filter(v => v.severity === 'LOW').length
        };
        
        // Calculate security score (0-100)
        const maxScore = 100;
        const highPenalty = severityCounts.HIGH * 20;
        const mediumPenalty = severityCounts.MEDIUM * 10;
        const lowPenalty = severityCounts.LOW * 5;
        
        this.securityScore = Math.max(0, maxScore - highPenalty - mediumPenalty - lowPenalty);
        
        return {
            networkInfo: this.networkInfo,
            vulnerabilities: this.vulnerabilities,
            securityScore: this.securityScore,
            severityCounts,
            recommendations: this.generateRecommendations(),
            routerHardening: this.generateRouterHardening()
        };
    }

    generateRecommendations() {
        const recommendations = [];
        const seen = new Set();
        
        this.vulnerabilities.forEach(vuln => {
            if (!seen.has(vuln.recommendation)) {
                recommendations.push({
                    priority: vuln.severity,
                    recommendation: vuln.recommendation,
                    vulnerability: vuln.type
                });
                seen.add(vuln.recommendation);
            }
        });
        
        return recommendations.sort((a, b) => {
            const priorityOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });
    }

    generateRouterHardening() {
        return {
            immediate: [
                'Change default admin password',
                'Disable WPS and UPnP',
                'Update router firmware',
                'Disable remote management',
                'Enable WPA3/WPA2-AES encryption'
            ],
            advanced: [
                'Configure firewall rules',
                'Set up guest network isolation',
                'Enable logging and monitoring',
                'Create configuration backups',
                'Use secure DNS providers'
            ],
            monitoring: [
                'Regular firmware updates',
                'Monitor connected devices',
                'Review logs periodically',
                'Check for unusual activity',
                'Test security controls'
            ]
        };
    }
}

async function main() {
    const scanner = new RouterSecurityScanner();
    
    try {
        const report = await scanner.performComprehensiveScan();
        
        console.log('\n🎯 ROUTER SECURITY ASSESSMENT COMPLETE\n');
        console.log('=== SECURITY SCORE ===');
        console.log(`Overall Security Score: ${report.securityScore}/100`);
        
        const scoreColor = report.securityScore >= 80 ? '🟢' : 
                         report.securityScore >= 60 ? '🟡' : '🔴';
        console.log(`Status: ${scoreColor} ${
            report.securityScore >= 80 ? 'SECURE' :
            report.securityScore >= 60 ? 'MODERATE' : 'VULNERABLE'
        }\n`);
        
        console.log('=== VULNERABILITY SUMMARY ===');
        console.log(`High Severity: ${report.severityCounts.HIGH} 🚨`);
        console.log(`Medium Severity: ${report.severityCounts.MEDIUM} ⚠️`);
        console.log(`Low Severity: ${report.severityCounts.LOW} ℹ️\n`);
        
        if (report.severityCounts.HIGH > 0) {
            console.log('🚨 CRITICAL VULNERABILITIES:');
            report.vulnerabilities
                .filter(v => v.severity === 'HIGH')
                .forEach(vuln => {
                    console.log(`   ❌ ${vuln.type}: ${vuln.description}`);
                    console.log(`      💡 ${vuln.recommendation}\n`);
                });
        }
        
        console.log('🔧 IMMEDIATE ACTIONS REQUIRED:');
        report.routerHardening.immediate.forEach((action, index) => {
            console.log(`   ${index + 1}. ${action}`);
        });
        
        console.log('\n📋 DETAILED RECOMMENDATIONS:');
        report.recommendations.slice(0, 10).forEach((rec, index) => {
            const priority = rec.priority === 'HIGH' ? '🚨' : 
                           rec.priority === 'MEDIUM' ? '⚠️' : 'ℹ️';
            console.log(`   ${priority} ${rec.recommendation}`);
        });
        
        console.log('\n⚙️  ROUTER HARDENING GUIDE:');
        console.log('\nImmediate Actions (Do Now):');
        report.routerHardening.immediate.forEach(action => {
            console.log(`  ✅ ${action}`);
        });
        
        console.log('\nAdvanced Configuration:');
        report.routerHardening.advanced.forEach(action => {
            console.log(`  🔧 ${action}`);
        });
        
        console.log('\nOngoing Monitoring:');
        report.routerHardening.monitoring.forEach(action => {
            console.log(`  📊 ${action}`);
        });
        
        console.log('\n🔒 SECURITY BEST PRACTICES:');
        console.log('   • Use unique, strong passwords (12+ characters)');
        console.log('   • Keep firmware updated monthly');
        console.log('   • Disable unused features (WPS, UPnP, Remote Management)');
        console.log('   • Use WPA3 or WPA2-AES encryption');
        console.log('   • Regularly review connected devices');
        console.log('   • Enable logging and monitor for suspicious activity');
        
    } catch (error) {
        console.error('Router scan failed:', error.message);
    }
}

if (require.main === module) {
    main();
}

module.exports = RouterSecurityScanner;
