# VS Code AI Integration Setup

*Last updated: October 7, 2025*

Comprehensive guide for configuring VS Code for effective AI-assisted development in this repository.

## 🎯 Overview

This document outlines the recommended VS Code configuration, extensions, and workflows for AI collaboration in the my-tiny-data-collider repository.

## 📦 Recommended Extensions

### Core AI Assistance
```json
{
  "recommendations": [
    "GitHub.copilot",
    "GitHub.copilot-chat",
    "ms-windows-ai-studio.windows-ai-studio",
    "ms-windows-ai-studio.windows-ai-studio-preview"
  ]
}
```

### Development Tools
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-vscode.vscode-markdown",
    "gruntfuggly.todo-tree"
  ]
}
```

### AI Enhancement
```json
{
  "recommendations": [
    "VisualStudioExcellence.CodeStream",
    "streetsidesoftware.code-spell-checker",
    "ms-vscode.vscode-github-issue-notebooks",
    "GitHub.vscode-pull-request-github"
  ]
}
```

## ⚙️ Workspace Settings

### Core Configuration
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.associations": {
    "*.md": "markdown",
    "*.yaml": "yaml",
    "*.yml": "yaml"
  },
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "markdown": true
  }
}
```

### AI-Specific Settings
```json
{
  "github.copilot.advanced": {
    "debug.overrideEngine": "nodejs",
    "debug.testOverrideProxyUrl": "http://localhost:3000",
    "debug.overrideCapiUrl": "https://api.githubcopilot.com"
  },
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "github.copilot.chat.experimental.codeFeedback": true
}
```

## 📁 Prompt Files Organization

### Directory Structure
```
.vscode/
├── prompts/                    # Custom prompt files
│   ├── code-generation.md     # Code creation prompts
│   ├── debugging.md           # Debugging assistance
│   ├── refactoring.md         # Code improvement
│   ├── documentation.md       # Documentation help
│   └── testing.md             # Test creation
├── settings.json              # Workspace settings
└── tasks.json                 # Build tasks
```

### Prompt File Format
Each prompt file should follow this structure:
```markdown
# Prompt Title

## Context
[Repository and project context]

## Task Types
- [Specific task category]
- [Another task type]

## Guidelines
- [Key instructions]
- [Best practices]

## Examples
[Concrete examples with expected outputs]
```

## 🚀 Workflow Integration

### Development Workflow
1. **Planning**: Use AI chat for task breakdown and planning
2. **Implementation**: Leverage Copilot for code suggestions
3. **Review**: AI-assisted code review and improvement
4. **Testing**: Generate and validate test cases
5. **Documentation**: AI help with documentation writing

### Keyboard Shortcuts
```json
{
  "key": "ctrl+shift+c",
  "command": "github.copilot.generate",
  "when": "editorTextFocus"
},
{
  "key": "ctrl+shift+v",
  "command": "github.copilot.chat.open",
  "when": "editorTextFocus"
},
{
  "key": "ctrl+shift+r",
  "command": "github.copilot.explain",
  "when": "editorTextFocus"
}
```

## 💬 Copilot Chat Integration

### Chat Participants
- **@workspace**: Search and understand codebase
- **@terminal**: Run commands and see output
- **@vscode**: VS Code API and extension development

### Custom Instructions
Create `.github/copilot-instructions.md`:
```markdown
# Copilot Instructions for my-tiny-data-collider

## Project Context
This is a Python-based data processing and AI integration platform using:
- Pydantic for data validation
- FastAPI for web services
- Firebase/Firestore for persistence
- Tool-based architecture for AI integration

## Code Standards
- Use async/await for service methods
- Follow Pydantic model patterns
- Include comprehensive error handling
- Write descriptive docstrings
- Use type hints throughout

## Architecture Patterns
- Service-Repository pattern for data access
- Tool decorator pattern for AI integration
- Request-Response DTOs for API communication
- Factory pattern for tool generation

## Quality Requirements
- All code must include unit tests
- Documentation must be updated with code changes
- Security considerations for all user-facing features
- Performance optimization for data processing operations
```

## 🔧 Task Automation

### Tasks Configuration
Create `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate Tools",
      "type": "shell",
      "command": "python",
      "args": ["scripts/generate_tools.py"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "python",
      "args": ["-m", "pytest"],
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
```

## 📊 Performance Optimization

### Memory Management
```json
{
  "github.copilot.editor.enableAutoCompletions": true,
  "github.copilot.chat.experimental.codeFeedback": false,
  "editor.suggest.showInlineDetails": false,
  "editor.quickSuggestions": {
    "other": "on",
    "comments": "off",
    "strings": "off"
  }
}
```

### Response Time Optimization
- Limit large file analysis
- Use specific file references
- Break complex requests into smaller tasks
- Cache frequent operations

## 🔒 Security Considerations

### API Key Management
- Never commit API keys to version control
- Use VS Code secrets management
- Environment-specific configuration
- Regular key rotation

### Code Security
- Enable security-focused extensions
- Regular dependency scanning
- CodeQL integration for vulnerability detection
- AI-assisted security review

## 📈 Monitoring and Analytics

### Usage Tracking
- Monitor Copilot usage patterns
- Track successful vs unsuccessful interactions
- Measure time savings and productivity gains
- Collect feedback on AI assistance quality

### Quality Metrics
- Code review pass rates for AI-generated code
- Bug rates in AI-assisted development
- Documentation completeness
- Test coverage maintenance

## 🔄 Updates and Maintenance

### Regular Updates
- Keep VS Code and extensions current
- Review and update prompt files quarterly
- Assess new AI tools and integrations
- Update documentation with new features

### Team Synchronization
- Share successful prompt templates
- Document effective workflows
- Maintain consistent configurations
- Regular team knowledge sharing

## 📚 Related Resources

- [Conversation Practices](./conversation-practices.md)
- [Prompt Templates](../prompts/README.md)
- [Quality Assurance](../workflows/quality-assurance.md)
- [VS Code Documentation](https://code.visualstudio.com/docs)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)