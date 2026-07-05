#!/usr/bin/env node

/**
 * Minimal MCP Server for Testing
 * Focus on proper MCP protocol communication only
 */

class MinimalMCPServer {
    constructor() {
        this.isRunning = false;
    }

    async start() {
        this.isRunning = true;
        this.listenForRequests();
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

    async handleToolCall(request) {
        const { name, arguments: args } = request.params;
        
        try {
            let result;
            
            switch (name) {
                case 'qoder_enhance':
                    result = {
                        success: true,
                        enhanced_code: '// Enhanced by QODER\n' + args.code + '\n// Enhanced',
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

    sendResponse(id, result) {
        const response = {
            jsonrpc: '2.0',
            id: id,
            result: result
        };
        
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
        
        process.stdout.write(JSON.stringify(response) + '\n');
    }
}

// Start server when run directly
if (require.main === module) {
    const server = new MinimalMCPServer();
    server.start();
    
    process.on('SIGINT', () => {
        process.exit(0);
    });
}

module.exports = MinimalMCPServer;
