# Prompt Templates

*Last updated: October 8, 2025 at 19:30*

Reusable prompt templates for consistent AI collaboration in my-tiny-data-collider repository.

## 📁 Template Categories

| Category | Purpose | Location |
|----------|---------|----------|
| **Code Generation** | Creating new code components | [code-generation/](./code-generation/) |
| **Tool Engineering** | YAML tool definitions and generation | [code-generation/](./code-generation/) |
| **DTO Design** | Request-Response DTO patterns | [code-generation/](./code-generation/) |
| **Code Review** | Reviewing and improving code | [code-review/](./code-review/) |
| **Documentation** | Writing and updating docs | [documentation/](./documentation/) |
| **Debugging** | Troubleshooting issues | [debugging/](./debugging/) |
| **Refactoring** | Code improvement and restructuring | [refactoring/](./refactoring/) |
| **Testing** | Test creation and validation | [testing/](./testing/) |
| **Architecture** | System design and planning | [architecture/](./architecture/) |

## 🎯 Template Standards

### Required Elements
All templates must include:
- **Context Section**: Project background and constraints
- **Task Definition**: Clear, specific objectives
- **Quality Standards**: Acceptance criteria and requirements
- **Output Format**: Expected response structure
- **Validation Steps**: How to verify the result

### Naming Convention
```
{category}-{action}-{scope}.md
```
Examples:
- `code-generation-api-endpoint.md`
- `documentation-api-reference.md`
- `debugging-performance-issue.md`

## 🚀 Quick Reference

### Most Used Templates
1. [Code Generation Template](./code-generation/general.md)
2. [Tool YAML Definition](./code-generation/tool-yaml-template.md) - NEW
3. [DTO Pattern Template](./code-generation/dto-pattern-template.md) - NEW
4. [Bug Fix Template](./debugging/bug-fix.md)
5. [Documentation Update](./documentation/update.md)
6. [Test Creation](./testing/unit-test.md)

### Repository-Specific Templates
- **Tool Engineering**: YAML tool definitions with parameter inheritance
- **Method Integration**: Connecting DTOs to service methods
- **Composite Tools**: Multi-step workflow orchestration
- **R-A-R Validation**: Request-Action-Response pattern compliance

### VS Code Integration
Templates are designed to work with:
- **GitHub Copilot**: Inline suggestions and completions
- **VS Code Prompts**: Custom prompt files in `.vscode/prompts/`
- **Extensions**: AI assistance tools and chat interfaces

## 📝 Template Usage Guidelines

### Before Using Templates
1. **Assess Complexity**: Choose appropriate template for task scope
2. **Gather Context**: Collect relevant code, requirements, and constraints
3. **Set Expectations**: Define success criteria and validation steps

### During AI Interaction
1. **Provide Context**: Share project structure, existing patterns, and constraints
2. **Be Specific**: Use concrete examples and avoid ambiguous requirements
3. **Iterate**: Request clarification and provide feedback on outputs
4. **Validate**: Test and review all AI-generated content

### After Completion
1. **Review**: Perform thorough code review of AI-generated content
2. **Test**: Validate functionality and integration
3. **Document**: Record successful patterns and lessons learned
4. **Update**: Refine templates based on outcomes

## 🔧 Customization

### Adapting Templates
- **Project-Specific**: Add repository context and standards
- **Team Preferences**: Include team-specific coding styles and patterns
- **Technology Stack**: Reference specific frameworks and tools used
- **Quality Gates**: Define project-specific validation requirements

### Creating New Templates
1. **Identify Need**: Document recurring patterns or challenges
2. **Gather Examples**: Collect successful instances of the pattern
3. **Standardize**: Create consistent structure and format
4. **Test**: Validate template effectiveness with team members
5. **Document**: Add usage guidelines and examples

## 📊 Template Metrics

### Effectiveness Tracking
- **Success Rate**: Percentage of template uses that meet quality standards
- **Time Savings**: Average time reduction compared to manual approaches
- **Error Reduction**: Decrease in bugs or issues in AI-generated code
- **Adoption Rate**: Percentage of team members using templates regularly

### Continuous Improvement
- **Feedback Collection**: Regular surveys and retrospective reviews
- **Template Updates**: Version control and improvement tracking
- **Best Practice Sharing**: Cross-team template exchange and adaptation
- **Tool Integration**: Updates based on new AI tool capabilities

## 🔗 Related Resources

- [Conversation Practices](../practices/conversation-practices.md)
- [Quality Assurance](../workflows/quality-assurance.md)
- [VS Code Setup](../practices/vscode-setup.md)
- [Template Examples](../examples/README.md)
- [HANDOVER Document](../../HANDOVER.md)
- [Copilot Instructions](../../.github/copilot-instructions.md)