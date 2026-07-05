# QODER + OpenClaw MCP Integration for Windsurf

A powerful Model Context Protocol (MCP) server that integrates QODER and OpenClaw capabilities directly into Windsurf, providing AI-powered development tools, automation, and multi-platform communication features.

## 🚀 Features

### QODER Features
- **AI Code Enhancement**: Intelligent code improvement and suggestions
- **Security Monitoring**: Real-time security analysis and vulnerability scanning
- **Workflow Assistance**: Automated workflow optimization and task management

### OpenClaw Features
- **Multi-Platform Communication**: WhatsApp, Telegram, Slack, Discord integration
- **AI Chat Assistant**: Advanced conversational AI capabilities
- **Automation Tools**: Task automation and scheduling
- **Skill Execution**: Dynamic skill-based AI operations

### Unified Interface
- **Global Access**: Auto-loaded and globally available interface
- **Dynamic Discovery**: Automatic skill discovery from external sources
- **Expanded Skills**: Comprehensive skill management system
- **Real-time Processing**: Streaming and block processing capabilities

## 📦 Installation

### Prerequisites
- Node.js >= 14.0.0
- Windsurf IDE with MCP support
- Git (for cloning)

### Quick Setup

1. **Clone or Download** the project to your desired location
2. **Run the setup script**:
   ```bash
   node setup.js
   ```
3. **Configure Windsurf MCP**:
   - Open Windsurf settings
   - Navigate to MCP configuration
   - Add the server configuration (see below)

### Manual Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Verify installation**:
   ```bash
   npm test
   ```

3. **Start the MCP server**:
   ```bash
   npm start
   ```

## ⚙️ Configuration

### MCP Server Configuration

Add this to your Windsurf MCP configuration (`mcp_config.json`):

```json
{
  "mcpServers": {
    "qoder-openclaw-simple": {
      "command": "node",
      "args": ["N:\\Windsurf\\simple-mcp-server.js"],
      "env": {
        "AUTO_ACCESSIBLE": "true",
        "NO_SDK_REQUIRED": "true",
        "OPENCLAW_SIMPLE_MODE": "true",
        "QODER_SIMPLE_MODE": "true"
      },
      "disabled": false
    }
  }
}
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Core Configuration
AUTO_ACCESSIBLE=true
NO_SDK_REQUIRED=true
OPENCLAW_SIMPLE_MODE=true
QODER_SIMPLE_MODE=true

# OpenClaw Settings
OPENCLAW_ROOT=./qoder-integration/openclaw
OPENCLAW_LOG_LEVEL=info
OPENCLAW_ENABLE_WEBHOOKS=true
OPENCLAW_ENABLE_AUTOMATION=true

# QODER Settings
QODER_AI_MODEL=default
QODER_ENHANCEMENT_MODE=balanced
QODER_SECURITY_SCAN=true
```

## 🎯 Usage

### Global Interface

Once loaded, the integration is available globally as `qoderOpenclaw`:

```javascript
// QODER functions
await qoderOpenclaw.qoder.enhance("your code here");
await qoderOpenclaw.qoder.monitor("content to analyze");
await qoderOpenclaw.qoder.assist("task description");

// OpenClaw functions
await qoderOpenclaw.openclaw.chat("message");
await qoderOpenclaw.openclaw.automate("task description");
await qoderOpenclaw.openclaw.skill("skill_name", input);

// Unified AI assistant
await qoderOpenclaw.ai.ask("your question");
await qoderOpenclaw.ai.help();
await qoderOpenclaw.ai.status();
```

### MCP Tools in Windsurf

The integration provides these MCP tools:

- `qoder_enhance`: AI code enhancement
- `qoder_monitor`: Security monitoring
- `openclaw_chat`: AI chat assistant
- `ai_ask`: Unified AI assistant

### Example Usage in Windsurf

1. **Code Enhancement**:
   - Use the `qoder_enhance` tool
   - Provide your code as input
   - Get enhanced code with suggestions

2. **Security Analysis**:
   - Use the `qoder_monitor` tool
   - Provide content to analyze
   - Receive security score and recommendations

3. **AI Assistance**:
   - Use the `ai_ask` tool for general questions
   - Use `openclaw_chat` for conversational AI
   - Automatic routing to appropriate handlers

## 🏗️ Project Structure

```
N:\Windsurf\
├── simple-mcp-server.js          # Main MCP server
├── windsurf-direct-integration.js # Core integration
├── expanded-skills-fixed.js       # Skills management
├── dynamic-skill-discovery.js     # Dynamic discovery
├── setup.js                       # Installation script
├── test-integration.js            # Test suite
├── package.json                   # Dependencies
├── README.md                      # This file
└── qoder-integration/
    └── openclaw/                  # OpenClaw platform
        ├── apps/                  # Application configurations
        ├── channels/              # Communication channels
        ├── config/                # Platform configuration
        ├── logs/                  # Log files
        ├── runtime/               # Runtime configurations
        ├── skills/                # Skill definitions
        ├── tools/                 # Tool configurations
        ├── channels.json          # Channel settings
        ├── skills.json            # Skill settings
        ├── tools.json             # Tool settings
        ├── core-platform.json     # Core platform config
        └── runtime.json           # Runtime settings
```

## 🔧 Development

### Running Tests

```bash
# Run full test suite
npm test

# Run specific test categories
node test-integration.js
```

### Development Mode

```bash
# Start with auto-reload
npm run dev

# Or use nodemon
npx nodemon simple-mcp-server.js
```

### Adding New Features

1. **New MCP Tools**: Add to `simple-mcp-server.js` in the `tools/list` method
2. **New Integration Features**: Add to `windsurf-direct-integration.js` in `setupFeatures()`
3. **New OpenClaw Capabilities**: Configure in `qoder-integration/openclaw/` directory

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Not Starting**:
   - Check Node.js version (>= 14.0.0)
   - Verify all dependencies are installed
   - Run `npm test` to check installation

2. **Tools Not Available in Windsurf**:
   - Verify MCP configuration is correct
   - Check environment variables
   - Restart Windsurf after configuration changes

3. **OpenClaw Features Not Working**:
   - Verify OpenClaw directory structure
   - Check configuration files in `qoder-integration/openclaw/`
   - Run setup script to reinitialize

### Debug Mode

Enable debug logging by setting:
```env
OPENCLAW_LOG_LEVEL=debug
```

### Getting Help

1. Run the doctor script:
   ```bash
   npm run doctor
   ```

2. Check the test results:
   ```bash
   npm test
   ```

3. Review logs in the `qoder-integration/openclaw/logs/` directory

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the README and inline comments
- **Community**: Join our Discord/Slack for community support

---

**QODER + OpenClaw MCP Integration** - Empowering Windsurf with AI-driven development and automation capabilities.
