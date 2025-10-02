"""
Gmail API client wrapper for MDS Objects.

Provides high-level interface for Gmail operations including listing,
reading, sending, and searching messages.
"""

import logging
import base64
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

from .auth import GoogleWorkspaceAuth

logger = logging.getLogger(__name__)


class GmailClient:
    """High-level client for Gmail API operations."""
    
    def __init__(self, user_id: Optional[str] = None, auth: Optional[GoogleWorkspaceAuth] = None):
        """
        Initialize Gmail client.
        
        Args:
            user_id: User ID for tracking (not used for API auth)
            auth: GoogleWorkspaceAuth instance (creates new if not provided)
        """
        self.user_id = user_id or "me"
        self.auth = auth or GoogleWorkspaceAuth()
        self._service = None
    
    def _get_service(self):
        """Get or create Gmail API service."""
        if not self._service:
            self._service = self.auth.build_service('gmail', 'v1')
        return self._service
    
    async def list_messages(
        self,
        max_results: int = 10,
        query: str = "",
        label_ids: Optional[List[str]] = None,
        include_spam_trash: bool = False
    ) -> Dict[str, Any]:
        """
        List messages from Gmail inbox.
        
        Args:
            max_results: Maximum number of messages to return (1-100)
            query: Gmail search query (e.g., "from:sender@example.com")
            label_ids: List of label IDs to filter by
            include_spam_trash: Whether to include spam and trash
            
        Returns:
            Dictionary with messages list and metadata
            
        Raises:
            HttpError: If API call fails
        """
        try:
            service = self._get_service()
            
            # Build request parameters
            params = {
                'userId': 'me',
                'maxResults': max_results,
                'includeSpamTrash': include_spam_trash
            }
            
            if query:
                params['q'] = query
            
            if label_ids:
                params['labelIds'] = label_ids
            
            # Execute request
            result = service.users().messages().list(**params).execute()
            
            messages = result.get('messages', [])
            result_size_estimate = result.get('resultSizeEstimate', 0)
            next_page_token = result.get('nextPageToken')
            
            logger.info(
                f"Listed {len(messages)} messages "
                f"(estimated total: {result_size_estimate})"
            )
            
            return {
                'messages': messages,
                'result_size_estimate': result_size_estimate,
                'next_page_token': next_page_token,
                'message_count': len(messages)
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error listing messages: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing messages: {e}")
            raise
    
    async def get_message(
        self,
        message_id: str,
        format: str = 'full',
        metadata_headers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get a specific Gmail message by ID.
        
        Args:
            message_id: The ID of the message to retrieve
            format: The format to return the message in (full, metadata, minimal, raw)
            metadata_headers: List of headers to return (when format='metadata')
            
        Returns:
            Dictionary containing message data
            
        Raises:
            HttpError: If API call fails
        """
        try:
            service = self._get_service()
            
            # Build request parameters
            params = {
                'userId': 'me',
                'id': message_id,
                'format': format
            }
            
            if metadata_headers and format == 'metadata':
                params['metadataHeaders'] = metadata_headers
            
            # Execute request
            message = service.users().messages().get(**params).execute()
            
            # Parse message data
            result = {
                'id': message.get('id'),
                'thread_id': message.get('threadId'),
                'label_ids': message.get('labelIds', []),
                'snippet': message.get('snippet', ''),
                'size_estimate': message.get('sizeEstimate', 0),
                'internal_date': message.get('internalDate')
            }
            
            # Add payload if available
            if 'payload' in message:
                payload = message['payload']
                result['headers'] = payload.get('headers', [])
                result['mime_type'] = payload.get('mimeType')
                result['body'] = payload.get('body', {})
                result['parts'] = payload.get('parts', [])
            
            # Add raw message if available
            if 'raw' in message:
                result['raw'] = message['raw']
            
            logger.info(f"Retrieved message {message_id}")
            
            return result
            
        except HttpError as e:
            logger.error(f"Gmail API error getting message {message_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting message {message_id}: {e}")
            raise
    
    async def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email message via Gmail.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (optional, uses authenticated user if not provided)
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            
        Returns:
            Dictionary with sent message ID and metadata
            
        Raises:
            HttpError: If API call fails
        """
        try:
            service = self._get_service()
            
            # Create MIME message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if from_email:
                message['from'] = from_email
            
            if cc:
                message['cc'] = cc
            
            if bcc:
                message['bcc'] = bcc
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Send message
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Sent message to {to}, ID: {result.get('id')}")
            
            return {
                'id': result.get('id'),
                'thread_id': result.get('threadId'),
                'label_ids': result.get('labelIds', []),
                'to': to,
                'subject': subject,
                'status': 'sent'
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error sending message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            raise
    
    async def search_messages(
        self,
        query: str,
        max_results: int = 10,
        label_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search Gmail messages using Gmail query syntax.
        
        Args:
            query: Gmail search query (e.g., "from:user@example.com subject:report")
            max_results: Maximum number of messages to return
            label_ids: List of label IDs to filter by
            
        Returns:
            Dictionary with search results
            
        Raises:
            HttpError: If API call fails
        """
        # Search is essentially list_messages with a query
        return await self.list_messages(
            max_results=max_results,
            query=query,
            label_ids=label_ids
        )
    
    async def get_labels(self) -> Dict[str, Any]:
        """
        Get list of Gmail labels for the user.
        
        Returns:
            Dictionary with labels list
            
        Raises:
            HttpError: If API call fails
        """
        try:
            service = self._get_service()
            
            result = service.users().labels().list(userId='me').execute()
            labels = result.get('labels', [])
            
            logger.info(f"Retrieved {len(labels)} labels")
            
            return {
                'labels': labels,
                'label_count': len(labels)
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error getting labels: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting labels: {e}")
            raise
    
    async def modify_message(
        self,
        message_id: str,
        add_label_ids: Optional[List[str]] = None,
        remove_label_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Modify labels on a message.
        
        Args:
            message_id: The ID of the message to modify
            add_label_ids: List of label IDs to add
            remove_label_ids: List of label IDs to remove
            
        Returns:
            Dictionary with updated message data
            
        Raises:
            HttpError: If API call fails
        """
        try:
            service = self._get_service()
            
            body = {}
            if add_label_ids:
                body['addLabelIds'] = add_label_ids
            if remove_label_ids:
                body['removeLabelIds'] = remove_label_ids
            
            result = service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            
            logger.info(f"Modified labels on message {message_id}")
            
            return {
                'id': result.get('id'),
                'thread_id': result.get('threadId'),
                'label_ids': result.get('labelIds', [])
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error modifying message {message_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error modifying message {message_id}: {e}")
            raise
