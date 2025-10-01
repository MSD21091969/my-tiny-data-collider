"""
Test different authentication methods with Community Solid Server.
"""

import requests
from dotenv import load_dotenv
import os
import base64
import json

load_dotenv()

POD_URL = os.getenv("SOLID_POD_URL", "http://localhost:3000/maassenhochrath@gmail.com/")
CLIENT_ID = os.getenv("SOLID_CLIENT_ID")
CLIENT_SECRET = os.getenv("SOLID_CLIENT_SECRET")
BASE_URL = "http://localhost:3000"

print("=" * 60)
print("🔍 Testing Solid Authentication Methods")
print("=" * 60)

# Test 1: Check OpenID configuration
print("\n1️⃣  Checking OpenID configuration...")
try:
    response = requests.get(f"{BASE_URL}/.well-known/openid-configuration")
    if response.status_code == 200:
        config = response.json()
        print(f"  ✅ Found OpenID config")
        print(f"     Token endpoint: {config.get('token_endpoint', 'N/A')}")
        print(f"     Grant types: {config.get('grant_types_supported', [])}")
    else:
        print(f"  ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: Try client credentials with token endpoint
print("\n2️⃣  Trying client credentials OAuth2 flow...")
if CLIENT_ID and CLIENT_SECRET:
    try:
        token_url = f"{BASE_URL}/idp/token/"
        data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
        response = requests.post(token_url, data=data)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"  ✅ Got access token!")
            access_token = token_data.get('access_token')
            print(f"     Token: {access_token[:30]}...")
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
else:
    print("  ⚠️  No client credentials configured")

# Test 3: Try DPoP token (if supported)
print("\n3️⃣  Checking DPoP support...")
try:
    response = requests.get(f"{BASE_URL}/.well-known/openid-configuration")
    if response.status_code == 200:
        config = response.json()
        dpop_supported = "dpop" in config.get("token_endpoint_auth_methods_supported", [])
        print(f"  DPoP supported: {dpop_supported}")
except:
    print("  ⚠️  Could not check DPoP support")

# Test 4: Try accessing pod with various auth methods
print("\n4️⃣  Testing pod access...")
test_url = POD_URL.rstrip('/') + '/'
print(f"  URL: {test_url}")

# No auth
print("\n  a) No authentication:")
try:
    response = requests.get(test_url)
    print(f"     Status: {response.status_code}")
except Exception as e:
    print(f"     Error: {e}")

# Basic auth
print("\n  b) Basic authentication:")
if CLIENT_ID and CLIENT_SECRET:
    try:
        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers = {'Authorization': f"Basic {encoded}"}
        response = requests.get(test_url, headers=headers)
        print(f"     Status: {response.status_code}")
    except Exception as e:
        print(f"     Error: {e}")

print("\n" + "=" * 60)
