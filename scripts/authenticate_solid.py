"""
Browser-based Solid authentication using Authorization Code + PKCE flow.
This opens a browser for you to log in, then captures the token.
"""

import webbrowser
import secrets
import hashlib
import base64
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from typing import Optional, Dict
import requests
from dotenv import load_dotenv, set_key
import os

load_dotenv()

# CSS OAuth2 endpoints
BASE_URL = "http://localhost:3000"
AUTH_ENDPOINT = f"{BASE_URL}/.oidc/auth"
TOKEN_ENDPOINT = f"{BASE_URL}/.oidc/token"
REDIRECT_URI = "http://127.0.0.1:8765/callback"
WEBID = os.getenv("SOLID_WEBID", "http://localhost:3000/maassenhochrath@gmail.com/profile/card#me")

# Storage for callback
auth_code = None
auth_state = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth2 callback."""
    
    def do_GET(self):
        """Handle the callback from CSS."""
        global auth_code, auth_state
        
        # Parse query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            auth_state = params.get('state', [None])[0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
                <html>
                <head><title>Authentication Successful</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: green;">Authentication Successful!</h1>
                    <p>You can close this window and return to VS Code.</p>
                    <p>The Tiny Data Collider now has access to your Solid Pod.</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            # Error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error = params.get('error', ['Unknown error'])[0]
            html = f"""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Authentication Failed</h1>
                    <p>Error: {error}</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress server logs."""
        pass


def generate_pkce_pair():
    """Generate PKCE code verifier and challenge."""
    # Generate random code verifier
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Create code challenge (SHA256 hash of verifier)
    challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge


def start_callback_server():
    """Start local server to receive OAuth2 callback."""
    # Bind to 127.0.0.1 explicitly (IPv4) to avoid IPv6 issues
    server = HTTPServer(('127.0.0.1', 8765), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.daemon = True
    thread.start()
    print(f"    Callback server listening on http://127.0.0.1:8765")
    return server


def authenticate():
    """
    Perform browser-based authentication flow.
    Returns access token and refresh token.
    """
    print("=" * 60)
    print("🌐 Browser-Based Solid Authentication")
    print("=" * 60)
    
    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(16)
    
    # Start local callback server
    print("\n1️⃣  Starting local callback server on port 8765...")
    server = start_callback_server()
    
    # Build authorization URL
    # Use a simple client_id for localhost development
    client_id = f"{REDIRECT_URI.rstrip('/callback')}"  # http://127.0.0.1:8765
    
    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid webid offline_access',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'state': state,
    }
    auth_url = f"{AUTH_ENDPOINT}?{urlencode(auth_params)}"
    
    print("\n2️⃣  Opening browser for login...")
    print(f"    If browser doesn't open, visit:\n    {auth_url}\n")
    webbrowser.open(auth_url)
    
    print("3️⃣  Waiting for authorization...")
    print("    → Log in to your Solid Pod")
    print("    → Authorize the application")
    print("    → Browser will redirect back automatically\n")
    
    # Wait for callback (timeout after 2 minutes)
    import time
    timeout = 120
    start_time = time.time()
    
    global auth_code
    while auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(0.5)
    
    if auth_code is None:
        print("❌ Timeout waiting for authorization")
        return None, None
    
    print("✅ Authorization code received!\n")
    
    # Exchange authorization code for tokens
    print("4️⃣  Exchanging code for access token...")
    
    client_id = REDIRECT_URI.rstrip('/callback')  # http://127.0.0.1:8765
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': client_id,
        'code_verifier': code_verifier,
    }
    
    try:
        response = requests.post(TOKEN_ENDPOINT, data=token_data)
        response.raise_for_status()
        
        tokens = response.json()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        
        print("✅ Access token obtained!\n")
        
        # Save tokens to .env
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        if access_token:
            set_key(env_file, 'SOLID_ACCESS_TOKEN', access_token)
            print(f"💾 Saved SOLID_ACCESS_TOKEN to .env")
        if refresh_token:
            set_key(env_file, 'SOLID_REFRESH_TOKEN', refresh_token)
            print(f"💾 Saved SOLID_REFRESH_TOKEN to .env")
        
        print("\n" + "=" * 60)
        print("🎉 Authentication Complete!")
        print("=" * 60)
        print("\nYou now have full access to your Solid Pod!")
        print("\nNext steps:")
        print("  python scripts\\init_solid_pod.py")
        print("=" * 60)
        
        return access_token, refresh_token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Token exchange failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None, None


if __name__ == "__main__":
    authenticate()
