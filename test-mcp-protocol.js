#!/usr/bin/env node

/**
 * MCP Protocol Test
 * Tests the MCP server communication protocol
 */

const { spawn } = require('child_process');
const path = require('path');

class MCPProtocolTest {
    constructor() {
        this.serverPath = path.join(__dirname, 'mcp-server-minimal.js');
        this.server = null;
        this.responses = [];
    }

    async run() {
        console.log('🧪 Testing MCP Protocol Communication...\n');

        try {
            await this.startServer();
            await this.testInitialize();
            await this.testToolsList();
            await this.testToolCall();
            await this.stopServer();

            this.printResults();

        } catch (error) {
            console.error('\n❌ MCP Protocol test failed:', error.message);
            await this.stopServer();
            process.exit(1);
        }
    }

    async startServer() {
        console.log('🚀 Starting MCP Server...');

        return new Promise((resolve, reject) => {
            this.server = spawn('node', [this.serverPath], {
                stdio: ['pipe', 'pipe', 'pipe'],
                cwd: __dirname
            });

            let startupOutput = '';
            
            this.server.stdout.on('data', (data) => {
                const output = data.toString();
                startupOutput += output;
                console.log('📤 Server output:', output.trim());
                
                // Wait for server to be ready
                if (output.includes('Simple MCP Server running')) {
                    setTimeout(resolve, 1000); // Give it a moment to fully start
                }
            });

            this.server.stderr.on('data', (data) => {
                console.error('❌ Server error:', data.toString());
            });

            this.server.on('error', (error) => {
                reject(new Error('Failed to start server: ' + error.message));
            });

            this.server.on('exit', (code) => {
                if (code !== 0) {
                    reject(new Error('Server exited with code: ' + code));
                }
            });

            // Timeout after 10 seconds
            setTimeout(() => {
                if (!startupOutput.includes('Simple MCP Server running')) {
                    reject(new Error('Server startup timeout'));
                }
            }, 10000);
        });
    }

    async sendRequest(request) {
        return new Promise((resolve, reject) => {
            const requestId = Date.now();
            const fullRequest = {
                jsonrpc: '2.0',
                id: requestId,
                ...request
            };

            console.log('📤 Sending request:', JSON.stringify(fullRequest, null, 2));

            let responseReceived = false;
            
            const onData = (data) => {
                const output = data.toString().trim();
                if (!output) return;

                console.log('📥 Raw response:', output);

                try {
                    const lines = output.split('\n').filter(line => line.trim());
                    for (const line of lines) {
                        if (line.startsWith('{') && line.endsWith('}')) {
                            const response = JSON.parse(line);
                            if (response.id === requestId) {
                                responseReceived = true;
                                this.server.stdout.removeListener('data', onData);
                                resolve(response);
                                return;
                            }
                        }
                    }
                } catch (error) {
                    console.log('⚠️ Non-JSON output:', output);
                }
            };

            this.server.stdout.on('data', onData);

            // Send the request
            this.server.stdin.write(JSON.stringify(fullRequest) + '\n');

            // Timeout after 5 seconds
            setTimeout(() => {
                if (!responseReceived) {
                    this.server.stdout.removeListener('data', onData);
                    reject(new Error('Request timeout'));
                }
            }, 5000);
        });
    }

    async testInitialize() {
        console.log('\n🔧 Testing Initialize...');
        
        try {
            const response = await this.sendRequest({
                method: 'initialize',
                params: {
                    protocolVersion: '2024-11-05',
                    capabilities: {
                        tools: {}
                    },
                    clientInfo: {
                        name: 'test-client',
                        version: '1.0.0'
                    }
                }
            });

            if (response.result) {
                console.log('✅ Initialize successful');
                this.responses.push({ test: 'initialize', status: 'PASS', response });
            } else {
                throw new Error('Initialize failed: ' + JSON.stringify(response));
            }
        } catch (error) {
            console.log('❌ Initialize failed:', error.message);
            this.responses.push({ test: 'initialize', status: 'FAIL', error: error.message });
        }
    }

    async testToolsList() {
        console.log('\n🔧 Testing Tools List...');
        
        try {
            const response = await this.sendRequest({
                method: 'tools/list'
            });

            if (response.result && response.result.tools) {
                console.log('✅ Tools list successful');
                console.log(`   Found ${response.result.tools.length} tools:`);
                response.result.tools.forEach(tool => {
                    console.log(`   - ${tool.name}: ${tool.description}`);
                });
                this.responses.push({ test: 'tools/list', status: 'PASS', response });
            } else {
                throw new Error('Tools list failed: ' + JSON.stringify(response));
            }
        } catch (error) {
            console.log('❌ Tools list failed:', error.message);
            this.responses.push({ test: 'tools/list', status: 'FAIL', error: error.message });
        }
    }

    async testToolCall() {
        console.log('\n🔧 Testing Tool Call...');
        
        try {
            const response = await this.sendRequest({
                method: 'tools/call',
                params: {
                    name: 'ai_ask',
                    arguments: {
                        query: 'hello world test'
                    }
                }
            });

            if (response.result && response.result.content) {
                console.log('✅ Tool call successful');
                console.log('   Response:', JSON.stringify(response.result, null, 2));
                this.responses.push({ test: 'tools/call', status: 'PASS', response });
            } else {
                throw new Error('Tool call failed: ' + JSON.stringify(response));
            }
        } catch (error) {
            console.log('❌ Tool call failed:', error.message);
            this.responses.push({ test: 'tools/call', status: 'FAIL', error: error.message });
        }
    }

    async stopServer() {
        console.log('\n🛑 Stopping server...');
        
        if (this.server) {
            this.server.kill('SIGTERM');
            
            // Wait for graceful shutdown
            await new Promise(resolve => {
                this.server.on('exit', resolve);
                setTimeout(resolve, 2000); // Force close after 2 seconds
            });

            if (this.server && !this.server.killed) {
                this.server.kill('SIGKILL');
            }
        }
    }

    printResults() {
        console.log('\n' + '='.repeat(60));
        console.log('🏁 MCP Protocol Test Results');
        console.log('='.repeat(60));

        const passed = this.responses.filter(r => r.status === 'PASS').length;
        const failed = this.responses.filter(r => r.status === 'FAIL').length;

        console.log(`✅ Passed: ${passed}`);
        console.log(`❌ Failed: ${failed}`);
        console.log(`📊 Total:  ${this.responses.length}`);

        if (failed > 0) {
            console.log('\n❌ Failed Tests:');
            this.responses
                .filter(r => r.status === 'FAIL')
                .forEach(test => {
                    console.log(`   - ${test.test}: ${test.error}`);
                });
        }

        if (failed === 0) {
            console.log('\n🎉 All MCP protocol tests passed!');
            console.log('The server should work with Windsurf MCP.');
        } else {
            console.log('\n⚠️ MCP protocol issues detected.');
            console.log('This explains the red light in Windsurf.');
        }
    }
}

// Run test if called directly
if (require.main === module) {
    const test = new MCPProtocolTest();
    test.run();
}

module.exports = MCPProtocolTest;
