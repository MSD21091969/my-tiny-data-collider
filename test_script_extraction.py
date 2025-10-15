#!/usr/bin/env python3
"""Test if generate_method_tools.py extraction functions work."""

import sys
sys.path.insert(0, 'scripts')

from generate_method_tools import import_request_model, extract_tool_parameters

# Test Gmail model
model = import_request_model(
    'src.pydantic_ai_integration.integrations.google_workspace.models',
    'GmailListMessagesRequest'
)

print(f"Model imported: {model}")
print(f"Model has payload field: {'payload' in model.model_fields if model else 'N/A'}")

if model:
    params = extract_tool_parameters(model)
    print(f"\nParameters extracted: {len(params)}")
    for p in params:
        print(f"  - {p['name']}: {p['type']} (required={p['required']})")
else:
    print("Model import failed!")
