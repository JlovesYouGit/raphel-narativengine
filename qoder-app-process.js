/**
 * QODER App Process - Safe Version
 * Safe QODER integration for Windsurf
 */

const SafeQODERIntegration = require('./safe-qoder-integration');

let qoderIntegration = null;
let isInitialized = false;

/**
 * Initialize QODER integration safely
 */
async function initializeQODERIntegration() {
    try {
        if (!qoderIntegration) {
            qoderIntegration = new SafeQODERIntegration();
        }
        
        const result = await qoderIntegration.initializeSafeIntegration();
        isInitialized = result.success;
        
        return result;
    } catch (error) {
        console.error('QODER initialization failed safely:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Get QODER status
 */
function getQODERStatus() {
    if (!qoderIntegration || !isInitialized) {
        return {
            initialized: false,
            message: 'QODER not initialized',
            mode: 'safe'
        };
    }
    
    return qoderIntegration.getIntegrationStatus();
}

/**
 * Execute safe operation
 */
async function executeWithQODER(operation, context = {}) {
    if (!qoderIntegration || !isInitialized) {
        return { success: false, error: 'QODER not initialized' };
    }
    
    return await qoderIntegration.executeSafeOperation(operation, context);
}

module.exports = {
    initializeQODERIntegration,
    getQODERStatus,
    executeWithQODER
};

// Auto-initialize in safe mode
if (require.main === module) {
    initializeQODERIntegration()
        .then(result => {
            console.log('QODER Safe Mode:', result);
        })
        .catch(error => {
            console.error('QODER Safe Mode Error:', error);
        });
}
