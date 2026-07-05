#!/usr/bin/env node

/**
 * Simple MCP Server - Fixed Version
 * Proper MCP protocol communication without stdout interference
 */

const WindsurfDirectIntegration = require('./windsurf-direct-integration');

class SimpleMCPServerFixed {
    constructor() {
        this.integration = null;
        this.isRunning = false;
        this.initialized = false;
    }

    /**
     * Start MCP server
     */
    async start() {
        // Only log to stderr to avoid interfering with MCP protocol
        console.error('🚀 Starting Simple MCP Server (Fixed)...');
        
        try {
            // Initialize integration silently
            this.integration = new WindsurfDirectIntegration();
            await this.integration.initializeSilent();
            
            // Start listening for stdin
            this.isRunning = true;
            this.initialized = true;
            this.listenForRequests();
            
            console.error('✅ Simple MCP Server (Fixed) running');
            
        } catch (error) {
            console.error('❌ MCP Server failed to start:', error);
        }
    }

    /**
     * Listen for MCP requests
     */
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

    /**
     * Handle MCP message
     */
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
                        name: 'qoder-openclaw-simple',
                        version: '1.0.0'
                    }
                });
            } else if (request.method === 'tools/list') {
                this.sendResponse(request.id, {
                    tools: [
                        {
                            name: 'qoder_enhance',
                            description: 'AI code enhancement',
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
                            description: 'Security monitoring',
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
                            description: 'AI chat assistant',
                            inputSchema: {
                                type: 'object',
                                properties: {
                                    message: { type: 'string' }
                                },
                                required: ['message']
                            }
                        },
                        {
                            name: 'ai_ask',
                            description: 'Unified AI assistant',
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

    /**
     * Handle tool call
     */
    async handleToolCall(request) {
        const { name, arguments: args } = request.params;
        
        try {
            let result;
            
            // Simple mock responses for testing
            switch (name) {
                case 'qoder_enhance':
                    result = {
                        success: true,
                        enhanced_code: '// Enhanced by QODER\n' + args.code + '\n// Enhancement complete',
                        suggestions: ['Add error handling', 'Add documentation'],
                        timestamp: new Date().toISOString()
                    };
                    break;
                case 'qoder_monitor':
                    result = {
                        success: true,
                        security_score: 0.92,
                        issues: [],
                        recommendations: ['Keep dependencies updated'],
                        timestamp: new Date().toISOString()
                    };
                    break;
                case 'openclaw_chat':
                    result = {
                        success: true,
                        response: 'I understand: ' + args.message + '. Here is my assistance...',
                        confidence: 0.88,
                        timestamp: new Date().toISOString()
                    };
                    break;
                case 'ai_ask':
                    result = {
                        success: true,
                        answer: 'Response to: ' + args.query,
                        timestamp: new Date().toISOString()
                    };
                    break;
                default:
                    throw new Error('Unknown tool: ' + name);
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

    /**
     * Send response
     */
    sendResponse(id, result) {
        const response = {
            jsonrpc: '2.0',
            id: id,
            result: result
        };
        
        // Only write JSON to stdout for MCP protocol
        process.stdout.write(JSON.stringify(response) + '\n');
    }

    /**
     * Send error
     */
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
    const server = new SimpleMCPServerFixed();
    server.start();
    
    // Handle shutdown
    process.on('SIGINT', () => {
        console.error('\n🛑 Shutting down MCP Server...');
        process.exit(0);
    });
}

module.exports = SimpleMCPServerFixed;
