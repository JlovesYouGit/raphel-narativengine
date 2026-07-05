
// Global QODER + OpenClaw Interface
(function() {
    const integration = require('./windsurf-direct-integration');
    let instance = null;
    
    async function getInstance() {
        if (!instance) {
            instance = new integration();
            await instance.initialize();
        }
        return instance;
    }
    
    // Global interface
    const globalInterface = {
        // QODER methods
        qoder: {
            enhance: async (code) => {
                const inst = await getInstance();
                return await inst.execute('qoder.enhance', { code });
            },
            monitor: async (content) => {
                const inst = await getInstance();
                return await inst.execute('qoder.monitor', { content });
            },
            assist: async (task) => {
                const inst = await getInstance();
                return await inst.execute('qoder.assist', { task });
            }
        },
        
        // OpenClaw methods
        openclaw: {
            chat: async (message) => {
                const inst = await getInstance();
                return await inst.execute('openclaw.chat', { message });
            },
            automate: async (task) => {
                const inst = await getInstance();
                return await inst.execute('openclaw.automate', { task });
            },
            skill: async (skillName, input) => {
                const inst = await getInstance();
                return await inst.execute('openclaw.skill', { skill: skillName, input });
            }
        },
        
        // Unified AI assistant
        ai: {
            ask: async (query) => {
                const inst = await getInstance();
                return await inst.askAI(query);
            },
            help: async () => {
                const inst = await getInstance();
                return await inst.getHelp();
            },
            status: async () => {
                const inst = await getInstance();
                return await inst.getStatus();
            },
            skills: async () => {
                const inst = await getInstance();
                return inst.skillsIntegration ? inst.skillsIntegration.getAvailableSkills() : {};
            },
            searchSkills: async (query) => {
                const inst = await getInstance();
                return inst.skillsIntegration ? inst.skillsIntegration.searchSkills(query) : [];
            },
            discoverSkills: async (query) => {
                const inst = await getInstance();
                return inst.dynamicDiscovery ? await inst.dynamicDiscovery.discoverSkillsFromQuery(query) : { success: false };
            },
            getDiscoveredSkills: async () => {
                const inst = await getInstance();
                return inst.dynamicDiscovery ? inst.dynamicDiscovery.getDiscoveredSkills() : {};
            },
            searchDiscoveredSkills: async (query) => {
                const inst = await getInstance();
                return inst.dynamicDiscovery ? inst.dynamicDiscovery.searchDiscoveredSkills(query) : [];
            }
        }
    };
    
    // Make globally available
    if (typeof global !== 'undefined') {
        global.qoderOpenclaw = globalInterface;
    }
    
    if (typeof window !== 'undefined') {
        window.qoderOpenclaw = globalInterface;
    }
    
    // Auto-initialize
    getInstance().then(() => {
        console.log('🚀 QODER + OpenClaw interface globally available');
    });
})();
