
// Auto-load QODER + OpenClaw integration
console.log('🚀 Loading QODER + OpenClaw integration...');

try {
    require('./global-interface.js');
    console.log('✅ Integration loaded successfully');
    console.log('🎯 Available globally as: qoderOpenclaw');
    console.log('💡 Try: qoderOpenclaw.ai.ask("help me code")');
} catch (error) {
    console.error('❌ Failed to load integration:', error.message);
}
