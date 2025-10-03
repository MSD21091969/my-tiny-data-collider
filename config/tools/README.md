# Tool Organization Structure

This directory contains all tool definitions organized by domain and capability.

## Directory Structure

```
tools/
├── communication/              # Communication and messaging tools
│   └── email/                  # Email-related tools
│       ├── gmail_get_message.yaml
│       ├── gmail_list_messages.yaml
│       ├── gmail_search_messages.yaml
│       └── gmail_send_message.yaml
│
├── workspace/                  # Workspace and productivity tools
│   └── google/                 # Google Workspace tools
│       ├── drive_list_files.yaml
│       └── sheets_batch_get.yaml
│
├── automation/                 # Automation and orchestration tools
│   └── pipelines/              # Multi-step workflows
│       ├── gmail_to_drive_pipeline.yaml
│       └── multi_echo_pipeline.yaml
│
└── utilities/                  # Development and debugging tools
    └── debugging/              # Debug and testing tools
        ├── echo_tool.yaml
        └── echo_chain_demo.yaml
```

## Classification System

### Primary Domains
- **communication/**: Tools for messaging, notifications, and communication
- **workspace/**: Productivity tools for documents, spreadsheets, and collaboration
- **automation/**: Orchestration, pipelines, and complex workflows
- **utilities/**: Development, debugging, and system tools

### Capabilities
- **create**: Tools that create new resources
- **read**: Tools that fetch or query data
- **update**: Tools that modify existing resources
- **delete**: Tools that remove resources
- **process**: Tools that transform or manipulate data

### Maturity Levels
- **experimental**: Alpha stage, may change significantly
- **beta**: Feature-complete, undergoing testing
- **stable**: Production-ready, fully tested
- **deprecated**: Being phased out

## Tool Naming Convention

Tools follow the pattern: `{service}_{action}_{resource}.yaml`

Examples:
- `gmail_send_message.yaml` - Gmail service, send action, message resource
- `drive_list_files.yaml` - Drive service, list action, files resource
- `sheets_batch_get.yaml` - Sheets service, batch get action