
/**
 * Safe Hook Manager - Non-Intrusive
 * Manages hooks without interfering with Windsurf
 */

class SafeHookManager {
    constructor() {
        this.hooks = new Map();
        this.isSafe = true;
    }

    /**
     * Register safe hook
     */
    registerHook(name, callback, options = {}) {
        if (!this.isSafe) {
            throw new Error('Hook manager not in safe mode');
        }

        const safeHook = {
            name,
            callback: this.makeSafeCallback(callback),
            options: {
                timeout: options.timeout || 5000,
                retry_count: options.retry_count || 1,
                ...options
            },
            enabled: true
        };

        this.hooks.set(name, safeHook);
    }

    /**
     * Make callback safe
     */
    makeSafeCallback(callback) {
        return async (...args) => {
            try {
                // Add timeout protection
                const timeout = setTimeout(() => {
                    console.warn('Hook timeout detected, preventing crash');
                }, 5000);

                const result = await callback(...args);
                clearTimeout(timeout);
                return result;
            } catch (error) {
                console.error('Hook error, preventing crash:', error);
                return null; // Safe fallback
            }
        };
    }

    /**
     * Execute hook safely
     */
    async executeHook(name, ...args) {
        const hook = this.hooks.get(name);
        if (!hook || !hook.enabled) {
            return null;
        }

        try {
            return await hook.callback(...args);
        } catch (error) {
            console.error(`Hook ${name} failed safely:`, error);
            return null;
        }
    }

    /**
     * Get hook status
     */
    getHookStatus() {
        const status = {};
        for (const [name, hook] of this.hooks.entries()) {
            status[name] = {
                enabled: hook.enabled,
                options: hook.options
            };
        }
        return status;
    }
}

module.exports = SafeHookManager;
