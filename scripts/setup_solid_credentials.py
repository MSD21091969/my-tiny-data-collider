"""
Helper script to display CSS credential setup instructions.
"""

print("=" * 60)
print("🔐 CSS Client Credentials Setup")
print("=" * 60)

print("\n📋 Open these URLs in your browser:\n")

print("1️⃣  Login page:")
print("   http://localhost:3000/.account/login")

print("\n2️⃣  Account settings (after login):")
print("   http://localhost:3000/.account/")

print("\n3️⃣  Look for one of these sections:")
print("   • 'Client Credentials'")
print("   • 'API Tokens'")
print("   • 'Application Credentials'")
print("   • 'Token Manager'")

print("\n🎯 When creating new credentials:")
print("   ✓ Give it a descriptive name: 'tiny-collider-full-access'")
print("   ✓ Look for permission/scope settings")
print("   ✓ Enable 'Read' and 'Write' if available")
print("   ✓ Some versions let you specify WebID:")
print("     http://localhost:3000/maassenhochrath@gmail.com/profile/card#me")

print("\n📝 After creating:")
print("   1. Copy the Client ID (starts with 'vscode_' or similar)")
print("   2. Copy the Client Secret (long hex string)")
print("   3. Update these lines in .env:")
print("      SOLID_CLIENT_ID=<paste_client_id>")
print("      SOLID_CLIENT_SECRET=<paste_client_secret>")

print("\n🔄 Then run:")
print("   python scripts\\init_solid_pod.py")

print("\n" + "=" * 60)
print("⚠️  Note: If client credentials still don't work, we'll")
print("   implement browser-based authentication instead")
print("=" * 60)
