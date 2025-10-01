# Manual Pod Setup Guide

Since CSS client credentials have restricted write permissions, we'll create the folder structure manually via the browser interface.

## Step 1: Access Your Pod

Open in browser (should already be logged in):
```
http://localhost:3000/maassenhochrath@gmail.com/
```

## Step 2: Create Folder Structure

Using the CSS web interface, create these folders:

```
/tiny-data-collider/
├── casefiles/
├── sessions/
├── corpuses/
│   ├── legal/
│   ├── financial/
│   └── technical/
├── metadata/
└── insights/
```

### How to create folders in CSS:
1. Click on your pod root in the browser
2. Look for "New Folder" or similar button
3. Enter folder name (e.g., `tiny-data-collider`)
4. Repeat for each subfolder

## Step 3: Set Permissions (Optional - for development)

For each folder, you can set access control:

### Public Read/Write (Development Only - NOT for production):
- Allows Python to read/write without authentication
- Good for testing integration quickly
- **Remember to restrict later!**

### Authenticated Access (Recommended):
- Only authenticated apps can read/write
- Requires proper OAuth2 flow in Python
- More secure but more complex

## Step 4: Verify Structure

After creating folders manually, run this to verify:

```powershell
python scripts/test_solid_connection.py
```

## Step 5: Upload README

Once folders exist, you can upload the README:

```powershell
# TODO: Add upload script
```

## Alternative: Browser-Based Authentication

For full programmatic access with write permissions, we need to implement:

1. **Authorization Code Flow** (browser-based OAuth2)
   - User logs in via browser
   - App gets refresh token
   - Python can then create/modify resources

2. **Solid-OIDC Library** (if available for Python)
   - Handles complex auth flow
   - May require additional dependencies

## Current Status

✅ Pod server running
✅ Account created
✅ Client credentials generated
✅ OAuth2 client working (authentication successful)
⚠️  Client credentials have limited permissions (403 Forbidden)
⏳ Need manual folder creation OR full OAuth2 flow

## Next Steps

1. Create folders manually in browser (5 minutes)
2. Test Python read/write to existing folders
3. Implement full OAuth2 flow if programmatic creation is critical
4. Consider ACL (Access Control List) management for fine-grained permissions
