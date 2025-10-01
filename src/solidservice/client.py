"""
Solid Pod Client for authenticated read/write operations.
Handles CSS client credentials authentication flow.
"""

from typing import Optional, Dict, Any
import logging
from authlib.integrations.requests_client import OAuth2Session

logger = logging.getLogger(__name__)


class SolidPodClient:
    """
    Client for interacting with a Solid Pod using CSS client credentials.
    
    CSS (Community Solid Server) uses OAuth2 Client Credentials flow.
    This client handles token management and authenticated requests.
    """
    
    def __init__(
        self,
        pod_url: str,
        client_id: str,
        client_secret: str,
        token_endpoint: Optional[str] = None
    ):
        """
        Initialize Solid Pod client.
        
        Args:
            pod_url: Base URL of your pod (e.g., http://localhost:3000/username/)
            client_id: Client ID from CSS account credentials
            client_secret: Client secret from CSS account credentials
            token_endpoint: OAuth2 token endpoint (auto-discovered if None)
        """
        self.pod_url = pod_url.rstrip('/') + '/'
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Extract base URL for token endpoint
        base_url = pod_url.rsplit('/', 2)[0]
        self.token_endpoint = token_endpoint or f"{base_url}/.oidc/token"
        
        self.session: Optional[OAuth2Session] = None
        self._access_token: Optional[str] = None
    
    def _get_session(self) -> OAuth2Session:
        """Get or create an authenticated OAuth2 session."""
        if self.session is None or self._access_token is None:
            # Create OAuth2 session with client credentials
            self.session = OAuth2Session(
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_endpoint=self.token_endpoint,
                grant_type='client_credentials'
            )
            
            # Fetch access token
            try:
                token = self.session.fetch_token(
                    self.token_endpoint,
                    grant_type='client_credentials'
                )
                self._access_token = token.get('access_token')
                logger.info("Successfully obtained access token")
            except Exception as e:
                logger.error(f"Failed to obtain access token: {e}")
                raise
        
        return self.session
    
    def create_container(self, path: str) -> bool:
        """
        Create a container (folder) in the pod.
        
        Args:
            path: Relative path from pod root (e.g., 'casefiles/' or 'data/legal/')
        
        Returns:
            True if created successfully, False otherwise
        """
        url = self.pod_url + path.lstrip('/')
        if not url.endswith('/'):
            url += '/'
        
        headers = {
            'Content-Type': 'text/turtle',
            'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'
        }
        
        try:
            session = self._get_session()
            response = session.put(url, headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info(f"Created container: {url}")
                return True
            else:
                logger.warning(f"Failed to create container {url}: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating container {url}: {e}")
            return False
    
    def write_resource(self, path: str, content: str, content_type: str = 'text/turtle') -> bool:
        """
        Write a resource (file) to the pod.
        
        Args:
            path: Relative path from pod root
            content: Content to write
            content_type: MIME type of content
        
        Returns:
            True if written successfully, False otherwise
        """
        url = self.pod_url + path.lstrip('/')
        
        headers = {
            'Content-Type': content_type
        }
        
        try:
            session = self._get_session()
            response = session.put(url, data=content.encode('utf-8'), headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info(f"Wrote resource: {url}")
                return True
            else:
                logger.warning(f"Failed to write resource {url}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing resource {url}: {e}")
            return False
    
    def read_resource(self, path: str) -> Optional[str]:
        """
        Read a resource from the pod.
        
        Args:
            path: Relative path from pod root
        
        Returns:
            Resource content as string, or None if not found
        """
        url = self.pod_url + path.lstrip('/')
        
        try:
            session = self._get_session()
            response = session.get(url)
            
            if response.status_code == 200:
                logger.info(f"Read resource: {url}")
                return response.text
            else:
                logger.warning(f"Failed to read resource {url}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading resource {url}: {e}")
            return None
    
    def delete_resource(self, path: str) -> bool:
        """
        Delete a resource from the pod.
        
        Args:
            path: Relative path from pod root
        
        Returns:
            True if deleted successfully, False otherwise
        """
        url = self.pod_url + path.lstrip('/')
        
        try:
            session = self._get_session()
            response = session.delete(url)
            
            if response.status_code in [200, 204]:
                logger.info(f"Deleted resource: {url}")
                return True
            else:
                logger.warning(f"Failed to delete resource {url}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting resource {url}: {e}")
            return False
    
    def list_container(self, path: str = '') -> Optional[Dict[str, Any]]:
        """
        List contents of a container.
        
        Args:
            path: Relative path from pod root
        
        Returns:
            Dictionary with container contents, or None if error
        """
        url = self.pod_url + path.lstrip('/')
        if not url.endswith('/'):
            url += '/'
        
        try:
            session = self._get_session()
            response = session.get(url, headers={'Accept': 'application/ld+json'})
            
            if response.status_code == 200:
                logger.info(f"Listed container: {url}")
                return response.json()
            else:
                logger.warning(f"Failed to list container {url}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error listing container {url}: {e}")
            return None
