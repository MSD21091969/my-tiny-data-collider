# Setting Up Community Solid Server for Tiny Data Collider
## Step-by-Step Guide

---

## 📦 Prerequisites

- Node.js 18+ installed
- npm or yarn
- Your Tiny Data Collider project

---

## 🚀 Installation

### Option 1: Quick Start (Recommended)

```bash
# Install globally
npm install -g @solid/community-server

# Run with default config (stores data in ./.data/)
npx @solid/community-server -p 3000

# Server will start at http://localhost:3000
```

### Option 2: Docker (For Production)

```yaml
# docker-compose-solid.yml
version: '3.8'

services:
  solid-server:
    image: solidproject/community-server:latest
    container_name: tiny-collider-solid
    ports:
      - "3000:3000"
    volumes:
      - ./solid-data:/data
      - ./solid-config:/config
    environment:
      - CSS_CONFIG=/config/config.json
    restart: unless-stopped

  # Optional: Add your Tiny Data Collider FastAPI service
  collider-api:
    build: .
    container_name: tiny-collider-api
    ports:
      - "8000:8000"
    depends_on:
      - solid-server
    environment:
      - SOLID_POD_URL=http://solid-server:3000/
    restart: unless-stopped
```

```bash
# Run both services
docker-compose -f docker-compose-solid.yml up -d
```

### Option 3: Local Development Setup

```bash
# Clone Community Solid Server
git clone https://github.com/CommunitySolidServer/CommunitySolidServer.git
cd CommunitySolidServer

# Install dependencies
npm install

# Run in development mode
npm start
```

---

## 🔧 Configuration

### Custom Config File

Create `solid-config.json`:

```json
{
  "@context": "https://linkedsoftwaredependencies.org/bundles/npm/@solid/community-server/^7.0.0/components/context.jsonld",
  "import": [
    "css:config/app/main/default.json",
    "css:config/app/init/initialize-root.json",
    "css:config/http/handler/default.json",
    "css:config/http/middleware/websockets.json",
    "css:config/http/server-factory/http.json",
    "css:config/http/static/default.json",
    "css:config/identity/access/public.json",
    "css:config/identity/email/default.json",
    "css:config/identity/handler/default.json",
    "css:config/identity/ownership/token.json",
    "css:config/identity/pod/static.json",
    "css:config/identity/registration/enabled.json",
    "css:config/ldp/authentication/dpop-bearer.json",
    "css:config/ldp/authorization/webacl.json",
    "css:config/ldp/handler/default.json",
    "css:config/ldp/metadata-parser/default.json",
    "css:config/ldp/metadata-writer/default.json",
    "css:config/ldp/modes/default.json",
    "css:config/storage/backend/file.json",
    "css:config/storage/key-value/memory.json",
    "css:config/storage/middleware/default.json",
    "css:config/util/auxiliary/acl.json",
    "css:config/util/identifiers/suffix.json",
    "css:config/util/index/default.json",
    "css:config/util/logging/winston.json",
    "css:config/util/representation-conversion/default.json",
    "css:config/util/resource-locker/memory.json",
    "css:config/util/variables/default.json"
  ],
  "@graph": [
    {
      "comment": "Custom configuration for Tiny Data Collider"
    },
    {
      "@id": "urn:solid-server:default:ServerFactory",
      "@type": "BaseHttpServerFactory",
      "baseUrl": "http://localhost:3000/",
      "port": 3000
    },
    {
      "@id": "urn:solid-server:default:ResourceStore",
      "@type": "DataAccessorBasedStore",
      "identifierStrategy": { "@id": "urn:solid-server:default:IdentifierStrategy" },
      "auxiliaryStrategy": { "@id": "urn:solid-server:default:AuxiliaryStrategy" },
      "accessor": { "@id": "urn:solid-server:default:FileDataAccessor" }
    }
  ]
}
```

Run with custom config:
```bash
npx @solid/community-server -c solid-config.json
```

---

## 👤 Create Your Pod

### Via Web Interface

1. Start the server: `npx @solid/community-server -p 3000`
2. Open browser: http://localhost:3000
3. Click **"Create a Pod"** or **"Sign Up"**
4. Fill in details:
   - **Username:** `your-username` (will be your pod URL)
   - **Email:** your-email@example.com
   - **Password:** secure-password
5. Your pod will be created at: `http://localhost:3000/your-username/`
6. Your WebID will be: `http://localhost:3000/your-username/profile/card#me`

### Via Command Line (Automated)

```bash
# Create a pod programmatically
curl -X POST http://localhost:3000/idp/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "your-password",
    "confirmPassword": "your-password",
    "podName": "your-username",
    "register": true
  }'
```

---

## 🔐 Authentication

### Get Access Token

```bash
# Method 1: Client Credentials (for server-to-server)
curl -X POST http://localhost:3000/idp/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"

# Method 2: Use Solid-OIDC flow (for apps)
# See: https://solidproject.org/TR/oidc-primer
```

### Store Token in .env

```bash
# Add to .env
SOLID_POD_URL=http://localhost:3000/your-username/
SOLID_WEBID=http://localhost:3000/your-username/profile/card#me
SOLID_TOKEN=your_access_token_here
SOLID_ENABLED=true
```

---

## 🧪 Test Connection

### Python Test Script

```python
# scripts/test_solid_connection.py
"""Test connection to Community Solid Server."""

import asyncio
import requests
import os
from dotenv import load_dotenv

load_dotenv()


async def test_solid_connection():
    """Test basic Solid Pod operations."""
    
    pod_url = os.getenv("SOLID_POD_URL")
    token = os.getenv("SOLID_TOKEN")
    
    print(f"Testing connection to: {pod_url}")
    
    # Test 1: Read root container
    print("\n1. Reading root container...")
    response = requests.get(
        pod_url,
        headers={
            "Accept": "text/turtle",
            "Authorization": f"Bearer {token}" if token else ""
        }
    )
    
    if response.status_code == 200:
        print("✅ Successfully connected to Solid Pod!")
        print(f"Content:\n{response.text[:200]}...")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return
    
    # Test 2: Create a test resource
    print("\n2. Creating test resource...")
    test_data = """
    @prefix dc: <http://purl.org/dc/terms/> .
    @prefix tdc: <https://tiny-data-collider.org/ns#> .
    
    <> a tdc:TestResource ;
       dc:title "Test from Tiny Data Collider" ;
       dc:created "2025-10-01T12:00:00Z" .
    """
    
    response = requests.put(
        f"{pod_url}test/collider-test.ttl",
        data=test_data,
        headers={
            "Content-Type": "text/turtle",
            "Authorization": f"Bearer {token}" if token else ""
        }
    )
    
    if response.status_code in [200, 201]:
        print("✅ Successfully created test resource!")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return
    
    # Test 3: Read it back
    print("\n3. Reading test resource back...")
    response = requests.get(
        f"{pod_url}test/collider-test.ttl",
        headers={
            "Accept": "text/turtle",
            "Authorization": f"Bearer {token}" if token else ""
        }
    )
    
    if response.status_code == 200:
        print("✅ Successfully read test resource!")
        print(f"Content:\n{response.text}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    print("\n✅ All tests passed! Solid Pod is ready for Tiny Data Collider!")


if __name__ == "__main__":
    asyncio.run(test_solid_connection())
```

Run test:
```bash
python scripts/test_solid_connection.py
```

---

## 📁 Directory Structure

Your Solid Pod will have structure like:

```
http://localhost:3000/your-username/
├── profile/
│   └── card  (Your WebID profile)
├── private/
│   └── (Private data, only you can access)
├── public/
│   └── (Public data, anyone can read)
├── tiny-data-collider/
│   ├── casefiles/
│   │   ├── cf_251001_abc.ttl
│   │   └── cf_251001_xyz.ttl
│   ├── sessions/
│   │   ├── ts_251001_session1.ttl
│   │   └── ts_251001_session2.ttl
│   ├── corpuses/
│   │   ├── legal/
│   │   ├── financial/
│   │   └── technical/
│   └── metadata/
│       └── knowledge-graph.ttl
```

---

## 🔗 Next: Integrate with Tiny Data Collider

See `SOLID_INTEGRATION_PLAN.md` for:
- Python Solid client implementation
- Integration with existing services
- Dual persistence strategy
- Access control setup

---

## 📚 Resources

- **Community Solid Server Docs:** https://communitysolidserver.github.io/CommunitySolidServer/
- **Solid Protocol Spec:** https://solidproject.org/TR/protocol
- **Getting Started Guide:** https://solidproject.org/developers/tutorials/getting-started
- **GitHub Repo:** https://github.com/CommunitySolidServer/CommunitySolidServer

---

## 🚀 You're Ready!

1. ✅ Fork the Solid Data Wallet
2. ✅ Run Community Solid Server locally
3. ✅ Create your pod
4. ✅ Test connection
5. 🔄 Integrate with your Tiny Data Collider

**Let's collide some data!** 🚀
