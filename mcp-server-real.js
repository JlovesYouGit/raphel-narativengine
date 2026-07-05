#!/usr/bin/env node

/**
 * Real OpenClaw MCP Server
 * Integrates with actual OpenClaw capabilities and IDE AI
 */

const WindsurfDirectIntegration = require('./windsurf-direct-integration');

class RealMCPServer {
    constructor() {
        this.integration = null;
        this.isRunning = false;
        this.initialized = false;
    }

    async start() {
        // Only log to stderr to avoid interfering with MCP protocol
        console.error('🚀 Starting Real OpenClaw MCP Server...');
        
        try {
            // Initialize real integration
            this.integration = new WindsurfDirectIntegration();
            
            // Initialize silently but with real capabilities
            await this.integration.initializeSilent();
            
            this.isRunning = true;
            this.initialized = true;
            this.listenForRequests();
            
            console.error('✅ Real OpenClaw MCP Server running');
            
        } catch (error) {
            console.error('❌ MCP Server failed to start:', error);
        }
    }

    listenForRequests() {
        process.stdin.setEncoding('utf8');
        process.stdin.on('data', async (data) => {
            try {
                const message = data.toString().trim();
                if (message) {
                    await this.handleMessage(message);
                }
            } catch (error) {
                this.sendError(error.message);
            }
        });
    }

    async handleMessage(message) {
        try {
            const request = JSON.parse(message);
            
            if (request.method === 'initialize') {
                this.sendResponse(request.id, {
                    protocolVersion: '2024-11-05',
                    capabilities: {
                        tools: {}
                    },
                    serverInfo: {
                        name: 'qoder-openclaw-real',
                        version: '1.0.0'
                    }
                });
            } else if (request.method === 'tools/list') {
                this.sendResponse(request.id, {
                    tools: [
                        {
                            name: 'qoder_enhance',
                            description: 'AI code enhancement using QODER',
                            inputSchema: {
                                type: 'object',
                                properties: {
                                    code: { type: 'string' }
                                },
                                required: ['code']
                            }
                        },
                        {
                            name: 'qoder_monitor',
                            description: 'Security monitoring using QODER',
                            inputSchema: {
                                type: 'object',
                                properties: {
                                    content: { type: 'string' }
                                },
                                required: ['content']
                            }
                        },
                        {
                            name: 'openclaw_chat',
                            description: 'AI chat assistant using OpenClaw',
                            inputSchema: {
                                type: 'object',
                                properties: {
                                    message: { type: 'string' }
                                },
                                required: ['message']
                            }
                        },
                        {
                            name: 'openclaw_automate',
                            description: 'Task automation using OpenClaw',
                            inputSchema: {
                                type: 'object',
                                properties: {
                                    task: { type: 'string' }
                                },
                                required: ['task']
                            }
                        },
                        {
                            name: 'openclaw_skill',
                            description: 'Execute AI skill using OpenClaw',
                            inputSchema: {
                                type: 'object',
                                properties: {
                                    skill: { type: 'string' },
                                    input: { type: 'string' }
                                },
                                required: ['skill', 'input']
                            }
                        },
                        {
                            name: 'ai_ask',
                            description: 'Unified AI assistant (IDE AI + OpenClaw)',
                            inputSchema: {
                                type: 'object',
                                properties: {
                                    query: { type: 'string' }
                                },
                                required: ['query']
                            }
                        }
                    ]
                });
            } else if (request.method === 'tools/call') {
                await this.handleToolCall(request);
            } else {
                this.sendError('Unknown method: ' + request.method, request.id);
            }
        } catch (error) {
            this.sendError('Invalid message: ' + error.message);
        }
    }

    async handleToolCall(request) {
        const { name, arguments: args } = request.params;
        
        try {
            let result;
            
            // Use real OpenClaw integration
            if (this.integration && this.initialized) {
                switch (name) {
                    case 'qoder_enhance':
                        result = await this.integration.execute('qoder.enhance', { code: args.code });
                        break;
                    case 'qoder_monitor':
                        result = await this.integration.execute('qoder.monitor', { content: args.content });
                        break;
                    case 'openclaw_chat':
                        result = await this.integration.execute('openclaw.chat', { message: args.message });
                        break;
                    case 'openclaw_automate':
                        result = await this.integration.execute('openclaw.automate', { task: args.task });
                        break;
                    case 'openclaw_skill':
                        result = await this.integration.execute('openclaw.skill', { skill: args.skill, input: args.input });
                        break;
                    case 'ai_ask':
                        // Use unified AI assistant - this will use IDE AI capabilities
                        result = await this.integration.askAI(args.query);
                        break;
                    default:
                        throw new Error('Unknown tool: ' + name);
                }
            } else {
                // Fallback to basic responses if integration not ready
                result = {
                    success: false,
                    error: 'OpenClaw integration not initialized',
                    fallback_response: 'Tool ' + name + ' called with args: ' + JSON.stringify(args),
                    timestamp: new Date().toISOString()
                };
            }
            
            this.sendResponse(request.id, {
                content: [{
                    type: 'text',
                    text: JSON.stringify(result, null, 2)
                }]
            });
            
        } catch (error) {
            this.sendError(error.message, request.id);
        }
    }

    sendResponse(id, result) {
        const response = {
            jsonrpc: '2.0',
            id: id,
            result: result
        };
        
        // Only write JSON to stdout for MCP protocol
        process.stdout.write(JSON.stringify(response) + '\n');
    }

    sendError(message, id = null) {
        const response = {
            jsonrpc: '2.0',
            id: id,
            error: {
                code: -1,
                message: message
            }
        };
        
        // Only write JSON to stdout for MCP protocol
        process.stdout.write(JSON.stringify(response) + '\n');
    }
}

// Start server when run directly
if (require.main === module) {
    const server = new RealMCPServer();
    server.start();
    
    // Handle shutdown
    process.on('SIGINT', () => {
        console.error('\n🛑 Shutting down Real OpenClaw MCP Server...');
        process.exit(0);
    });
}

module.exports = RealMCPServer;
