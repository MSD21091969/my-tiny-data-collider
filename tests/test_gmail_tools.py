"""
Comprehensive test suite for Gmail tools.

Tests cover:
- Parameter validation
- API client integration
- Error handling
- Event tracking
- Success scenarios
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.pydantic_ai_integration.tools.gmail_tools import (
    GmailListMessagesParams,
    GmailGetMessageParams,
    GmailSendMessageParams,
    GmailSearchMessagesParams,
    gmail_list_messages,
    gmail_get_message,
    gmail_send_message,
    gmail_search_messages
)
from src.pydantic_ai_integration.dependencies import MDSContext


# ============================================================================
# Parameter Validation Tests
# ============================================================================

class TestGmailListMessagesParams:
    """Test parameter validation for gmail_list_messages."""
    
    def test_valid_params(self):
        """Test that valid parameters are accepted."""
        params = GmailListMessagesParams(
            max_results=50,
            query="from:sender@example.com",
            label_ids=["INBOX"],
            include_spam_trash=False
        )
        assert params.max_results == 50
        assert params.query == "from:sender@example.com"
    
    def test_max_results_minimum(self):
        """Test that max_results must be at least 1."""
        with pytest.raises(ValueError):
            GmailListMessagesParams(max_results=0)
    
    def test_max_results_maximum(self):
        """Test that max_results must be at most 100."""
        with pytest.raises(ValueError):
            GmailListMessagesParams(max_results=101)
    
    def test_query_length_limit(self):
        """Test that query length is limited to 500 characters."""
        long_query = "a" * 501
        with pytest.raises(ValueError):
            GmailListMessagesParams(query=long_query)
    
    def test_default_values(self):
        """Test that default values are correctly set."""
        params = GmailListMessagesParams()
        assert params.max_results == 10
        assert params.query == ""
        assert params.label_ids is None
        assert params.include_spam_trash is False


class TestGmailGetMessageParams:
    """Test parameter validation for gmail_get_message."""
    
    def test_valid_params(self):
        """Test that valid parameters are accepted."""
        params = GmailGetMessageParams(
            message_id="msg_12345",
            format="metadata",
            metadata_headers=["Subject", "From"]
        )
        assert params.message_id == "msg_12345"
        assert params.format == "metadata"
    
    def test_message_id_required(self):
        """Test that message_id is required."""
        with pytest.raises(ValueError):
            GmailGetMessageParams()
    
    def test_message_id_min_length(self):
        """Test that message_id must have minimum length."""
        with pytest.raises(ValueError):
            GmailGetMessageParams(message_id="")
    
    def test_message_id_max_length(self):
        """Test that message_id length is limited."""
        long_id = "a" * 101
        with pytest.raises(ValueError):
            GmailGetMessageParams(message_id=long_id)
    
    def test_default_format(self):
        """Test that format defaults to 'full'."""
        params = GmailGetMessageParams(message_id="msg_12345")
        assert params.format == "full"


class TestGmailSendMessageParams:
    """Test parameter validation for gmail_send_message."""
    
    def test_valid_params(self):
        """Test that valid parameters are accepted."""
        params = GmailSendMessageParams(
            to="recipient@example.com",
            subject="Test Email",
            body="This is a test email body"
        )
        assert params.to == "recipient@example.com"
        assert params.subject == "Test Email"
    
    def test_to_required(self):
        """Test that 'to' field is required."""
        with pytest.raises(ValueError):
            GmailSendMessageParams(
                subject="Test",
                body="Body"
            )
    
    def test_subject_required(self):
        """Test that 'subject' field is required."""
        with pytest.raises(ValueError):
            GmailSendMessageParams(
                to="recipient@example.com",
                body="Body"
            )
    
    def test_body_required(self):
        """Test that 'body' field is required."""
        with pytest.raises(ValueError):
            GmailSendMessageParams(
                to="recipient@example.com",
                subject="Test"
            )
    
    def test_to_min_length(self):
        """Test that 'to' has minimum length requirement."""
        with pytest.raises(ValueError):
            GmailSendMessageParams(
                to="a@b",  # Too short
                subject="Test",
                body="Body"
            )
    
    def test_subject_min_length(self):
        """Test that subject cannot be empty."""
        with pytest.raises(ValueError):
            GmailSendMessageParams(
                to="recipient@example.com",
                subject="",
                body="Body"
            )
    
    def test_body_max_length(self):
        """Test that body length is limited."""
        long_body = "a" * 50001
        with pytest.raises(ValueError):
            GmailSendMessageParams(
                to="recipient@example.com",
                subject="Test",
                body=long_body
            )


class TestGmailSearchMessagesParams:
    """Test parameter validation for gmail_search_messages."""
    
    def test_valid_params(self):
        """Test that valid parameters are accepted."""
        params = GmailSearchMessagesParams(
            query="subject:report",
            max_results=25
        )
        assert params.query == "subject:report"
        assert params.max_results == 25
    
    def test_query_required(self):
        """Test that query is required."""
        with pytest.raises(ValueError):
            GmailSearchMessagesParams()
    
    def test_query_min_length(self):
        """Test that query cannot be empty."""
        with pytest.raises(ValueError):
            GmailSearchMessagesParams(query="")
    
    def test_query_max_length(self):
        """Test that query length is limited."""
        long_query = "a" * 501
        with pytest.raises(ValueError):
            GmailSearchMessagesParams(query=long_query)


# ============================================================================
# Tool Implementation Tests
# ============================================================================

@pytest.mark.asyncio
class TestGmailListMessages:
    """Test gmail_list_messages tool implementation."""
    
    async def test_successful_list(self, minimal_mds_context):
        """Test successful message listing."""
        ctx = minimal_mds_context
        
        # Mock Gmail client
        mock_result = {
            'messages': [
                {'id': 'msg1', 'threadId': 'thread1'},
                {'id': 'msg2', 'threadId': 'thread2'}
            ],
            'result_size_estimate': 100,
            'message_count': 2,
            'next_page_token': 'token123'
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.list_messages = AsyncMock(return_value=mock_result)
            
            result = await gmail_list_messages(ctx, max_results=10, query="")
            
            assert result['message_count'] == 2
            assert len(result['messages']) == 2
            assert result['result_size_estimate'] == 100
    
    async def test_list_with_query(self, minimal_mds_context):
        """Test listing with search query."""
        ctx = minimal_mds_context
        
        mock_result = {
            'messages': [{'id': 'msg1', 'threadId': 'thread1'}],
            'result_size_estimate': 1,
            'message_count': 1,
            'next_page_token': None
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.list_messages = AsyncMock(return_value=mock_result)
            
            result = await gmail_list_messages(
                ctx,
                max_results=10,
                query="from:sender@example.com"
            )
            
            assert result['message_count'] == 1
            mock_instance.list_messages.assert_called_once()
    
    async def test_list_error_handling(self, minimal_mds_context):
        """Test error handling in list_messages."""
        ctx = minimal_mds_context
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.list_messages = AsyncMock(
                side_effect=Exception("API Error")
            )
            
            result = await gmail_list_messages(ctx, max_results=10, query="")
            
            assert 'error' in result
            assert result['message_count'] == 0


@pytest.mark.asyncio
class TestGmailGetMessage:
    """Test gmail_get_message tool implementation."""
    
    async def test_successful_get(self, minimal_mds_context):
        """Test successful message retrieval."""
        ctx = minimal_mds_context
        
        mock_result = {
            'id': 'msg123',
            'thread_id': 'thread123',
            'snippet': 'Test message',
            'label_ids': ['INBOX'],
            'headers': [
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'From', 'value': 'sender@example.com'}
            ]
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.get_message = AsyncMock(return_value=mock_result)
            
            result = await gmail_get_message(ctx, message_id="msg123")
            
            assert result['id'] == 'msg123'
            assert result['snippet'] == 'Test message'
    
    async def test_get_with_format(self, minimal_mds_context):
        """Test getting message with specific format."""
        ctx = minimal_mds_context
        
        mock_result = {
            'id': 'msg123',
            'thread_id': 'thread123',
            'snippet': 'Test'
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.get_message = AsyncMock(return_value=mock_result)
            
            result = await gmail_get_message(
                ctx,
                message_id="msg123",
                format="metadata"
            )
            
            assert 'id' in result
            mock_instance.get_message.assert_called_once()
    
    async def test_get_error_handling(self, minimal_mds_context):
        """Test error handling in get_message."""
        ctx = minimal_mds_context
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.get_message = AsyncMock(
                side_effect=Exception("Message not found")
            )
            
            result = await gmail_get_message(ctx, message_id="invalid")
            
            assert 'error' in result


@pytest.mark.asyncio
class TestGmailSendMessage:
    """Test gmail_send_message tool implementation."""
    
    async def test_successful_send(self, minimal_mds_context):
        """Test successful message sending."""
        ctx = minimal_mds_context
        
        mock_result = {
            'id': 'sent123',
            'thread_id': 'thread123',
            'to': 'recipient@example.com',
            'subject': 'Test Email',
            'status': 'sent'
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.send_message = AsyncMock(return_value=mock_result)
            
            result = await gmail_send_message(
                ctx,
                to="recipient@example.com",
                subject="Test Email",
                body="This is a test message"
            )
            
            assert result['status'] == 'sent'
            assert result['to'] == 'recipient@example.com'
    
    async def test_send_with_cc_bcc(self, minimal_mds_context):
        """Test sending with CC and BCC."""
        ctx = minimal_mds_context
        
        mock_result = {
            'id': 'sent123',
            'thread_id': 'thread123',
            'status': 'sent'
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.send_message = AsyncMock(return_value=mock_result)
            
            result = await gmail_send_message(
                ctx,
                to="recipient@example.com",
                subject="Test",
                body="Body",
                cc="cc@example.com",
                bcc="bcc@example.com"
            )
            
            assert 'id' in result
            mock_instance.send_message.assert_called_once()
    
    async def test_send_error_handling(self, minimal_mds_context):
        """Test error handling in send_message."""
        ctx = minimal_mds_context
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.send_message = AsyncMock(
                side_effect=Exception("Send failed")
            )
            
            result = await gmail_send_message(
                ctx,
                to="recipient@example.com",
                subject="Test",
                body="Body"
            )
            
            assert 'error' in result


@pytest.mark.asyncio
class TestGmailSearchMessages:
    """Test gmail_search_messages tool implementation."""
    
    async def test_successful_search(self, minimal_mds_context):
        """Test successful message search."""
        ctx = minimal_mds_context
        
        mock_result = {
            'messages': [
                {'id': 'msg1', 'threadId': 'thread1'},
                {'id': 'msg2', 'threadId': 'thread2'}
            ],
            'result_size_estimate': 2,
            'message_count': 2
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.search_messages = AsyncMock(return_value=mock_result)
            
            result = await gmail_search_messages(
                ctx,
                query="from:sender@example.com"
            )
            
            assert result['message_count'] == 2
            assert result['query'] == "from:sender@example.com"
    
    async def test_search_with_labels(self, minimal_mds_context):
        """Test search with label filtering."""
        ctx = minimal_mds_context
        
        mock_result = {
            'messages': [{'id': 'msg1', 'threadId': 'thread1'}],
            'result_size_estimate': 1,
            'message_count': 1
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.search_messages = AsyncMock(return_value=mock_result)
            
            result = await gmail_search_messages(
                ctx,
                query="subject:report",
                label_ids=["INBOX"]
            )
            
            assert result['message_count'] == 1
    
    async def test_search_error_handling(self, minimal_mds_context):
        """Test error handling in search_messages."""
        ctx = minimal_mds_context
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.search_messages = AsyncMock(
                side_effect=Exception("Search failed")
            )
            
            result = await gmail_search_messages(ctx, query="test")
            
            assert 'error' in result
            assert result['message_count'] == 0


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
class TestGmailToolsIntegration:
    """Integration tests for Gmail tools."""
    
    async def test_event_tracking(self, minimal_mds_context):
        """Test that events are properly tracked."""
        ctx = minimal_mds_context
        
        mock_result = {
            'messages': [],
            'message_count': 0,
            'result_size_estimate': 0
        }
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.list_messages = AsyncMock(return_value=mock_result)
            
            await gmail_list_messages(ctx, max_results=10, query="")
            
            # Check that event was registered
            assert len(ctx.tool_events) > 0
            event = ctx.tool_events[-1]
            assert event.tool_name == "gmail_list_messages"
    
    async def test_context_preservation(self, minimal_mds_context):
        """Test that context is preserved across tool calls."""
        ctx = minimal_mds_context
        original_user_id = ctx.user_id
        
        mock_result = {'messages': [], 'message_count': 0}
        
        with patch('src.pydantic_ai_integration.tools.gmail_tools.GmailClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.list_messages = AsyncMock(return_value=mock_result)
            
            await gmail_list_messages(ctx, max_results=10, query="")
            
            # Context should be unchanged
            assert ctx.user_id == original_user_id
