#!/usr/bin/env node

/**
 * QODER + OpenClaw MCP Setup Script
 * Automated installation and configuration
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class SetupManager {
    constructor() {
        this.projectRoot = __dirname;
        this.clawPath = path.join(this.projectRoot, 'qoder-integration', 'openclaw');
    }

    async run() {
        console.log('🚀 Setting up QODER + OpenClaw MCP Integration...\n');

        try {
            await this.checkPrerequisites();
            await this.installDependencies();
            await this.setupClawStructure();
            await this.configureEnvironment();
            await this.verifyInstallation();
            await this.createStartupScripts();

            console.log('\n✅ Setup completed successfully!');
            console.log('\n🎯 Next steps:');
            console.log('1. Restart Windsurf to load the MCP server');
            console.log('2. Use the tools in Windsurf via the MCP panel');
            console.log('3. Test with: qoderOpenclaw.ai.ask("hello")');

        } catch (error) {
            console.error('\n❌ Setup failed:', error.message);
            process.exit(1);
        }
    }

    async checkPrerequisites() {
        console.log('📋 Checking prerequisites...');

        // Check Node.js version
        const nodeVersion = process.version;
        const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
        
        if (majorVersion < 14) {
            throw new Error(`Node.js version ${nodeVersion} is too old. Requires >= 14.0.0`);
        }

        // Check if required files exist
        const requiredFiles = [
            'simple-mcp-server.js',
            'windsurf-direct-integration.js',
            'expanded-skills-fixed.js',
            'dynamic-skill-discovery.js'
        ];

        for (const file of requiredFiles) {
            const filePath = path.join(this.projectRoot, file);
            if (!fs.existsSync(filePath)) {
                throw new Error(`Required file missing: ${file}`);
            }
        }

        console.log('✅ Prerequisites check passed');
    }

    async installDependencies() {
        console.log('📦 Installing dependencies...');
        
        try {
            execSync('npm install', { stdio: 'inherit', cwd: this.projectRoot });
            console.log('✅ Dependencies installed');
        } catch (error) {
            throw new Error('Failed to install dependencies: ' + error.message);
        }
    }

    async setupClawStructure() {
        console.log('🏗️ Setting up OpenClaw structure...');

        // Ensure claw directory exists
        if (!fs.existsSync(this.clawPath)) {
            fs.mkdirSync(this.clawPath, { recursive: true });
        }

        // Create required subdirectories
        const subdirs = ['apps', 'channels', 'config', 'logs', 'runtime', 'skills', 'tools'];
        
        for (const subdir of subdirs) {
            const dirPath = path.join(this.clawPath, subdir);
            if (!fs.existsSync(dirPath)) {
                fs.mkdirSync(dirPath, { recursive: true });
            }
        }

        // Initialize configuration files if they don't exist
        await this.initializeConfigFiles();
        
        console.log('✅ OpenClaw structure ready');
    }

    async initializeConfigFiles() {
        const configFiles = {
            'channels.json': {
                whatsapp: { enabled: true, library: "Baileys", features: ["text", "media", "voice", "groups"] },
                telegram: { enabled: true, library: "grammY", features: ["text", "media", "voice", "groups"] },
                slack: { enabled: true, library: "Bolt", features: ["text", "media", "files", "threads"] },
                discord: { enabled: true, library: "discord.js", features: ["text", "media", "voice", "channels"] },
                signal: { enabled: false, library: "signal-cli", features: ["text", "media"] },
                webchat: { enabled: true, library: "native", features: ["text", "media", "real-time"] }
            },
            'skills.json': {
                bundled: {
                    assistant: { enabled: true, description: "General assistant skills" },
                    developer: { enabled: true, description: "Developer-focused skills" },
                    analyst: { enabled: true, description: "Data analysis skills" }
                },
                managed: {
                    custom: { enabled: true, description: "Custom user skills" },
                    workspace: { enabled: true, description: "Workspace-specific skills" }
                }
            },
            'tools.json': {
                browser_control: {
                    enabled: true,
                    features: ["snapshots", "actions", "uploads", "profiles"],
                    safety: "sandboxed"
                },
                canvas: {
                    enabled: true,
                    features: ["push", "reset", "eval", "snapshot"],
                    safety: "isolated"
                },
                automation: {
                    cron: { enabled: true, safety: "limited" },
                    webhooks: { enabled: true, safety: "validated" },
                    gmail: { enabled: false, safety: "auth_required" }
                }
            }
        };

        for (const [filename, content] of Object.entries(configFiles)) {
            const filePath = path.join(this.clawPath, filename);
            if (!fs.existsSync(filePath)) {
                fs.writeFileSync(filePath, JSON.stringify(content, null, 2));
            }
        }
    }

    async configureEnvironment() {
        console.log('⚙️ Configuring environment...');

        const envContent = `
# QODER + OpenClaw MCP Environment
AUTO_ACCESSIBLE=true
NO_SDK_REQUIRED=true
OPENCLAW_SIMPLE_MODE=true
QODER_SIMPLE_MODE=true

# OpenClaw Configuration
OPENCLAW_ROOT=${this.clawPath}
OPENCLAW_LOG_LEVEL=info
OPENCLAW_ENABLE_WEBHOOKS=true
OPENCLAW_ENABLE_AUTOMATION=true

# QODER Configuration
QODER_AI_MODEL=default
QODER_ENHANCEMENT_MODE=balanced
QODER_SECURITY_SCAN=true

# MCP Configuration
MCP_SERVER_NAME=qoder-openclaw-simple
MCP_SERVER_VERSION=1.0.0
`;

        const envPath = path.join(this.projectRoot, '.env');
        if (!fs.existsSync(envPath)) {
            fs.writeFileSync(envPath, envContent.trim());
        }

        console.log('✅ Environment configured');
    }

    async verifyInstallation() {
        console.log('🔍 Verifying installation...');

        try {
            // Test if the main server can be required
            const SimpleMCPServer = require('./simple-mcp-server');
            const WindsurfDirectIntegration = require('./windsurf-direct-integration');
            
            // Test initialization (dry run)
            const integration = new WindsurfDirectIntegration();
            const features = integration.getFeatures();
            
            console.log('✅ Installation verified');
            console.log(`   - Features available: ${Object.keys(features).length}`);
            console.log(`   - OpenClaw path: ${this.clawPath}`);
            
        } catch (error) {
            throw new Error('Installation verification failed: ' + error.message);
        }
    }

    async createStartupScripts() {
        console.log('📝 Creating startup scripts...');

        // Windows batch file
        const batContent = `@echo off
echo 🚀 Starting QODER + OpenClaw MCP Server...
cd /d "%~dp0"
node simple-mcp-server.js
pause
`;

        // Shell script for Unix systems
        const shContent = `#!/bin/bash
echo "🚀 Starting QODER + OpenClaw MCP Server..."
cd "$(dirname "$0")"
node simple-mcp-server.js
`;

        fs.writeFileSync(path.join(this.projectRoot, 'start.bat'), batContent);
        fs.writeFileSync(path.join(this.projectRoot, 'start.sh'), shContent);

        // Make shell script executable
        try {
            execSync('chmod +x start.sh', { cwd: this.projectRoot });
        } catch (error) {
            // Ignore chmod errors on Windows
        }

        console.log('✅ Startup scripts created');
    }
}

// Run setup if called directly
if (require.main === module) {
    const setup = new SetupManager();
    setup.run();
}

module.exports = SetupManager;
