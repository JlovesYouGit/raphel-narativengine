const NetworkSecurityManager = require('./network_security_manager.js');

class NetworkSecurityUpdater {
    constructor() {
        this.securityManager = new NetworkSecurityManager();
        this.updateQueue = [];
        this.isProcessing = false;
    }

    async initialize() {
        console.log('🔄 Initializing Network Security Updater...\n');
        await this.securityManager.initializeNetworkSecurity();
        console.log('✅ Security Updater Ready\n');
    }

    async addDeviceToWhitelist(macAddress, deviceName = '') {
        console.log(`➕ Adding device to whitelist: ${macAddress}`);
        
        try {
            // Validate MAC address
            if (!this.securityManager.macFilter.validateMAC(macAddress)) {
                throw new Error('Invalid MAC address format');
            }
            
            // Add to whitelist
            this.securityManager.securityConfig.macWhitelist.push(macAddress.toUpperCase());
            
            // Remove from blocked list if present
            const blockedIndex = this.securityManager.securityConfig.blockedMACs.indexOf(macAddress.toUpperCase());
            if (blockedIndex > -1) {
                this.securityManager.securityConfig.blockedMACs.splice(blockedIndex, 1);
            }
            
            // Apply firewall rule
            await this.securityManager.ethernetController.applyMACFiltering('ALLOW', macAddress, `Whitelisted: ${deviceName}`);
            
            // Save configuration
            await this.securityManager.saveSecurityConfiguration();
            
            console.log(`✅ Device ${macAddress} added to whitelist`);
            return { success: true, message: 'Device whitelisted successfully' };
            
        } catch (error) {
            console.error(`❌ Error adding device to whitelist: ${error.message}`);
            return { success: false, message: error.message };
        }
    }

    async blockDevice(macAddress, reason = '') {
        console.log(`🚫 Blocking device: ${macAddress}`);
        
        try {
            // Validate MAC address
            if (!this.securityManager.macFilter.validateMAC(macAddress)) {
                throw new Error('Invalid MAC address format');
            }
            
            // Add to blocked list
            this.securityManager.securityConfig.blockedMACs.push(macAddress.toUpperCase());
            
            // Remove from whitelist if present
            const whitelistIndex = this.securityManager.securityConfig.macWhitelist.indexOf(macAddress.toUpperCase());
            if (whitelistIndex > -1) {
                this.securityManager.securityConfig.macWhitelist.splice(whitelistIndex, 1);
            }
            
            // Apply firewall rule
            await this.securityManager.ethernetController.applyMACFiltering('BLOCK', macAddress, `Blocked: ${reason}`);
            
            // Save configuration
            await this.securityManager.saveSecurityConfiguration();
            
            console.log(`✅ Device ${macAddress} blocked successfully`);
            return { success: true, message: 'Device blocked successfully' };
            
        } catch (error) {
            console.error(`❌ Error blocking device: ${error.message}`);
            return { success: false, message: error.message };
        }
    }

    async removeDevice(macAddress) {
        console.log(`🗑️  Removing device from all lists: ${macAddress}`);
        
        try {
            // Validate MAC address
            if (!this.securityManager.macFilter.validateMAC(macAddress)) {
                throw new Error('Invalid MAC address format');
            }
            
            // Remove from whitelist
            const whitelistIndex = this.securityManager.securityConfig.macWhitelist.indexOf(macAddress.toUpperCase());
            if (whitelistIndex > -1) {
                this.securityManager.securityConfig.macWhitelist.splice(whitelistIndex, 1);
            }
            
            // Remove from blocked list
            const blockedIndex = this.securityManager.securityConfig.blockedMACs.indexOf(macAddress.toUpperCase());
            if (blockedIndex > -1) {
                this.securityManager.securityConfig.blockedMACs.splice(blockedIndex, 1);
            }
            
            // Remove firewall rule
            await this.securityManager.ethernetController.applyMACFiltering('REMOVE', macAddress);
            
            // Save configuration
            await this.securityManager.saveSecurityConfiguration();
            
            console.log(`✅ Device ${macAddress} removed from all security lists`);
            return { success: true, message: 'Device removed successfully' };
            
        } catch (error) {
            console.error(`❌ Error removing device: ${error.message}`);
            return { success: false, message: error.message };
        }
    }

    async updateEthernetPort(adapterName, settings) {
        console.log(`🔧 Updating Ethernet port: ${adapterName}`);
        
        try {
            const result = await this.securityManager.ethernetController.updateAdapterSettings(adapterName, settings);
            console.log(`✅ Ethernet port updated: ${result}`);
            return { success: true, message: result };
            
        } catch (error) {
            console.error(`❌ Error updating Ethernet port: ${error.message}`);
            return { success: false, message: error.message };
        }
    }

    async refreshNetworkSecurity() {
        console.log('🔄 Refreshing Network Security...\n');
        
        try {
            // Re-run the complete security process
            const report = await this.securityManager.detectAndSecureNetwork();
            
            console.log('✅ Network security refreshed');
            return { success: true, report };
            
        } catch (error) {
            console.error(`❌ Error refreshing network security: ${error.message}`);
            return { success: false, message: error.message };
        }
    }

    async getSecurityStatus() {
        const config = this.securityManager.securityConfig;
        const adapters = await this.securityManager.ethernetController.getEthernetAdapters();
        
        return {
            timestamp: new Date().toISOString(),
            whitelistedDevices: config.macWhitelist.length,
            blockedDevices: config.blockedMACs.length,
            totalEthernetAdapters: adapters.length,
            securityLevel: config.securityLevel,
            configuration: {
                macWhitelist: config.macWhitelist,
                blockedMACs: config.blockedMACs,
                trustedDevices: config.trustedDevices
            },
            ethernetAdapters: adapters
        };
    }

    async batchUpdateDevices(updates) {
        console.log(`📦 Processing ${updates.length} batch updates...\n`);
        
        const results = [];
        
        for (const update of updates) {
            try {
                let result;
                
                switch (update.action) {
                    case 'whitelist':
                        result = await this.addDeviceToWhitelist(update.mac, update.name);
                        break;
                    case 'block':
                        result = await this.blockDevice(update.mac, update.reason);
                        break;
                    case 'remove':
                        result = await this.removeDevice(update.mac);
                        break;
                    default:
                        result = { success: false, message: 'Unknown action' };
                }
                
                results.push({
                    mac: update.mac,
                    action: update.action,
                    ...result
                });
                
            } catch (error) {
                results.push({
                    mac: update.mac,
                    action: update.action,
                    success: false,
                    message: error.message
                });
            }
        }
        
        console.log(`✅ Batch update complete: ${results.filter(r => r.success).length}/${results.length} successful`);
        return results;
    }
}

// Interactive command interface
async function runInteractiveMode() {
    const updater = new NetworkSecurityUpdater();
    await updater.initialize();
    
    console.log('🎮 Network Security Interactive Mode\n');
    console.log('Available commands:');
    console.log('  whitelist <MAC> [name]  - Add device to whitelist');
    console.log('  block <MAC> [reason]     - Block device');
    console.log('  remove <MAC>             - Remove device from all lists');
    console.log('  status                   - Show security status');
    console.log('  refresh                  - Refresh network security');
    console.log('  update <adapter> <settings> - Update Ethernet adapter');
    console.log('  help                     - Show this help');
    console.log('  exit                     - Exit interactive mode\n');
    
    // Simple command loop (in a real implementation, you'd use readline)
    process.stdin.setEncoding('utf8');
    process.stdin.on('readable', () => {
        const chunk = process.stdin.read();
        if (chunk !== null) {
            const command = chunk.trim().split(' ');
            handleCommand(command, updater);
        }
    });
}

async function handleCommand(command, updater) {
    const [cmd, ...args] = command;
    
    try {
        switch (cmd.toLowerCase()) {
            case 'whitelist':
                if (args.length < 1) {
                    console.log('Usage: whitelist <MAC> [name]');
                    return;
                }
                const whitelistResult = await updater.addDeviceToWhitelist(args[0], args[1] || '');
                console.log(whitelistResult.success ? '✅ Success' : '❌ Failed:', whitelistResult.message);
                break;
                
            case 'block':
                if (args.length < 1) {
                    console.log('Usage: block <MAC> [reason]');
                    return;
                }
                const blockResult = await updater.blockDevice(args[0], args.slice(1).join(' ') || 'Security policy');
                console.log(blockResult.success ? '✅ Success' : '❌ Failed:', blockResult.message);
                break;
                
            case 'remove':
                if (args.length < 1) {
                    console.log('Usage: remove <MAC>');
                    return;
                }
                const removeResult = await updater.removeDevice(args[0]);
                console.log(removeResult.success ? '✅ Success' : '❌ Failed:', removeResult.message);
                break;
                
            case 'status':
                const status = await updater.getSecurityStatus();
                console.log('\n📊 Security Status:');
                console.log(`   Whitelisted Devices: ${status.whitelistedDevices}`);
                console.log(`   Blocked Devices: ${status.blockedDevices}`);
                console.log(`   Ethernet Adapters: ${status.totalEthernetAdapters}`);
                console.log(`   Security Level: ${status.securityLevel}`);
                break;
                
            case 'refresh':
                console.log('Refreshing network security...');
                const refreshResult = await updater.refreshNetworkSecurity();
                console.log(refreshResult.success ? '✅ Security refreshed' : '❌ Failed:', refreshResult.message);
                break;
                
            case 'help':
                console.log('Available commands:');
                console.log('  whitelist <MAC> [name]  - Add device to whitelist');
                console.log('  block <MAC> [reason]     - Block device');
                console.log('  remove <MAC>             - Remove device from all lists');
                console.log('  status                   - Show security status');
                console.log('  refresh                  - Refresh network security');
                console.log('  help                     - Show this help');
                console.log('  exit                     - Exit interactive mode');
                break;
                
            case 'exit':
                console.log('👋 Exiting interactive mode');
                process.exit(0);
                break;
                
            default:
                console.log(`Unknown command: ${cmd}. Type 'help' for available commands.`);
        }
    } catch (error) {
        console.error('Command error:', error.message);
    }
}

// Example usage
async function exampleUsage() {
    console.log('🔧 Example Network Security Operations\n');
    
    const updater = new NetworkSecurityUpdater();
    await updater.initialize();
    
    // Example 1: Add a trusted device
    console.log('1. Adding trusted device to whitelist...');
    await updater.addDeviceToWhitelist('00:11:22:33:44:55', 'Laptop-John');
    
    // Example 2: Block a suspicious device
    console.log('\n2. Blocking suspicious device...');
    await updater.blockDevice('AA:BB:CC:DD:EE:FF', 'Unknown device detected');
    
    // Example 3: Update Ethernet adapter
    console.log('\n3. Updating Ethernet adapter settings...');
    await updater.updateEthernetPort('Ethernet', {
        staticIP: '192.168.1.100',
        subnet: '255.255.255.0',
        gateway: '192.168.1.1',
        dns: '1.1.1.1'
    });
    
    // Example 4: Check security status
    console.log('\n4. Current security status:');
    const status = await updater.getSecurityStatus();
    console.log(JSON.stringify(status, null, 2));
    
    // Example 5: Batch update
    console.log('\n5. Batch device updates...');
    const batchUpdates = [
        { action: 'whitelist', mac: '11:22:33:44:55:66', name: 'Phone-Mary' },
        { action: 'block', mac: '77:88:99:AA:BB:CC', reason: 'Unauthorized device' },
        { action: 'remove', mac: 'DD:EE:FF:00:11:22' }
    ];
    
    const batchResults = await updater.batchUpdateDevices(batchUpdates);
    console.log('Batch results:', batchResults);
}

async function main() {
    console.log('🛡️  Network Security Updater\n');
    
    if (process.argv.includes('--interactive')) {
        await runInteractiveMode();
    } else if (process.argv.includes('--example')) {
        await exampleUsage();
    } else {
        console.log('Usage:');
        console.log('  node network_security_updater.js --interactive  - Run in interactive mode');
        console.log('  node network_security_updater.js --example      - Run example operations');
        console.log('\nStarting example operations...\n');
        await exampleUsage();
    }
}

if (require.main === module) {
    main();
}

module.exports = NetworkSecurityUpdater;
