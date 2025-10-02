"""
OAuth2 authentication helper for Google Workspace APIs.

Provides authentication and credential management for Gmail, Drive, Calendar,
and other Google Workspace services.
"""

import os
import logging
from typing import Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GoogleWorkspaceAuth:
    """Manages OAuth2 authentication for Google Workspace APIs."""
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        scopes: Optional[list] = None
    ):
        """
        Initialize authentication manager.
        
        Args:
            credentials_path: Path to OAuth2 client credentials JSON
            token_path: Path to store/load access tokens
            scopes: List of OAuth2 scopes to request
        """
        self.credentials_path = credentials_path or os.getenv(
            'GOOGLE_OAUTH_CREDENTIALS',
            'credentials.json'
        )
        self.token_path = token_path or os.getenv(
            'GOOGLE_TOKEN_PATH',
            'token.json'
        )
        self.scopes = scopes or GMAIL_SCOPES
        self._credentials: Optional[Credentials] = None
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Get valid credentials, refreshing or authenticating as needed.
        
        Returns:
            Valid Credentials object or None if authentication fails
        """
        # Try to load existing token
        if os.path.exists(self.token_path):
            try:
                self._credentials = Credentials.from_authorized_user_file(
                    self.token_path,
                    self.scopes
                )
                logger.info(f"Loaded credentials from {self.token_path}")
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")
                self._credentials = None
        
        # Refresh if expired
        if self._credentials and self._credentials.expired and self._credentials.refresh_token:
            try:
                self._credentials.refresh(Request())
                logger.info("Refreshed expired credentials")
                self._save_credentials()
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                self._credentials = None
        
        # Authenticate if no valid credentials
        if not self._credentials or not self._credentials.valid:
            if not os.path.exists(self.credentials_path):
                logger.error(
                    f"Credentials file not found: {self.credentials_path}\n"
                    "Please download OAuth2 credentials from Google Cloud Console"
                )
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.scopes
                )
                self._credentials = flow.run_local_server(port=0)
                logger.info("Completed OAuth2 authentication flow")
                self._save_credentials()
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                return None
        
        return self._credentials
    
    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        if self._credentials:
            try:
                with open(self.token_path, 'w') as token_file:
                    token_file.write(self._credentials.to_json())
                logger.info(f"Saved credentials to {self.token_path}")
            except Exception as e:
                logger.warning(f"Failed to save credentials: {e}")
    
    def build_service(self, service_name: str, version: str):
        """
        Build a Google API service client.
        
        Args:
            service_name: Name of the service (e.g., 'gmail', 'drive')
            version: API version (e.g., 'v1')
            
        Returns:
            Service client object
        """
        credentials = self.get_credentials()
        if not credentials:
            raise RuntimeError("Failed to obtain valid credentials")
        
        return build(service_name, version, credentials=credentials)
    
    def revoke_credentials(self) -> bool:
        """
        Revoke current credentials and delete token file.
        
        Returns:
            True if successful
        """
        try:
            if self._credentials:
                self._credentials.revoke(Request())
                logger.info("Revoked credentials")
            
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
                logger.info(f"Deleted token file: {self.token_path}")
            
            self._credentials = None
            return True
        except Exception as e:
            logger.error(f"Failed to revoke credentials: {e}")
            return False
