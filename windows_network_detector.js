const { exec } = require('child_process');
const os = require('os');
const fs = require('fs');
const path = require('path');

class WindowsNetworkDetector {
    constructor() {
        this.networkInfo = {
            interfaces: [],
            ethernetPorts: [],
            securityIssues: [],
            recommendations: []
        };
    }

    async performNetworkAnalysis() {
        console.log('🔍 Analyzing Windows Network Configuration...\n');
        
        try {
            await this.getNetworkInterfaces();
            await this.analyzeEthernetPorts();
            await this.checkNetworkSecurity();
            await this.analyzeNetworkProtocols();
            await this.checkFirewallStatus();
            await this.scanForVulnerabilities();
            
            return this.generateNetworkReport();
        } catch (error) {
            console.error('Network analysis error:', error.message);
            throw error;
        }
    }

    async getNetworkInterfaces() {
        console.log('📡 Detecting Network Interfaces...');
        
        return new Promise((resolve, reject) => {
            exec('wmic path win32_networkadapter get Name,AdapterType,Speed,MACAddress,NetConnectionID /format:csv', (error, stdout, stderr) => {
                if (error) {
                    reject(error);
                    return;
                }
                
                const lines = stdout.split('\n').filter(line => line.trim() && !line.includes('Node,Name'));
                
                lines.forEach(line => {
                    const parts = line.split(',');
                    if (parts.length >= 5) {
                        const networkInterface = {
                            name: parts[1]?.trim() || 'Unknown',
                            type: parts[2]?.trim() || 'Unknown',
                            speed: parts[3]?.trim() || 'Unknown',
                            mac: parts[4]?.trim() || 'Unknown',
                            connectionId: parts[5]?.trim() || 'Unknown'
                        };
                        
                        this.networkInfo.interfaces.push(networkInterface);
                        
                        if (networkInterface.type.toLowerCase().includes('ethernet') || 
                            networkInterface.name.toLowerCase().includes('ethernet') ||
                            networkInterface.name.toLowerCase().includes('realtek') ||
                            networkInterface.name.toLowerCase().includes('intel')) {
                            this.networkInfo.ethernetPorts.push(networkInterface);
                        }
                    }
                });
                
                console.log(`   Found ${this.networkInfo.interfaces.length} network interfaces`);
                console.log(`   Found ${this.networkInfo.ethernetPorts.length} Ethernet ports\n`);
                resolve();
            });
        });
    }

    async analyzeEthernetPorts() {
        console.log('🔌 Analyzing Ethernet Port Security...');
        
        for (const port of this.networkInfo.ethernetPorts) {
            console.log(`   Analyzing: ${port.name}`);
            
            // Get detailed adapter information
            await this.getAdapterDetails(port);
            
            // Check for security issues
            this.checkEthernetSecurity(port);
        }
    }

    async getAdapterDetails(port) {
        return new Promise((resolve) => {
            exec(`wmic path win32_networkadapterconfiguration where "Description='${port.name}'" get IPAddress,IPSubnet,DefaultIPGateway,DNSServerSearchOrder,IPEnabled /format:csv`, (error, stdout) => {
                if (!error && stdout) {
                    const lines = stdout.split('\n').filter(line => line.trim() && !line.includes('Node,IPAddress'));
                    
                    if (lines.length > 0) {
                        const parts = lines[0].split(',');
                        port.ipAddress = parts[1]?.trim() || 'N/A';
                        port.subnet = parts[2]?.trim() || 'N/A';
                        port.gateway = parts[3]?.trim() || 'N/A';
                        port.dns = parts[4]?.trim() || 'N/A';
                        port.ipEnabled = parts[5]?.trim() || 'N/A';
                    }
                }
                resolve();
            });
        });
    }

    checkEthernetSecurity(port) {
        const issues = [];
        
        // Check if adapter is enabled
        if (port.ipEnabled === 'FALSE') {
            issues.push('Ethernet adapter is disabled');
        }
        
        // Check for DHCP vs Static IP
        if (port.ipAddress.includes('DHCP') || !port.ipAddress || port.ipAddress === 'N/A') {
            issues.push('Using DHCP - consider static IP for security');
        }
        
        // Check MAC address format
        if (port.mac && port.mac !== 'Unknown') {
            if (!/^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/.test(port.mac)) {
                issues.push('Invalid MAC address format detected');
            }
        }
        
        // Check for common security issues
        if (port.name.toLowerCase().includes('virtual') || port.name.toLowerCase().includes('hyper-v')) {
            issues.push('Virtual network adapter detected - ensure proper isolation');
        }
        
        if (issues.length > 0) {
            this.networkInfo.securityIssues.push({
                port: port.name,
                issues: issues,
                severity: 'MEDIUM'
            });
        }
    }

    async checkNetworkSecurity() {
        console.log('🛡️  Checking Network Security Settings...');
        
        await this.checkWindowsFirewall();
        await this.checkNetworkProtocols();
        await this.checkNetworkSharing();
        await this.checkNetworkDiscovery();
    }

    async checkWindowsFirewall() {
        return new Promise((resolve) => {
            exec('netsh advfirewall show allprofiles', (error, stdout) => {
                if (!error) {
                    const profiles = stdout.split('\n');
                    let firewallEnabled = true;
                    
                    profiles.forEach(line => {
                        if (line.includes('State') && line.includes('OFF')) {
                            firewallEnabled = false;
                        }
                    });
                    
                    if (!firewallEnabled) {
                        this.networkInfo.securityIssues.push({
                            type: 'FIREWALL_DISABLED',
                            description: 'Windows Firewall is disabled on one or more profiles',
                            severity: 'HIGH',
                            recommendation: 'Enable Windows Firewall for all network profiles'
                        });
                    }
                }
                resolve();
            });
        });
    }

    async checkNetworkProtocols() {
        console.log('📋 Checking Network Protocols...');
        
        return new Promise((resolve) => {
            exec('netsh interface ipv4 show interfaces', (error, stdout) => {
                if (!error) {
                    // Check for IPv6
                    exec('netsh interface ipv6 show interfaces', (ipv6Error, ipv6Stdout) => {
                        if (!ipv6Error && ipv6Stdout.includes('enabled')) {
                            this.networkInfo.securityIssues.push({
                                type: 'IPV6_ENABLED',
                                description: 'IPv6 is enabled - potential security risk if not used',
                                severity: 'LOW',
                                recommendation: 'Disable IPv6 if not actively used'
                            });
                        }
                        resolve();
                    });
                } else {
                    resolve();
                }
            });
        });
    }

    async checkNetworkSharing() {
        return new Promise((resolve) => {
            exec('net share', (error, stdout) => {
                if (!error && stdout) {
                    const shares = stdout.split('\n').filter(line => line.trim() && !line.includes('Share name'));
                    
                    if (shares.length > 2) { // More than default admin shares
                        this.networkInfo.securityIssues.push({
                            type: 'NETWORK_SHARES',
                            description: `Found ${shares.length} network shares - review for security`,
                            severity: 'MEDIUM',
                            recommendation: 'Review and secure network shares, disable unused shares'
                        });
                    }
                }
                resolve();
            });
        });
    }

    async checkNetworkDiscovery() {
        return new Promise((resolve) => {
            exec('netsh advfirewall firewall show rule name="Network Discovery"', (error, stdout) => {
                if (!error && stdout.includes('Enabled:                              Yes')) {
                    this.networkInfo.securityIssues.push({
                        type: 'NETWORK_DISCOVERY',
                        description: 'Network Discovery is enabled - exposes system information',
                        severity: 'MEDIUM',
                        recommendation: 'Disable Network Discovery on public networks'
                    });
                }
                resolve();
            });
        });
    }

    async analyzeNetworkProtocols() {
        console.log('🔍 Analyzing Network Protocols...');
        
        // Check for SMBv1 (WannaCry vulnerability)
        await this.checkSMBv1();
        
        // Check for LLMNR (NetBIOS)
        await this.checkLLMNR();
        
        // Check for SNMP
        await this.checkSNMP();
    }

    async checkSMBv1() {
        return new Promise((resolve) => {
            exec('Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol | Select-Object State', (error, stdout) => {
                if (!error && stdout.includes('Enabled')) {
                    this.networkInfo.securityIssues.push({
                        type: 'SMBV1_ENABLED',
                        description: 'SMBv1 is enabled - vulnerable to WannaCry and other attacks',
                        severity: 'HIGH',
                        recommendation: 'Disable SMBv1 immediately, use SMBv2/3'
                    });
                }
                resolve();
            });
        });
    }

    async checkLLMNR() {
        return new Promise((resolve) => {
            exec('reg query "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\DNSClient" /v EnableMulticast', (error, stdout) => {
                if (!error && stdout.includes('0x1')) {
                    this.networkInfo.securityIssues.push({
                        type: 'LLMNR_ENABLED',
                        description: 'LLMNR is enabled - vulnerable to spoofing attacks',
                        severity: 'MEDIUM',
                        recommendation: 'Disable LLMNR to prevent network spoofing'
                    });
                }
                resolve();
            });
        });
    }

    async checkSNMP() {
        return new Promise((resolve) => {
            exec('reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\SNMP\\Parameters" /v EnableAuthenticationTraps', (error, stdout) => {
                if (!error) {
                    this.networkInfo.securityIssues.push({
                        type: 'SNMP_ENABLED',
                        description: 'SNMP service detected - review security configuration',
                        severity: 'LOW',
                        recommendation: 'Secure SNMP with strong community strings or disable if unused'
                    });
                }
                resolve();
            });
        });
    }

    async checkFirewallStatus() {
        console.log('🔥 Analyzing Firewall Configuration...');
        
        // Check firewall rules
        await this.analyzeFirewallRules();
        
        // Check for open ports
        await this.scanOpenPorts();
    }

    async analyzeFirewallRules() {
        return new Promise((resolve) => {
            exec('netsh advfirewall firewall show rule name=all verbose', (error, stdout) => {
                if (!error) {
                    const rules = stdout.split('\n');
                    let riskyRules = 0;
                    
                    rules.forEach(line => {
                        if (line.includes('Enabled:                              Yes') && 
                            (line.includes('Any') || line.includes('All'))) {
                            riskyRules++;
                        }
                    });
                    
                    if (riskyRules > 5) {
                        this.networkInfo.securityIssues.push({
                            type: 'PERMISSIVE_FIREWALL',
                            description: `Found ${riskyRules} permissive firewall rules`,
                            severity: 'MEDIUM',
                            recommendation: 'Review and tighten firewall rules'
                        });
                    }
                }
                resolve();
            });
        });
    }

    async scanOpenPorts() {
        return new Promise((resolve) => {
            exec('netstat -an | findstr "LISTENING"', (error, stdout) => {
                if (!error) {
                    const listeningPorts = stdout.split('\n').filter(line => line.includes('LISTENING'));
                    const suspiciousPorts = [];
                    
                    listeningPorts.forEach(line => {
                        const portMatch = line.match(/:(\d+)\s/);
                        if (portMatch) {
                            const port = parseInt(portMatch[1]);
                            
                            // Check for suspicious ports
                            const suspicious = [23, 135, 139, 445, 3389, 1433, 3306];
                            if (suspicious.includes(port)) {
                                suspiciousPorts.push(port);
                            }
                        }
                    });
                    
                    if (suspiciousPorts.length > 0) {
                        this.networkInfo.securityIssues.push({
                            type: 'SUSPICIOUS_PORTS',
                            description: `Suspicious ports open: ${suspiciousPorts.join(', ')}`,
                            severity: 'HIGH',
                            recommendation: 'Close unnecessary ports and services'
                        });
                    }
                }
                resolve();
            });
        });
    }

    async scanForVulnerabilities() {
        console.log('🔍 Scanning for Network Vulnerabilities...');
        
        // Check for common Windows network vulnerabilities
        await this.checkWindowsUpdates();
        await this.checkAntivirusStatus();
        await this.checkNetworkServices();
        await this.checkPowerShellSecurity();
    }

    async checkWindowsUpdates() {
        return new Promise((resolve) => {
            exec('wmic qfe list', (error, stdout) => {
                if (!error) {
                    const updates = stdout.split('\n').filter(line => line.trim());
                    const latestUpdate = updates[updates.length - 2]; // Last actual update
                    
                    if (latestUpdate) {
                        const dateMatch = latestUpdate.match(/(\d{1,2}\/\d{1,2}\/\d{4})/);
                        if (dateMatch) {
                            const updateDate = new Date(dateMatch[1]);
                            const threeMonthsAgo = new Date();
                            threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
                            
                            if (updateDate < threeMonthsAgo) {
                                this.networkInfo.securityIssues.push({
                                    type: 'OUTDATED_UPDATES',
                                    description: `Last Windows update: ${dateMatch[1]} - system may be vulnerable`,
                                    severity: 'HIGH',
                                    recommendation: 'Install latest Windows updates immediately'
                                });
                            }
                        }
                    }
                }
                resolve();
            });
        });
    }

    async checkAntivirusStatus() {
        return new Promise((resolve) => {
            exec('wmic /namespace:\\\\root\\securitycenter2 path antivirusproduct get displayName,productState /format:csv', (error, stdout) => {
                if (!error && stdout) {
                    const lines = stdout.split('\n').filter(line => line.trim() && !line.includes('Node,displayName'));
                    
                    if (lines.length === 0) {
                        this.networkInfo.securityIssues.push({
                            type: 'NO_ANTIVIRUS',
                            description: 'No antivirus detected',
                            severity: 'HIGH',
                            recommendation: 'Install reputable antivirus software'
                        });
                    }
                }
                resolve();
            });
        });
    }

    async checkNetworkServices() {
        return new Promise((resolve) => {
            exec('sc query type= service state= running | findstr "SERVICE_NAME"', (error, stdout) => {
                if (!error) {
                    const services = stdout.split('\n').filter(line => line.includes('SERVICE_NAME'));
                    const riskyServices = [];
                    
                    services.forEach(line => {
                        const serviceName = line.split(':')[1]?.trim();
                        if (serviceName) {
                            const risky = ['telnet', 'ftp', 'tftp', 'snmp', 'wins'];
                            if (risky.some(risk => serviceName.toLowerCase().includes(risk))) {
                                riskyServices.push(serviceName);
                            }
                        }
                    });
                    
                    if (riskyServices.length > 0) {
                        this.networkInfo.securityIssues.push({
                            type: 'RISKY_SERVICES',
                            description: `Risky services running: ${riskyServices.join(', ')}`,
                            severity: 'HIGH',
                            recommendation: 'Disable unnecessary network services'
                        });
                    }
                }
                resolve();
            });
        });
    }

    async checkPowerShellSecurity() {
        return new Promise((resolve) => {
            exec('Get-ExecutionPolicy', (error, stdout) => {
                if (!error && stdout.includes('Unrestricted')) {
                    this.networkInfo.securityIssues.push({
                        type: 'POWERSHELL_UNRESTRICTED',
                        description: 'PowerShell execution policy is Unrestricted',
                        severity: 'MEDIUM',
                        recommendation: 'Set PowerShell execution policy to Restricted or AllSigned'
                    });
                }
                resolve();
            });
        });
    }

    generateNetworkReport() {
        const highSeverity = this.networkInfo.securityIssues.filter(i => i.severity === 'HIGH');
        const mediumSeverity = this.networkInfo.securityIssues.filter(i => i.severity === 'MEDIUM');
        const lowSeverity = this.networkInfo.securityIssues.filter(i => i.severity === 'LOW');
        
        // Calculate security score
        const maxScore = 100;
        const highPenalty = highSeverity.length * 20;
        const mediumPenalty = mediumSeverity.length * 10;
        const lowPenalty = lowSeverity.length * 5;
        
        const securityScore = Math.max(0, maxScore - highPenalty - mediumPenalty - lowPenalty);
        
        return {
            timestamp: new Date().toISOString(),
            networkInfo: this.networkInfo,
            securityScore,
            vulnerabilityCount: {
                total: this.networkInfo.securityIssues.length,
                high: highSeverity.length,
                medium: mediumSeverity.length,
                low: lowSeverity.length
            },
            recommendations: this.generateRecommendations(),
            ethernetAnalysis: this.analyzeEthernetSecurity()
        };
    }

    generateRecommendations() {
        const recommendations = [];
        const seen = new Set();
        
        this.networkInfo.securityIssues.forEach(issue => {
            if (!seen.has(issue.recommendation)) {
                recommendations.push({
                    priority: issue.severity,
                    action: issue.recommendation,
                    vulnerability: issue.type
                });
                seen.add(issue.recommendation);
            }
        });
        
        return recommendations.sort((a, b) => {
            const priorityOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });
    }

    analyzeEthernetSecurity() {
        const analysis = {
            totalPorts: this.networkInfo.ethernetPorts.length,
            enabledPorts: this.networkInfo.ethernetPorts.filter(p => p.ipEnabled === 'TRUE').length,
            securityIssues: [],
            recommendations: []
        };
        
        this.networkInfo.ethernetPorts.forEach(port => {
            if (port.ipEnabled === 'FALSE') {
                analysis.securityIssues.push(`${port.name} is disabled`);
            }
            
            if (port.speed && parseInt(port.speed) < 1000000000) { // Less than 1Gbps
                analysis.securityIssues.push(`${port.name} - slow connection detected (${port.speed} bps)`);
            }
        });
        
        analysis.recommendations = [
            'Enable only necessary network adapters',
            'Use static IP addresses for critical servers',
            'Configure VLANs for network segmentation',
            'Enable MAC address filtering where appropriate',
            'Monitor network adapter performance and errors'
        ];
        
        return analysis;
    }
}

async function main() {
    console.log('🖥️  Windows Network Security Analyzer\n');
    console.log('Analyzing Ethernet ports and network configuration...\n');
    
    const detector = new WindowsNetworkDetector();
    
    try {
        const report = await detector.performNetworkAnalysis();
        
        console.log('\n🎯 NETWORK SECURITY ANALYSIS COMPLETE\n');
        console.log('=== SECURITY SCORE ===');
        console.log(`Overall Security Score: ${report.securityScore}/100`);
        
        const scoreColor = report.securityScore >= 80 ? '🟢' : 
                         report.securityScore >= 60 ? '🟡' : '🔴';
        console.log(`Status: ${scoreColor} ${
            report.securityScore >= 80 ? 'SECURE' :
            report.securityScore >= 60 ? 'MODERATE' : 'VULNERABLE'
        }\n`);
        
        console.log('=== ETHERNET PORT ANALYSIS ===');
        console.log(`Total Ethernet Ports: ${report.ethernetAnalysis.totalPorts}`);
        console.log(`Enabled Ports: ${report.ethernetAnalysis.enabledPorts}`);
        
        if (report.ethernetAnalysis.securityIssues.length > 0) {
            console.log('\nEthernet Issues:');
            report.ethernetAnalysis.securityIssues.forEach(issue => {
                console.log(`   ⚠️  ${issue}`);
            });
        }
        
        console.log('\n=== VULNERABILITY SUMMARY ===');
        console.log(`High Severity: ${report.vulnerabilityCount.high} 🚨`);
        console.log(`Medium Severity: ${report.vulnerabilityCount.medium} ⚠️`);
        console.log(`Low Severity: ${report.vulnerabilityCount.low} ℹ️`);
        console.log(`Total Issues: ${report.vulnerabilityCount.total}\n`);
        
        if (report.vulnerabilityCount.high > 0) {
            console.log('🚨 CRITICAL SECURITY ISSUES:');
            const highIssues = report.networkInfo.securityIssues.filter(i => i.severity === 'HIGH');
            highIssues.forEach(issue => {
                console.log(`   ❌ ${issue.type}: ${issue.description}`);
                console.log(`      💡 ${issue.recommendation}\n`);
            });
        }
        
        console.log('🔧 IMMEDIATE ACTIONS REQUIRED:');
        report.recommendations.slice(0, 5).forEach((rec, index) => {
            const priority = rec.priority === 'HIGH' ? '🚨' : 
                           rec.priority === 'MEDIUM' ? '⚠️' : 'ℹ️';
            console.log(`   ${index + 1}. ${priority} ${rec.action}`);
        });
        
        console.log('\n📋 ETHERNET SECURITY RECOMMENDATIONS:');
        report.ethernetAnalysis.recommendations.forEach((rec, index) => {
            console.log(`   ${index + 1}. ${rec}`);
        });
        
        console.log('\n🔒 NETWORK SECURITY BEST PRACTICES:');
        console.log('   • Keep Windows updated with latest security patches');
        console.log('   • Enable Windows Firewall for all network profiles');
        console.log('   • Disable unused network services and protocols');
        console.log('   • Use strong, unique passwords for network accounts');
        console.log('   • Monitor network traffic for suspicious activity');
        console.log('   • Segment network with VLANs for critical systems');
        console.log('   • Regularly backup network configurations');
        
    } catch (error) {
        console.error('Network analysis failed:', error.message);
    }
}

if (require.main === module) {
    main();
}

module.exports = WindowsNetworkDetector;
