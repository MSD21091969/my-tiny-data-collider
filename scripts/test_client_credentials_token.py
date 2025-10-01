"""
Try using client credentials with proper token exchange.
CSS client credentials can get an access token with specific scopes.
"""

import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://localhost:3000"
TOKEN_ENDPOINT = f"{BASE_URL}/.oidc/token"
CLIENT_ID = os.getenv("SOLID_CLIENT_ID")
CLIENT_SECRET = os.getenv("SOLID_CLIENT_SECRET")
WEBID = os.getenv("SOLID_WEBID")

print("=" * 60)
print("🔐 Testing Client Credentials Token Exchange")
print("=" * 60)

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ Missing CLIENT_ID or CLIENT_SECRET in .env")
    exit(1)

print(f"\nClient ID: {CLIENT_ID[:30]}...")
print(f"WebID: {WEBID}\n")

# Try client credentials grant with webid scope
print("Attempting token exchange with webid scope...")

data = {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'scope': 'webid',  # Request webid scope
}

try:
    response = requests.post(TOKEN_ENDPOINT, data=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Token obtained!")
        print(f"   Access Token: {token_data.get('access_token', 'N/A')[:50]}...")
        print(f"   Token Type: {token_data.get('token_type', 'N/A')}")
        print(f"   Expires In: {token_data.get('expires_in', 'N/A')} seconds")
        print(f"   Scope: {token_data.get('scope', 'N/A')}")
        
        # Test using this token
        print("\n📝 Testing token with pod access...")
        pod_url = "http://localhost:3000/maassenhochrath@gmail.com/"
        headers = {
            'Authorization': f"Bearer {token_data['access_token']}"
        }
        test_response = requests.get(pod_url, headers=headers)
        print(f"   Pod access status: {test_response.status_code}")
        
        if test_response.status_code == 200:
            print("   ✅ Token works for pod access!")
        else:
            print(f"   ❌ Still getting: {test_response.status_code}")
            
    else:
        print(f"❌ Token request failed")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
