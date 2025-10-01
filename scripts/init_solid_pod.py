"""
Initialize your Solid Pod structure for Tiny Data Collider.
Creates folders using authenticated Solid client.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.solidservice.client import SolidPodClient
from dotenv import load_dotenv
import os

load_dotenv()

POD_URL = os.getenv("SOLID_POD_URL", "http://localhost:3000/maassenhochrath@gmail.com/")
CLIENT_ID = os.getenv("SOLID_CLIENT_ID")
CLIENT_SECRET = os.getenv("SOLID_CLIENT_SECRET")

def main():
    print("=" * 60)
    print("🏗️  Initializing Tiny Data Collider Pod Structure")
    print("=" * 60)
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Missing credentials!")
        print("   Please set SOLID_CLIENT_ID and SOLID_CLIENT_SECRET in .env")
        return
    
    print(f"🔑 Using client credentials authentication")
    print(f"   Client ID: {CLIENT_ID[:20]}...")
    print(f"\nPod URL: {POD_URL}\n")
    
    # Initialize Solid client
    try:
        client = SolidPodClient(
            pod_url=POD_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        print("✅ Solid client initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return
    
    folders = [
        "tiny-data-collider/",
        "tiny-data-collider/casefiles/",
        "tiny-data-collider/sessions/",
        "tiny-data-collider/corpuses/",
        "tiny-data-collider/corpuses/legal/",
        "tiny-data-collider/corpuses/financial/",
        "tiny-data-collider/corpuses/technical/",
        "tiny-data-collider/metadata/",
        "tiny-data-collider/insights/",
    ]
    
    success_count = 0
    
    for folder in folders:
        print(f"Creating: {folder}")
        try:
            result = client.create_container(folder)
            if result:
                print(f"  ✅ Created successfully")
                success_count += 1
            else:
                print(f"  ⚠️  Failed (see logs)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ Created {success_count}/{len(folders)} folders")
    
    if success_count == len(folders):
        print("\n🎉 Pod structure initialized successfully!")
        print("\nNext steps:")
        print("1. Browse your pod at:", POD_URL)
        print("2. Test Python integration with read/write operations")
        print("3. Configure mobile wallet to connect to your pod")
    elif success_count == 0:
        print("\n⚠️  No folders created. Check authentication.")
        print("\nTroubleshooting:")
        print("1. Verify credentials in .env are correct")
        print("2. Check that Solid server is running (docker ps)")
        print("3. Try accessing pod in browser:", POD_URL)
    
    print("=" * 60)

if __name__ == "__main__":
    main()
