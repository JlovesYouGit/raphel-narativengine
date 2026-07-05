#!/usr/bin/env node

/**
 * QODER + OpenClaw MCP Doctor
 * Diagnostic and troubleshooting tool
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class MCPDoctor {
    constructor() {
        this.projectRoot = __dirname;
        this.issues = [];
        this.warnings = [];
        this.passed = [];
    }

    async run() {
        console.log('🩺 QODER + OpenClaw MCP Doctor\n');
        console.log('Running comprehensive diagnostic check...\n');

        try {
            await this.checkEnvironment();
            await this.checkFiles();
            await this.checkDependencies();
            await this.checkConfiguration();
            await this.checkOpenClawStructure();
            await this.checkMCPIntegration();
            await this.checkPermissions();
            await this.generateReport();

        } catch (error) {
            console.error('❌ Doctor failed:', error.message);
            process.exit(1);
        }
    }

    async checkEnvironment() {
        console.log('🌍 Environment Check');

        // Node.js version
        const nodeVersion = process.version;
        const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
        
        if (majorVersion >= 14) {
            this.passed.push(`Node.js version: ${nodeVersion} ✅`);
        } else {
            this.issues.push(`Node.js version ${nodeVersion} is too old (requires >= 14.0.0)`);
        }

        // Platform
        const platform = process.platform;
        this.passed.push(`Platform: ${platform} ✅`);

        // Working directory
        const cwd = process.cwd();
        if (cwd.includes('Windsurf') || cwd.includes('windsurf')) {
            this.passed.push(`Working directory: ${cwd} ✅`);
        } else {
            this.warnings.push(`Working directory may not be optimal: ${cwd}`);
        }

        console.log('  Environment check complete\n');
    }

    async checkFiles() {
        console.log('📁 File Structure Check');

        const requiredFiles = [
            'simple-mcp-server.js',
            'windsurf-direct-integration.js',
            'expanded-skills-fixed.js',
            'dynamic-skill-discovery.js',
            'package.json',
            'setup.js',
            'test-integration.js',
            'README.md'
        ];

        for (const file of requiredFiles) {
            const filePath = path.join(this.projectRoot, file);
            if (fs.existsSync(filePath)) {
                const stats = fs.statSync(filePath);
                this.passed.push(`${file} exists (${stats.size} bytes) ✅`);
            } else {
                this.issues.push(`Required file missing: ${file}`);
            }
        }

        console.log('  File structure check complete\n');
    }

    async checkDependencies() {
        console.log('📦 Dependencies Check');

        try {
            const packageJson = JSON.parse(fs.readFileSync(path.join(this.projectRoot, 'package.json'), 'utf8'));
            
            // Check if dependencies are installed
            const nodeModulesPath = path.join(this.projectRoot, 'node_modules');
            if (fs.existsSync(nodeModulesPath)) {
                this.passed.push('node_modules directory exists ✅');
                
                // Check key dependencies
                const keyDeps = ['axios', 'ws', 'express', 'fs-extra', 'dotenv'];
                for (const dep of keyDeps) {
                    const depPath = path.join(nodeModulesPath, dep);
                    if (fs.existsSync(depPath)) {
                        this.passed.push(`Dependency ${dep} installed ✅`);
                    } else {
                        this.issues.push(`Dependency ${dep} not installed`);
                    }
                }
            } else {
                this.issues.push('node_modules directory missing - run npm install');
            }

            // Check package.json structure
            if (packageJson.dependencies && packageJson.scripts) {
                this.passed.push('package.json structure valid ✅');
            } else {
                this.issues.push('package.json missing required sections');
            }

        } catch (error) {
            this.issues.push(`Failed to check dependencies: ${error.message}`);
        }

        console.log('  Dependencies check complete\n');
    }

    async checkConfiguration() {
        console.log('⚙️ Configuration Check');

        // Check .env file
        const envPath = path.join(this.projectRoot, '.env');
        if (fs.existsSync(envPath)) {
            this.passed.push('.env file exists ✅');
            
            const envContent = fs.readFileSync(envPath, 'utf8');
            const requiredEnvVars = ['AUTO_ACCESSIBLE', 'OPENCLAW_SIMPLE_MODE', 'QODER_SIMPLE_MODE'];
            
            for (const envVar of requiredEnvVars) {
                if (envContent.includes(envVar)) {
                    this.passed.push(`Environment variable ${envVar} set ✅`);
                } else {
                    this.warnings.push(`Environment variable ${envVar} not set`);
                }
            }
        } else {
            this.warnings.push('.env file not found - run setup.js to create it');
        }

        console.log('  Configuration check complete\n');
    }

    async checkOpenClawStructure() {
        console.log('🦾 OpenClaw Structure Check');

        const clawPath = path.join(this.projectRoot, 'qoder-integration', 'openclaw');
        
        if (fs.existsSync(clawPath)) {
            this.passed.push('OpenClaw directory exists ✅');
            
            // Check subdirectories
            const requiredDirs = ['apps', 'channels', 'config', 'logs', 'runtime', 'skills', 'tools'];
            for (const dir of requiredDirs) {
                const dirPath = path.join(clawPath, dir);
                if (fs.existsSync(dirPath)) {
                    this.passed.push(`OpenClaw directory ${dir} exists ✅`);
                } else {
                    this.issues.push(`OpenClaw directory missing: ${dir}`);
                }
            }

            // Check configuration files
            const requiredConfigs = ['channels.json', 'skills.json', 'tools.json', 'core-platform.json', 'runtime.json'];
            for (const config of requiredConfigs) {
                const configPath = path.join(clawPath, config);
                if (fs.existsSync(configPath)) {
                    try {
                        JSON.parse(fs.readFileSync(configPath, 'utf8'));
                        this.passed.push(`OpenClaw config ${config} valid ✅`);
                    } catch (error) {
                        this.issues.push(`OpenClaw config ${config} invalid JSON`);
                    }
                } else {
                    this.issues.push(`OpenClaw config missing: ${config}`);
                }
            }
        } else {
            this.issues.push('OpenClaw directory missing - run setup.js to create it');
        }

        console.log('  OpenClaw structure check complete\n');
    }

    async checkMCPIntegration() {
        console.log('🔌 MCP Integration Check');

        try {
            // Check if MCP server can be loaded
            const SimpleMCPServer = require('./simple-mcp-server');
            const server = new SimpleMCPServer();
            
            if (server.start && typeof server.start === 'function') {
                this.passed.push('MCP Server class loads correctly ✅');
            } else {
                this.issues.push('MCP Server class missing required methods');
            }

            // Check Windsurf integration
            const WindsurfDirectIntegration = require('./windsurf-direct-integration');
            const integration = new WindsurfDirectIntegration();
            
            if (integration.getFeatures && typeof integration.getFeatures === 'function') {
                const features = integration.getFeatures();
                const featureCount = Object.keys(features).length;
                this.passed.push(`Windsurf Integration loads with ${featureCount} features ✅`);
            } else {
                this.issues.push('Windsurf Integration class missing required methods');
            }

        } catch (error) {
            this.issues.push(`MCP Integration check failed: ${error.message}`);
        }

        console.log('  MCP Integration check complete\n');
    }

    async checkPermissions() {
        console.log('🔐 Permissions Check');

        try {
            // Check if we can write to the project directory
            const testFile = path.join(this.projectRoot, '.doctor-test');
            fs.writeFileSync(testFile, 'test');
            fs.unlinkSync(testFile);
            this.passed.push('Write permissions OK ✅');
        } catch (error) {
            this.issues.push(`Write permissions issue: ${error.message}`);
        }

        // Check if we can execute node
        try {
            execSync('node --version', { stdio: 'ignore' });
            this.passed.push('Node.js execution OK ✅');
        } catch (error) {
            this.issues.push('Node.js execution failed');
        }

        console.log('  Permissions check complete\n');
    }

    async generateReport() {
        console.log('📋 Diagnostic Report');
        console.log('='.repeat(60));

        if (this.passed.length > 0) {
            console.log(`\n✅ Passed Checks (${this.passed.length}):`);
            this.passed.forEach(check => console.log(`   ${check}`));
        }

        if (this.warnings.length > 0) {
            console.log(`\n⚠️ Warnings (${this.warnings.length}):`);
            this.warnings.forEach(warning => console.log(`   ${warning}`));
        }

        if (this.issues.length > 0) {
            console.log(`\n❌ Issues Found (${this.issues.length}):`);
            this.issues.forEach(issue => console.log(`   ${issue}`));
        }

        console.log('\n' + '='.repeat(60));

        // Recommendations
        if (this.issues.length > 0) {
            console.log('\n🔧 Recommended Actions:');
            
            if (this.issues.some(issue => issue.includes('npm install'))) {
                console.log('   1. Run: npm install');
            }
            
            if (this.issues.some(issue => issue.includes('setup.js'))) {
                console.log('   2. Run: node setup.js');
            }
            
            if (this.issues.some(issue => issue.includes('missing'))) {
                console.log('   3. Ensure all required files are present');
            }
            
            console.log('   4. Run: npm test to verify installation');
        }

        // Overall status
        if (this.issues.length === 0) {
            console.log('\n🎉 All checks passed! Integration is healthy.');
            console.log('\n🚀 Ready to start the MCP server:');
            console.log('   npm start');
        } else {
            console.log(`\n⚠️ ${this.issues.length} issues found. Please address them before using the integration.`);
        }
    }
}

// Run doctor if called directly
if (require.main === module) {
    const doctor = new MCPDoctor();
    doctor.run();
}

module.exports = MCPDoctor;
