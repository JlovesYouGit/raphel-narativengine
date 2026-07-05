#!/usr/bin/env node

const { spawn } = require('child_process');

console.log('🧪 Simple MCP Server Test...');

const server = spawn('node', ['mcp-server-robust.js'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: __dirname
});

let output = '';

server.stdout.on('data', (data) => {
    const response = data.toString();
    output += response;
    console.log('📥 Response:', response.trim());
});

server.stderr.on('data', (data) => {
    console.error('❌ Error:', data.toString());
});

server.on('error', (error) => {
    console.error('❌ Server error:', error);
});

// Wait a moment for server to start
setTimeout(() => {
    console.log('📤 Sending initialize request...');
    
    const initRequest = {
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
            protocolVersion: '2024-11-05',
            capabilities: { tools: {} },
            clientInfo: { name: 'test', version: '1.0.0' }
        }
    };
    
    server.stdin.write(JSON.stringify(initRequest) + '\n');
    
    // Wait for response
    setTimeout(() => {
        console.log('📤 Sending tools/list request...');
        
        const toolsRequest = {
            jsonrpc: '2.0',
            id: 2,
            method: 'tools/list'
        };
        
        server.stdin.write(JSON.stringify(toolsRequest) + '\n');
        
        // Wait and close
        setTimeout(() => {
            server.kill();
            console.log('\n🏁 Test complete');
            console.log('Total output:', output.length, 'characters');
        }, 2000);
    }, 1000);
}, 1000);
