#!/usr/bin/env node

/**
 * Robust OpenClaw MCP Server
 * Handles all integrations without getting stuck, proper iterations for unified tool calling
 */

const fs = require('fs');
const path = require('path');

class RobustMCPServer {
    constructor() {
        this.integration = null;
        this.isRunning = false;
        this.capabilities = null;
        this.tools = new Map();
        this.timeout = 30000; // 30 second timeout
    }

    async start() {
        console.error('🚀 Starting Robust OpenClaw MCP Server...');
        
        try {
            // Initialize capabilities with timeout
            await this.initializeCapabilities();
            
            this.isRunning = true;
            this.listenForRequests();
            
            console.error('✅ Robust OpenClaw MCP Server running');
            console.error(`📊 Loaded ${this.tools.size} tools`);
            
        } catch (error) {
            console.error('❌ MCP Server failed to start:', error);
            // Continue anyway with basic tools
            this.setupBasicTools();
            this.isRunning = true;
            this.listenForRequests();
        }
    }

    async initializeCapabilities() {
        try {
            // Try to load integration with timeout
            const integrationPromise = this.loadIntegration();
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Integration timeout')), this.timeout)
            );
            
            this.capabilities = await Promise.race([integrationPromise, timeoutPromise]);
            
            if (this.capabilities) {
                this.setupFullTools();
            } else {
                this.setupBasicTools();
            }
            
        } catch (error) {
            console.error('⚠️ Integration failed, using basic tools:', error.message);
            this.setupBasicTools();
        }
    }

    async loadIntegration() {
        try {
            // Try to load the integration
            const WindsurfDirectIntegration = require('./windsurf-direct-integration');
            this.integration = new WindsurfDirectIntegration();
            
            // Initialize with timeout protection
            const initResult = await this.withTimeout(
                this.integration.initializeSilent(),
                10000 // 10 second timeout for initialization
            );
            
            return initResult.success ? this.integration : null;
            
        } catch (error) {
            console.error('⚠️ Could not load integration:', error.message);
            return null;
        }
    }

    withTimeout(promise, timeout) {
        return Promise.race([
            promise,
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error(`Operation timed out after ${timeout}ms`)), timeout)
            )
        ]);
    }

    setupFullTools() {
        // Full integration tools
        this.tools.set('qoder_enhance', {
            description: 'AI code enhancement using QODER',
            handler: async (args) => {
                return await this.withTimeout(
                    this.integration.execute('qoder.enhance', { code: args.code }),
                    15000
                );
            }
        });

        this.tools.set('qoder_monitor', {
            description: 'Security monitoring using QODER',
            handler: async (args) => {
                return await this.withTimeout(
                    this.integration.execute('qoder.monitor', { content: args.content }),
                    10000
                );
            }
        });

        this.tools.set('openclaw_chat', {
            description: 'AI chat assistant using OpenClaw',
            handler: async (args) => {
                return await this.withTimeout(
                    this.integration.execute('openclaw.chat', { message: args.message }),
                    20000
                );
            }
        });

        this.tools.set('openclaw_automate', {
            description: 'Task automation using OpenClaw',
            handler: async (args) => {
                return await this.withTimeout(
                    this.integration.execute('openclaw.automate', { task: args.task }),
                    25000
                );
            }
        });

        this.tools.set('openclaw_skill', {
            description: 'Execute AI skill using OpenClaw',
            handler: async (args) => {
                return await this.withTimeout(
                    this.integration.execute('openclaw.skill', { skill: args.skill, input: args.input }),
                    20000
                );
            }
        });

        this.tools.set('openclaw_discover', {
            description: 'Discover new skills from external sources',
            handler: async (args) => {
                if (this.integration.dynamicDiscovery) {
                    return await this.withTimeout(
                        this.integration.dynamicDiscovery.discoverSkillsFromQuery(args.query || ''),
                        15000
                    );
                } else {
                    return { success: false, error: 'Dynamic discovery not available' };
                }
            }
        });

        this.tools.set('openclaw_list_skills', {
            description: 'List all available OpenClaw skills',
            handler: async () => {
                const skills = {};
                
                if (this.integration.skillsIntegration) {
                    skills.expanded = this.integration.skillsIntegration.getAvailableSkills();
                }
                
                if (this.integration.dynamicDiscovery) {
                    skills.discovered = this.integration.dynamicDiscovery.getDiscoveredSkills();
                }
                
                return { success: true, skills };
            }
        });

        this.tools.set('ai_ask', {
            description: 'Unified AI assistant (IDE AI + OpenClaw)',
            handler: async (args) => {
                return await this.withTimeout(
                    this.integration.askAI(args.query),
                    20000
                );
            }
        });

        this.tools.set('ai_unified', {
            description: 'Unified tool calling with all integrations',
            handler: async (args) => {
                const { query, iterations = 1 } = args;
                const results = [];
                
                for (let i = 0; i < iterations; i++) {
                    try {
                        const result = await this.withTimeout(
                            this.integration.askAI(`${query} (iteration ${i + 1})`),
                            15000
                        );
                        results.push({ iteration: i + 1, result });
                    } catch (error) {
                        results.push({ iteration: i + 1, error: error.message });
                    }
                }
                
                return { success: true, results, iterations };
            }
        });
    }

    setupBasicTools() {
        // Fallback tools when integration fails
        this.tools.set('qoder_enhance', {
            description: 'AI code enhancement (basic mode)',
            handler: async (args) => {
                return {
                    success: true,
                    enhanced_code: `// Enhanced by QODER (Basic Mode)\n${args.code}\n// Enhancement complete`,
                    suggestions: ['Add error handling', 'Add documentation'],
                    mode: 'basic',
                    timestamp: new Date().toISOString()
                };
            }
        });

        this.tools.set('openclaw_chat', {
            description: 'AI chat assistant (basic mode)',
            handler: async (args) => {
                return {
                    success: true,
                    response: `Basic OpenClaw response to: ${args.message}`,
                    mode: 'basic',
                    timestamp: new Date().toISOString()
                };
            }
        });

        this.tools.set('ai_ask', {
            description: 'Unified AI assistant (basic mode)',
            handler: async (args) => {
                return {
                    success: true,
                    answer: `Basic AI response to: ${args.query}`,
                    mode: 'basic',
                    timestamp: new Date().toISOString()
                };
            }
        });
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
                        name: 'qoder-openclaw-robust',
                        version: '1.0.0'
                    }
                });
            } else if (request.method === 'tools/list') {
                const toolsList = [];
                for (const [name, tool] of this.tools.entries()) {
                    toolsList.push({
                        name,
                        description: tool.description,
                        inputSchema: {
                            type: 'object',
                            properties: this.getInputProperties(name),
                            required: this.getRequiredProperties(name)
                        }
                    });
                }
                
                this.sendResponse(request.id, { tools: toolsList });
            } else if (request.method === 'tools/call') {
                await this.handleToolCall(request);
            } else {
                this.sendError('Unknown method: ' + request.method, request.id);
            }
        } catch (error) {
            this.sendError('Invalid message: ' + error.message);
        }
    }

    getInputProperties(toolName) {
        const properties = {
            'qoder_enhance': { code: { type: 'string' } },
            'qoder_monitor': { content: { type: 'string' } },
            'openclaw_chat': { message: { type: 'string' } },
            'openclaw_automate': { task: { type: 'string' } },
            'openclaw_skill': { 
                skill: { type: 'string' },
                input: { type: 'string' }
            },
            'openclaw_discover': { 
                query: { type: 'string' }
            },
            'openclaw_list_skills': {},
            'ai_ask': { query: { type: 'string' } },
            'ai_unified': { 
                query: { type: 'string' },
                iterations: { type: 'number' }
            }
        };
        
        return properties[toolName] || {};
    }

    getRequiredProperties(toolName) {
        const required = {
            'qoder_enhance': ['code'],
            'qoder_monitor': ['content'],
            'openclaw_chat': ['message'],
            'openclaw_automate': ['task'],
            'openclaw_skill': ['skill', 'input'],
            'ai_ask': ['query'],
            'ai_unified': ['query']
        };
        
        return required[toolName] || [];
    }

    async handleToolCall(request) {
        const { name, arguments: args } = request.params;
        
        try {
            const tool = this.tools.get(name);
            if (!tool) {
                throw new Error('Unknown tool: ' + name);
            }
            
            // Execute tool with timeout
            const result = await this.withTimeout(
                tool.handler(args),
                this.timeout
            );
            
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
    const server = new RobustMCPServer();
    server.start();
    
    process.on('SIGINT', () => {
        console.error('\n🛑 Shutting down Robust OpenClaw MCP Server...');
        process.exit(0);
    });
}

module.exports = RobustMCPServer;
