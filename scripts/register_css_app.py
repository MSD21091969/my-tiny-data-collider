"""
Alternative approach: Create a registered client application in CSS.
This guides you through registering an app with proper redirect URIs.
"""

print("=" * 60)
print("🔧 CSS Application Registration Guide")
print("=" * 60)

print("\n📋 We need to register our application with CSS.")
print("   This gives it proper OAuth2 credentials.\n")

print("Step 1: Open CSS Account Page")
print("   http://localhost:3000/.account/\n")

print("Step 2: Look for 'Applications' or 'Registered Clients'")
print("   (This might be under a different menu)\n")

print("Step 3: Register a new application with:")
print("   • Name: Tiny Data Collider")
print("   • Redirect URI: http://127.0.0.1:8765/callback")
print("   • Scopes: openid, webid, offline_access\n")

print("Step 4: You'll get:")
print("   • Client ID")
print("   • Client Secret (if provided)\n")

print("Step 5: Add to .env:")
print("   SOLID_APP_CLIENT_ID=<the_client_id>")
print("   SOLID_APP_CLIENT_SECRET=<the_secret>\n")

print("=" * 60)
print("💡 Alternative: Manual Folder Creation")
print("=" * 60)
print("\nIf CSS doesn't support app registration, we can:")
print("1. Create folders manually in browser")
print("2. Set ACL permissions to allow public/authenticated access")
print("3. Python can then read/write to those folders\n")

print("Which would you prefer?")
print("  A) Try to find app registration in CSS")
print("  B) Create folders manually and continue")
print("=" * 60)
