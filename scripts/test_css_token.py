"""
Test CSS client credential token format.
Based on CSS documentation for token-based authentication.
"""

import requests
from dotenv import load_dotenv
import os

load_dotenv()

POD_URL = os.getenv("SOLID_POD_URL", "http://localhost:3000/maassenhochrath@gmail.com/")
CLIENT_ID = os.getenv("SOLID_CLIENT_ID")
CLIENT_SECRET = os.getenv("SOLID_CLIENT_SECRET")

print("=" * 60)
print("🔐 Testing CSS Token Formats")
print("=" * 60)
print(f"\nClient ID: {CLIENT_ID[:30]}...")
print(f"Client Secret: {CLIENT_SECRET[:30]}...")
print(f"\nTest URL: {POD_URL}")

# Test different token formats
formats = [
    ("CSS-Account-Token", f"{CLIENT_ID}:{CLIENT_SECRET}"),
    ("Bearer", CLIENT_SECRET),  # Sometimes the secret itself is the token
    ("Bearer", f"{CLIENT_ID}:{CLIENT_SECRET}"),
    ("Token", CLIENT_SECRET),
    ("Authorization", CLIENT_SECRET),
]

for auth_type, token_value in formats:
    print(f"\n{'='*60}")
    print(f"Testing: {auth_type}")
    print(f"{'='*60}")
    
    headers = {
        'Authorization': f"{auth_type} {token_value}"
    }
    
    try:
        response = requests.get(POD_URL, headers=headers)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ SUCCESS! This format works!")
            print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
            break
        elif response.status_code == 401:
            print(f"  ❌ Unauthorized")
        else:
            print(f"  ⚠️  Unexpected status")
            print(f"  Response: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("💡 Note: CSS client credentials created via the web UI")
print("   may only work with specific authentication flows.")
print("   We may need to use a Solid auth library instead.")
print("=" * 60)
