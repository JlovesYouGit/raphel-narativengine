/**
 * Simple MCP Server - No SDK Dependencies
 * Basic MCP server for QODER + OpenClaw integration
 */

const WindsurfDirectIntegration = require('./windsurf-direct-integration');

class SimpleMCPServer {
    constructor() {
        this.integration = null;
        this.isRunning = false;
    }

    /**
     * Start MCP server
     */
    async start() {
        // Log to stderr to avoid interfering with MCP protocol
        console.error('🚀 Starting Simple MCP Server...');
        
        try {
            // Initialize integration
            this.integration = new WindsurfDirectIntegration();
            await this.integration.initialize();
            
            // Start listening for stdin
            this.isRunning = true;
            this.listenForRequests();
            
            console.error('✅ Simple MCP Server running');
            
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
            
            if (request.method === 'tools/list') {
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
                case 'ai_ask':
                    result = await this.integration.askAI(args.query);
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
        
        process.stdout.write(JSON.stringify(response) + '\\n');
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
        
        process.stdout.write(JSON.stringify(response) + '\\n');
    }
}

// Start server when run directly
if (require.main === module) {
    const server = new SimpleMCPServer();
    server.start();
    
    // Handle shutdown
    process.on('SIGINT', () => {
        console.log('\\n🛑 Shutting down MCP Server...');
        process.exit(0);
    });
}

module.exports = SimpleMCPServer;
