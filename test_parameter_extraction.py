#!/usr/bin/env python3
"""Test parameter extraction from Google Workspace request models."""

from src.pydantic_ai_integration.integrations.google_workspace.models import (
    GmailListMessagesRequest,
    GmailGetMessageRequest,
    GmailSendMessageRequest,
    GmailSearchMessagesRequest,
    DriveListFilesRequest,
    SheetsBatchGetRequest,
)
from pydantic_ai_integration.method_registry import extract_parameters_from_request_model

def test_extraction(model_class, name):
    """Test parameter extraction for a request model."""
    params = extract_parameters_from_request_model(model_class)
    print(f"\n{name}:")
    print(f"  Model: {model_class.__name__}")
    print(f"  Parameters extracted: {len(params)}")
    for param in params:
        print(f"    - {param.name}: {param.param_type} (required={param.required})")
    return len(params)

# Test all Google Workspace request models
models = [
    (GmailListMessagesRequest, "GmailClient.list_messages"),
    (GmailGetMessageRequest, "GmailClient.get_message"),
    (GmailSendMessageRequest, "GmailClient.send_message"),
    (GmailSearchMessagesRequest, "GmailClient.search_messages"),
    (DriveListFilesRequest, "DriveClient.list_files"),
    (SheetsBatchGetRequest, "SheetsClient.batch_get"),
]

print("=" * 70)
print("PARAMETER EXTRACTION TEST - Google Workspace Models")
print("=" * 70)

total_params = 0
for model_class, name in models:
    count = test_extraction(model_class, name)
    total_params += count

print(f"\n{'='*70}")
print(f"TOTAL PARAMETERS EXTRACTED: {total_params}")
print(f"Expected: > 0 for each model (they all have required fields)")
print(f"{'='*70}\n")
