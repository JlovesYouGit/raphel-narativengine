#!/usr/bin/env node

/**
 * Agent-97 Enhanced QODER_FREERUNNER Startup Script
 * 
 * This script starts the QODER_FREERUNNER with Agent-97 enhancements
 * including linear flow calculations, MCP flow logic, and harsh data path handling.
 */

const Agent97EnhancedQoder = require('./agent97-enhanced-qoder');
const LinearFlowCalculationSystem = require('./linear-flow-calculation-system');
const MCPFlowLogic = require('./mcp-flow-logic');

async function startEnhancedQoder() {
  try {
    console.log('Starting Agent-97 Enhanced QODER_FREERUNNER...');
    
    // Initialize enhanced QODER
    const enhancedQoder = new Agent97EnhancedQoder();
    await enhancedQoder.initialize();
    
    // Initialize linear flow system
    const linearFlowSystem = new LinearFlowCalculationSystem();
    
    // Initialize MCP flow logic
    const mcpFlowLogic = new MCPFlowLogic();
    
    // Start the server
    await enhancedQoder.start();
    
    console.log('Agent-97 Enhanced QODER_FREERUNNER started successfully!');
    console.log('Health check: http://localhost:3174/health');
    console.log('Linear Flow System: Active');
    console.log('MCP Flow Logic: Active');
    console.log('Harsh Data Path Handling: Active');
    console.log('Exion 5nm Precision: Active');
    console.log('Formula Truncation Detection: Active');
    
    // Graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\nShutting down Agent-97 Enhanced QODER_FREERUNNER...');
      await enhancedQoder.stop();
      process.exit(0);
    });
    
  } catch (error) {
    console.error('Failed to start Agent-97 Enhanced QODER_FREERUNNER:', error);
    process.exit(1);
  }
}

// Start the enhanced system
startEnhancedQoder();
