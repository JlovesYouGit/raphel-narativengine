
/**
 * Safe Logger - Non-Intrusive
 * Logs without interfering with Windsurf
 */

class SafeLogger {
    constructor(logPath) {
        this.logPath = logPath;
        this.maxLogSize = 10 * 1024 * 1024; // 10MB
    }

    /**
     * Log message safely
     */
    log(level, message, data = null) {
        try {
            const logEntry = {
                timestamp: new Date().toISOString(),
                level,
                message: this.sanitizeMessage(message),
                ...(data && { data: this.sanitizeData(data) })
            };

            const logLine = JSON.stringify(logEntry) + '\n';
            fs.appendFileSync(this.logPath, logLine);

            // Rotate log if too large
            this.rotateLogIfNeeded();
        } catch (error) {
            // Fail silently to prevent crashes
            console.error('Log error (safe fallback):', error);
        }
    }

    /**
     * Sanitize message
     */
    sanitizeMessage(message) {
        if (typeof message !== 'string') {
            message = String(message);
        }
        return message.substring(0, 1000); // Limit length
    }

    /**
     * Sanitize data
     */
    sanitizeData(data) {
        if (!data || typeof data !== 'object') {
            return data;
        }

        const sanitized = {};
        for (const [key, value] of Object.entries(data)) {
            if (typeof value === 'string' && value.length > 500) {
                sanitized[key] = value.substring(0, 500) + '...';
            } else {
                sanitized[key] = value;
            }
        }
        return sanitized;
    }

    /**
     * Rotate log if needed
     */
    rotateLogIfNeeded() {
        try {
            const stats = fs.statSync(this.logPath);
            if (stats.size > this.maxLogSize) {
                const backupPath = this.logPath + '.backup';
                fs.renameSync(this.logPath, backupPath);
            }
        } catch (error) {
            // Fail silently
        }
    }
}

module.exports = SafeLogger;
