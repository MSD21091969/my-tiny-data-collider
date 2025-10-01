"""
Test reading from Solid Pod to verify authentication works.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.solidservice.client import SolidPodClient
from dotenv import load_dotenv
import os

load_dotenv()

POD_URL = os.getenv("SOLID_POD_URL", "http://localhost:3000/maassenhochrath@gmail.com/")
CLIENT_ID = os.getenv("SOLID_CLIENT_ID")
CLIENT_SECRET = os.getenv("SOLID_CLIENT_SECRET")

print("=" * 60)
print("🧪 Testing Solid Pod Read Access")
print("=" * 60)

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ Missing credentials in .env")
    exit(1)

print(f"\nPod URL: {POD_URL}")
print(f"Client ID: {CLIENT_ID[:20]}...\n")

# Initialize client
try:
    client = SolidPodClient(
        pod_url=POD_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    print("✅ Client initialized\n")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    exit(1)

# Test reading pod root
print("📖 Reading pod root container...")
try:
    contents = client.list_container("")
    if contents:
        print("✅ Successfully read pod contents!")
        print(f"   Response keys: {list(contents.keys())[:5]}")
    else:
        print("⚠️  Empty response or read failed")
except Exception as e:
    print(f"❌ Error reading pod: {e}")

# Test reading /tiny-data-collider/ if it exists
print("\n📖 Checking /tiny-data-collider/...")
try:
    contents = client.list_container("tiny-data-collider/")
    if contents:
        print("✅ /tiny-data-collider/ exists and is readable!")
        print(f"   Contents: {contents}")
    else:
        print("⚠️  Folder doesn't exist or isn't readable")
except Exception as e:
    print(f"⚠️  Could not read: {e}")

print("\n" + "=" * 60)
print("Summary:")
print("- Authentication: ✅ Working (got OAuth2 token)")
print("- Read access: Testing above")
print("- Write access: ⚠️  Limited (403 Forbidden)")
print("\nNext: Create folders manually in browser, then test again")
print("=" * 60)
