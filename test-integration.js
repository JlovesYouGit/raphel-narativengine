#!/usr/bin/env node

/**
 * QODER + OpenClaw MCP Integration Test
 * Verifies all components are working correctly
 */

const fs = require('fs');
const path = require('path');

class IntegrationTester {
    constructor() {
        this.projectRoot = __dirname;
        this.results = {
            passed: 0,
            failed: 0,
            tests: []
        };
    }

    async run() {
        console.log('🧪 Running QODER + OpenClaw Integration Tests...\n');

        try {
            await this.testFileStructure();
            await this.testDependencies();
            await this.testMCPServer();
            await this.testWindsurfIntegration();
            await this.testOpenClawStructure();
            await this.testConfiguration();

            this.printResults();

        } catch (error) {
            console.error('\n❌ Test suite failed:', error.message);
            process.exit(1);
        }
    }

    async testFileStructure() {
        this.test('File Structure Check', () => {
            const requiredFiles = [
                'simple-mcp-server.js',
                'windsurf-direct-integration.js',
                'expanded-skills-fixed.js',
                'dynamic-skill-discovery.js',
                'package.json',
                'setup.js'
            ];

            for (const file of requiredFiles) {
                const filePath = path.join(this.projectRoot, file);
                if (!fs.existsSync(filePath)) {
                    throw new Error(`Missing required file: ${file}`);
                }
            }

            return `All ${requiredFiles.length} required files present`;
        });
    }

    async testDependencies() {
        this.test('Dependencies Check', () => {
            try {
                const packageJson = require('./package.json');
                const requiredDeps = ['axios', 'ws', 'express', 'fs-extra', 'dotenv'];
                
                for (const dep of requiredDeps) {
                    if (!packageJson.dependencies[dep]) {
                        throw new Error(`Missing dependency: ${dep}`);
                    }
                }

                return `All ${requiredDeps.length} dependencies configured`;
            } catch (error) {
                throw new Error('Package.json dependencies check failed: ' + error.message);
            }
        });
    }

    async testMCPServer() {
        this.test('MCP Server Loading', () => {
            try {
                const SimpleMCPServer = require('./simple-mcp-server');
                const server = new SimpleMCPServer();
                
                if (!server.start || typeof server.start !== 'function') {
                    throw new Error('MCP Server missing start method');
                }

                return 'MCP Server class loads correctly';
            } catch (error) {
                throw new Error('MCP Server loading failed: ' + error.message);
            }
        });
    }

    async testWindsurfIntegration() {
        this.test('Windsurf Integration Loading', () => {
            try {
                const WindsurfDirectIntegration = require('./windsurf-direct-integration');
                const integration = new WindsurfDirectIntegration();
                
                if (!integration.initialize || typeof integration.initialize !== 'function') {
                    throw new Error('Integration missing initialize method');
                }

                // Initialize features setup
                integration.setupFeatures();
                
                const features = integration.getFeatures();
                const expectedFeatures = ['qoder.enhance', 'qoder.monitor', 'openclaw.chat', 'openclaw.automate', 'openclaw.skill'];
                
                for (const feature of expectedFeatures) {
                    if (!features[feature]) {
                        throw new Error(`Missing feature: ${feature}`);
                    }
                }

                return `Windsurf Integration loads with ${Object.keys(features).length} features`;
            } catch (error) {
                throw new Error('Windsurf Integration loading failed: ' + error.message);
            }
        });
    }

    async testOpenClawStructure() {
        this.test('OpenClaw Structure Check', () => {
            const clawPath = path.join(this.projectRoot, 'qoder-integration', 'openclaw');
            
            if (!fs.existsSync(clawPath)) {
                throw new Error('OpenClaw directory missing');
            }

            const requiredDirs = ['apps', 'channels', 'config', 'logs', 'runtime', 'skills', 'tools'];
            for (const dir of requiredDirs) {
                const dirPath = path.join(clawPath, dir);
                if (!fs.existsSync(dirPath)) {
                    throw new Error(`Missing OpenClaw directory: ${dir}`);
                }
            }

            const requiredConfigs = ['channels.json', 'skills.json', 'tools.json', 'core-platform.json', 'runtime.json'];
            for (const config of requiredConfigs) {
                const configPath = path.join(clawPath, config);
                if (!fs.existsSync(configPath)) {
                    throw new Error(`Missing OpenClaw config: ${config}`);
                }
            }

            return `OpenClaw structure complete with ${requiredDirs.length} directories and ${requiredConfigs.length} configs`;
        });
    }

    async testConfiguration() {
        this.test('Configuration Validation', () => {
            const clawPath = path.join(this.projectRoot, 'qoder-integration', 'openclaw');
            
            // Test channels.json
            const channelsConfig = JSON.parse(fs.readFileSync(path.join(clawPath, 'channels.json'), 'utf8'));
            const expectedChannels = ['whatsapp', 'telegram', 'slack', 'discord', 'webchat'];
            
            for (const channel of expectedChannels) {
                if (!channelsConfig[channel]) {
                    throw new Error(`Missing channel config: ${channel}`);
                }
            }

            // Test skills.json
            const skillsConfig = JSON.parse(fs.readFileSync(path.join(clawPath, 'skills.json'), 'utf8'));
            if (!skillsConfig.bundled || !skillsConfig.managed) {
                throw new Error('Skills config missing required sections');
            }

            // Test tools.json
            const toolsConfig = JSON.parse(fs.readFileSync(path.join(clawPath, 'tools.json'), 'utf8'));
            if (!toolsConfig.browser_control || !toolsConfig.canvas) {
                throw new Error('Tools config missing required sections');
            }

            return 'All configuration files valid';
        });
    }

    test(name, testFn) {
        try {
            const result = testFn();
            this.results.passed++;
            this.results.tests.push({ name, status: 'PASS', result });
            console.log(`✅ ${name}: ${result}`);
        } catch (error) {
            this.results.failed++;
            this.results.tests.push({ name, status: 'FAIL', error: error.message });
            console.log(`❌ ${name}: ${error.message}`);
        }
    }

    printResults() {
        console.log('\n' + '='.repeat(60));
        console.log('🏁 Test Results Summary');
        console.log('='.repeat(60));
        console.log(`✅ Passed: ${this.results.passed}`);
        console.log(`❌ Failed: ${this.results.failed}`);
        console.log(`📊 Total:  ${this.results.tests.length}`);
        
        if (this.results.failed > 0) {
            console.log('\n❌ Failed Tests:');
            this.results.tests
                .filter(test => test.status === 'FAIL')
                .forEach(test => {
                    console.log(`   - ${test.name}: ${test.error}`);
                });
        }

        if (this.results.failed === 0) {
            console.log('\n🎉 All tests passed! Integration is ready.');
        } else {
            console.log('\n⚠️ Some tests failed. Please fix the issues before using the integration.');
            process.exit(1);
        }
    }
}

// Run tests if called directly
if (require.main === module) {
    const tester = new IntegrationTester();
    tester.run();
}

module.exports = IntegrationTester;
