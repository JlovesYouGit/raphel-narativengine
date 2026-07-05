/**
 * Windsurf Unified MCP - Safe Version
 * Safe MCP server for QODER integration
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { initializeQODERIntegration, getQODERStatus } = require('./qoder-app-process');

const server = new Server(
    {
        name: 'qoder-freeruner',
        version: '1.0.0',
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// Register safe tools
server.setRequestHandler('tools/list', async () => {
    return {
        tools: [
            {
                name: 'get_qoder_status',
                description: 'Get QODER integration status',
                inputSchema: { type: 'object', properties: {} }
            },
            {
                name: 'execute_safe_operation',
                description: 'Execute safe QODER operation',
                inputSchema: {
                    type: 'object',
                    properties: {
                        operation: { type: 'string' },
                        parameters: { type: 'object' }
                    },
                    required: ['operation']
                }
            },
            {
                name: 'get_openclaw_status',
                description: 'Get OpenClaw integration status',
                inputSchema: { type: 'object', properties: {} }
            },
            {
                name: 'execute_openclaw_operation',
                description: 'Execute OpenClaw operation (channels, tools, skills)',
                inputSchema: {
                    type: 'object',
                    properties: {
                        operation: { type: 'string' },
                        parameters: { type: 'object' }
                    },
                    required: ['operation']
                }
            },
            {
                name: 'get_available_features',
                description: 'Get all available QODER + OpenClaw features',
                inputSchema: { type: 'object', properties: {} }
            }
        ]
    };
});

server.setRequestHandler('tools/call', async (request) => {
    const { name, arguments: args } = request.params;
    
    try {
        switch (name) {
            case 'get_qoder_status':
                return { content: [{ type: 'text', text: JSON.stringify(getQODERStatus(), null, 2) }] };
                
            case 'execute_safe_operation':
                const { executeWithQODER } = require('./qoder-app-process');
                const result = await executeWithQODER(args.operation, args.parameters);
                return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
                
            case 'get_openclaw_status':
                const { getQODERStatus } = require('./qoder-app-process');
                const qoderStatus = getQODERStatus();
                const openclawStatus = qoderStatus.openclaw_integration || { status: 'not_available' };
                return { content: [{ type: 'text', text: JSON.stringify(openclawStatus, null, 2) }] };
                
            case 'execute_openclaw_operation':
                const { executeWithQODER: executeQODERWithOpenClaw } = require('./qoder-app-process');
                const openclawResult = await executeQODERWithOpenClaw(args.operation, args.parameters);
                return { content: [{ type: 'text', text: JSON.stringify(openclawResult, null, 2) }] };
                
            case 'get_available_features':
                const SafeQODERIntegration = require('./safe-qoder-integration');
                const integration = new SafeQODERIntegration();
                const features = integration.getAvailableFeatures();
                return { content: [{ type: 'text', text: JSON.stringify(features, null, 2) }] };
                
            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    } catch (error) {
        return { 
            content: [{ 
                type: 'text', 
                text: JSON.stringify({ 
                    success: false, 
                    error: error.message 
                }, null, 2) 
            }] 
        };
    }
});

async function main() {
    try {
        // Initialize QODER first
        await initializeQODERIntegration();
        
        const transport = new StdioServerTransport();
        await server.connect(transport);
        console.error('QODER MCP Server running safely');
    } catch (error) {
        console.error('QODER MCP Server startup error:', error);
    }
}

main().catch(console.error);
