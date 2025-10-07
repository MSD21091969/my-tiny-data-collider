# Develop Branch AI Collaboration Guide

*Last updated: October 7, 2025*

This document outlines AI collaboration practices and guidelines specific to the **develop** branch.

## 📋 Branch Overview

### Purpose
The develop branch serves as the main integration branch for ongoing development work. It contains the latest stable development code and is used for:

- Feature development and integration
- Bug fixes and improvements
- Documentation updates
- Tool generation and configuration
- Quality assurance and testing

### Target Audience
- Core development team members
- Contributors working on new features
- QA engineers validating changes
- Technical writers updating documentation

### Timeline
- **Continuous**: Ongoing development with regular merges to main
- **Release Cycle**: Bi-weekly releases from develop to main
- **Hotfixes**: Emergency fixes bypass develop when necessary

## 🤖 AI Collaboration Guidelines

### Applicable AI Practices
- [x] Code generation for new services and tools
- [x] Documentation updates for API changes
- [x] Testing assistance for unit and integration tests
- [x] Debugging support for development issues
- [x] Refactoring existing codebase components
- [x] Architecture planning and design reviews

### Branch-Specific Constraints
- **Technology Stack**: Python 3.11+, Pydantic, FastAPI, Firebase
- **Architecture Patterns**: Service-Repository pattern, Tool decorators
- **Quality Standards**: 80%+ test coverage, pylint score >8.0
- **Security Requirements**: Input validation, authentication checks

### Prohibited AI Uses
- Security-sensitive authentication code
- Production deployment configurations
- Legal or compliance documentation
- Financial calculation logic (requires manual review)

## 📝 Recommended Prompts

### Primary Templates
1. **Service Generation** - For creating new microservices
   - Location: `docs/ai-collaboration/prompts/code-generation/service.md`
   - Use case: New API endpoints, business logic services

2. **Tool Configuration** - For YAML tool definitions
   - Location: `docs/ai-collaboration/prompts/code-generation/tool-yaml.md`
   - Use case: Creating new tool configurations

3. **Test Generation** - For comprehensive test suites
   - Location: `docs/ai-collaboration/prompts/testing/comprehensive.md`
   - Use case: Unit tests, integration tests, edge cases

### Custom Branch Prompts
**Documentation Updates**: When API signatures change
```
Generate documentation updates for the following API changes:

Context: Python FastAPI service with Pydantic models
Changes: [List specific changes]
Requirements: Update method docs, API reference, examples
Standards: Follow existing documentation patterns
```

## 🔍 Quality Assurance

### Review Requirements
- **Mandatory Reviews**: All AI-generated code requires senior developer review
- **Review Criteria**: Functionality, security, performance, maintainability
- **Approval Process**: PR review with at least 2 approvals for AI contributions

### Testing Standards
- **Test Coverage**: Minimum 85% coverage for new AI-generated code
- **Test Types**: Unit, integration, and end-to-end tests required
- **Performance Benchmarks**: Response time <200ms for API endpoints

### Documentation Updates
- **README Updates**: Update all affected README.md files with dates
- **API Documentation**: Update method docs and registry documentation
- **User Guides**: Update usage examples and integration guides

## 📊 Success Metrics

### Quality Metrics
- **Code Review Pass Rate**: Target 90% first-pass acceptance
- **Test Coverage**: Minimum 85% overall coverage maintained
- **Bug Rate**: <5 bugs per 1000 lines of AI-generated code
- **Performance**: Meet established API response time benchmarks

### Process Metrics
- **AI Usage Rate**: 60-70% of development tasks use AI assistance
- **Review Turnaround**: Maximum 4 hours for standard reviews
- **Integration Success**: 95% successful CI/CD pipeline runs

## 🚨 Risk Mitigation

### Branch-Specific Risks
- Integration conflicts from multiple feature branches
- Performance regressions in core services
- Security vulnerabilities in new API endpoints
- Breaking changes to existing tool configurations

### Mitigation Strategies
- Regular integration testing and conflict resolution
- Performance monitoring and benchmarking
- Security code reviews for all API changes
- Backward compatibility testing for tool updates

## 📞 Support and Resources

### Getting Help
- **Team Contacts**: Development team lead for AI collaboration questions
- **Documentation**: Main AI collaboration guide and prompt templates
- **Examples**: Recent successful AI collaborations in PR history

### Escalation Process
- Contact development team lead for urgent AI quality issues
- Escalate to architecture team for design or security concerns
- Use GitHub issues for tracking AI collaboration improvements

## 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-07 | Initial develop branch guide created | AI Collaboration Team |

---

**Note**: This guide applies to all feature branches created from develop. Feature branches should reference this guide and note any specific variations in their own branch guides.

## 🔗 Related Documentation

- [Main AI Collaboration Guide](../README.md)
- [Conversation Practices](../practices/conversation-practices.md)
- [Quality Assurance](quality-assurance.md)
- [Tool Generation Workflow](../../../TOOL_GENERATION_WORKFLOW.md)