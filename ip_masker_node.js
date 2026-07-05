const https = require('https');
const crypto = require('crypto');

class IPMasker {
    constructor() {
        this.layer1Salt = 'first-layer-salt-2025';
        this.layer2Salt = 'second-layer-salt-2025';
        this.layer3Salt = 'third-layer-salt-2025';
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

    sha256Hash(data, salt = '') {
        const input = data + salt;
        return crypto.createHash('sha256').update(input).digest('hex');
    }

    maskIP(ip) {
        console.log(`Original IP: ${ip}`);
        
        const layer1 = this.sha256Hash(ip, this.layer1Salt);
        console.log(`Layer 1 Hash: ${layer1}`);
        
        const layer2 = this.sha256Hash(layer1, this.layer2Salt);
        console.log(`Layer 2 Hash: ${layer2}`);
        
        const layer3 = this.sha256Hash(layer2, this.layer3Salt);
        console.log(`Layer 3 Hash: ${layer3}`);
        
        return {
            original: ip,
            layer1: layer1,
            layer2: layer2,
            layer3: layer3,
            timestamp: new Date().toISOString()
        };
    }

    async getAndMaskIP() {
        try {
            const ip = await this.getPublicIP();
            return this.maskIP(ip);
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }
}

async function main() {
    const masker = new IPMasker();
    
    console.log('=== 3-Layer SHA-256 IP Masking System ===');
    console.log('Detecting and masking current IP address...\n');
    
    const result = await masker.getAndMaskIP();
    
    console.log('\n=== Final Result ===');
    console.log(`Original IP: ${result.original}`);
    console.log(`Final Masked IP: ${result.layer3}`);
    console.log(`Timestamp: ${result.timestamp}`);
    
    console.log('\n=== Network Encryption Simulation ===');
    console.log('Packet routing through encrypted layers:');
    console.log(`[Network] --> Layer1: ${result.layer1.substring(0, 16)}...`);
    console.log(`[Layer1] --> Layer2: ${result.layer2.substring(0, 16)}...`);
    console.log(`[Layer2] --> Layer3: ${result.layer3.substring(0, 16)}...`);
    console.log('[Layer3] --> Internet (Fully Encrypted)');
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = IPMasker;
