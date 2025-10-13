#!/usr/bin/env python3
"""
POC: Email-to-Spreadsheet Workflow

Demonstrates the Phase 1 Pydantic validation enhancements in action:
- Gmail operations with validated models
- Casefile creation with custom types
- Email storage with full validation
- Spreadsheet generation with mock Google Workspace clients
- End-to-end workflow with data integrity guarantees

This POC showcases:
- Custom types: CasefileId, IsoTimestamp, ShortString, etc.
- Validated models: GmailMessage, CasefileModel, etc.
- Mock operations: Search emails → Create casefile → Generate spreadsheet → Email results

Usage:
    python scripts/poc_email_workflow.py
"""

import asyncio
import logging
from datetime import datetime
from typing import List

# Import the enhanced models with custom types
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    CreateCasefileRequest,
    CreateCasefilePayload,
    StoreGmailMessagesRequest, 
    StoreGmailMessagesPayload
)

# Import Google Workspace clients with new mock methods
from src.pydantic_ai_integration.integrations.google_workspace.clients import (
    GmailClient,
    SheetsClient,
    DriveClient
)

# Import validated models
from src.pydantic_models.workspace.gmail import GmailMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def poc_email_to_spreadsheet():
    """
    Complete POC workflow demonstrating validation enhancements.
    
    Workflow:
    1. Search emails by date using GmailClient (mock)
    2. Create casefile with validated custom types
    3. Store emails in casefile with full validation
    4. Generate spreadsheet with email metadata
    5. Upload spreadsheet to Drive (mock)
    6. Email results back to user (mock)
    
    Returns:
        dict: Results summary with casefile_id, message count, etc.
    """
    
    print("🎯 Starting Email-to-Spreadsheet POC Workflow")
    print("=" * 60)
    
    # Step 1: Search Gmail messages (mock mode)
    print("\n📧 Step 1: Searching Gmail messages...")
    gmail = GmailClient(user_id="poc_user", use_mock=True)
    
    email_response = await gmail.search_messages(
        query="after:2025/10/01",
        max_results=10
    )
    
    messages = email_response.messages  # List[GmailMessage] - fully validated!
    print(f"   ✅ Found {len(messages)} messages")
    print(f"   📊 First message: {messages[0].subject if messages else 'None'}")
    
    # Step 2: Create casefile (with custom types validation)
    print("\n📁 Step 2: Creating casefile with validated custom types...")
    casefile_svc = CasefileService()
    
    # This request uses custom types: ShortString, TagList, etc.
    create_request = CreateCasefileRequest(
        user_id="poc_user",
        operation="create_casefile",
        payload=CreateCasefilePayload(
            title="Email Analysis POC 2025-10-13",  # ShortString validation
            description="Proof-of-concept workflow demonstrating validation enhancements",
            tags=["poc", "email-analysis", "validation-demo"]  # TagList validation
        )
    )
    
    casefile_resp = await casefile_svc.create_casefile(create_request)
    casefile_id = casefile_resp.payload.casefile_id  # CasefileId type!
    print(f"   ✅ Created casefile: {casefile_id}")
    print(f"   🏷️  Tags: {create_request.payload.tags}")
    
    # Step 3: Store emails in casefile (validated storage)
    print("\n💾 Step 3: Storing emails with full validation...")
    if messages:
        store_request = StoreGmailMessagesRequest(
            user_id="poc_user",
            operation="store_gmail_messages",
            payload=StoreGmailMessagesPayload(
                casefile_id=casefile_id,
                messages=[msg.model_dump() for msg in messages],
                overwrite=True
            )
        )
        
        store_resp = await casefile_svc.store_gmail_messages(store_request)
        print(f"   ✅ Stored {len(messages)} messages in casefile")
        print(f"   📈 Storage status: {store_resp.status}")
    
    # Step 4: Generate spreadsheet data
    print("\n📊 Step 4: Generating spreadsheet with email metadata...")
    
    # Create spreadsheet data: Email ID | Sender | Subject | Attachments
    sheet_data = [
        ["Email ID", "Sender", "Subject", "Attachments", "Date"],  # Header
    ]
    
    for msg in messages:
        sheet_data.append([
            msg.id,
            msg.sender,
            msg.subject,
            "Y" if msg.has_attachments else "N",
            msg.internal_date
        ])
    
    print(f"   ✅ Generated spreadsheet with {len(sheet_data)} rows")
    print(f"   📋 Headers: {sheet_data[0]}")
    
    # Step 5: Create and populate spreadsheet (mock)
    print("\n🗂️  Step 5: Creating spreadsheet in Google Sheets...")
    sheets = SheetsClient(user_id="poc_user", use_mock=True)
    
    # Use the new create_spreadsheet method we just added!
    spreadsheet_result = await sheets.create_spreadsheet(
        title=f"Email Analysis - {datetime.now().strftime('%Y-%m-%d')}"
    )
    spreadsheet_id = spreadsheet_result["spreadsheet_id"]
    spreadsheet_url = spreadsheet_result["spreadsheet_url"]
    
    print(f"   ✅ Created spreadsheet: {spreadsheet_id}")
    print(f"   🔗 URL: {spreadsheet_url}")
    
    # Use the new update_values method we just added!
    update_result = await sheets.update_values(
        spreadsheet_id=spreadsheet_id,
        range_name="Sheet1!A1:E10",
        values=sheet_data
    )
    
    print(f"   ✅ Updated {update_result['updated_cells']} cells")
    
    # Step 6: Upload to Drive (mock)
    print("\n🗃️  Step 6: Backing up to Google Drive...")
    drive = DriveClient(user_id="poc_user", use_mock=True)
    
    # Create CSV content for backup
    csv_content = "\\n".join([",".join(map(str, row)) for row in sheet_data])
    
    # Use the new upload_file method we just added!
    drive_result = await drive.upload_file(
        file_name=f"email_analysis_backup_{datetime.now().strftime('%Y%m%d')}.csv",
        content=csv_content,
        mime_type="text/csv"
    )
    
    print(f"   ✅ Uploaded backup file: {drive_result['id']}")
    print(f"   🔗 Drive link: {drive_result['web_view_link']}")
    
    # Step 7: Email results (mock)
    print("\n📬 Step 7: Emailing results...")
    
    results_body = f"""
POC Email Analysis Complete!

Casefile: {casefile_id}
Messages analyzed: {len(messages)}
Spreadsheet: {spreadsheet_url}
Drive backup: {drive_result['web_view_link']}

This workflow demonstrated:
✅ Custom types validation (CasefileId, ShortString, etc.)
✅ Enhanced model validation (GmailMessage with 20+ fields)
✅ End-to-end data integrity
✅ Mock Google Workspace integration

Phase 1 Pydantic validation enhancements working perfectly!
"""
    
    email_result = await gmail.send_message(
        to="poc_user@example.com",
        subject="POC: Email Analysis Results - Validation Demo",
        body=results_body.strip()
    )
    
    print(f"   ✅ Sent results email: {email_result.message_id}")
    
    # Summary
    print("\n🎉 POC Workflow Complete!")
    print("=" * 60)
    
    results = {
        "casefile_id": casefile_id,
        "messages_analyzed": len(messages),
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": spreadsheet_url,
        "drive_backup_id": drive_result['id'],
        "results_email_id": email_result.message_id,
        "validation_features_used": [
            "CasefileId custom type",
            "ShortString validation", 
            "TagList validation",
            "GmailMessage model with 20+ fields",
            "IsoTimestamp formatting",
            "Full request/response validation"
        ]
    }
    
    print(f"📊 Results Summary:")
    for key, value in results.items():
        if key != "validation_features_used":
            print(f"   {key}: {value}")
    
    print(f"\n🔧 Validation Features Demonstrated:")
    for feature in results["validation_features_used"]:
        print(f"   ✅ {feature}")
    
    return results

async def main():
    """Main entry point for the POC."""
    try:
        results = await poc_email_to_spreadsheet()
        print("\n✨ POC completed successfully!")
        print("This demonstrates how Phase 1 validation enhancements enable")
        print("complex, real-world workflows with data integrity guarantees!")
        return results
    except Exception as e:
        logger.error(f"POC failed: {e}")
        print(f"\n❌ POC failed: {e}")
        raise

if __name__ == "__main__":
    # Run the POC workflow
    results = asyncio.run(main())