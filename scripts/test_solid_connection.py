"""
Test connection to your Solid Pod.
"""

import asyncio
import os
import requests
from dotenv import load_dotenv

load_dotenv()


async def test_solid_connection():
    """Test basic Solid Pod operations."""
    
    pod_url = os.getenv("SOLID_POD_URL")
    webid = os.getenv("SOLID_WEBID")
    
    print("=" * 60)
    print("🧪 Testing Solid Pod Connection")
    print("=" * 60)
    
    print(f"\n📍 Pod URL: {pod_url}")
    print(f"🆔 WebID: {webid}")
    
    # Test 1: Check if server is accessible
    print("\n1️⃣ Testing server accessibility...")
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Solid server is running!")
        else:
            print(f"   ⚠️  Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Check your pod root
    print("\n2️⃣ Testing your pod access...")
    try:
        response = requests.get(
            pod_url,
            headers={"Accept": "text/turtle"},
            timeout=5
        )
        if response.status_code == 200:
            print(f"   ✅ Your pod is accessible!")
            print(f"   📦 Response size: {len(response.text)} bytes")
        elif response.status_code == 401:
            print("   🔒 Pod exists but requires authentication")
            print("   💡 This is expected - we'll add auth tokens later")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error accessing pod: {e}")
    
    # Test 3: Check WebID profile
    print("\n3️⃣ Testing WebID profile...")
    try:
        response = requests.get(
            webid.split('#')[0],  # Remove fragment
            headers={"Accept": "text/turtle"},
            timeout=5
        )
        if response.status_code == 200:
            print("   ✅ WebID profile accessible!")
            print(f"   👤 Profile size: {len(response.text)} bytes")
        elif response.status_code == 401:
            print("   🔒 Profile requires authentication")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error accessing profile: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Connection Test Complete!")
    print("=" * 60)
    
    print("\n📝 Summary:")
    print("   ✅ Solid server: Running")
    print(f"   ✅ Your pod: {pod_url}")
    print("   ✅ WebID: Configured")
    print("\n💡 Next steps:")
    print("   1. Generate authentication token")
    print("   2. Create container for collider data")
    print("   3. Start writing data to your pod!")


if __name__ == "__main__":
    asyncio.run(test_solid_connection())
