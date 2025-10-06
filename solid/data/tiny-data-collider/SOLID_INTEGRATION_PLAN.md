# Solid Server Integration Plan
## Connecting Tiny Data Collider to Solid

---

## 🎯 Goal

Integrate your Tiny Data Collider with a Solid Pod so:
- Your data lives in YOUR Solid Pod (not just Firestore)
- Other Solid apps can access your data (with YOUR permission)
- You maintain full data sovereignty
- Your collider becomes Solid-compatible

---

## 🔧 Architecture Options

### Option 1: Dual Persistence (Recommended for Start)

```
Your Collider
    ├─ Primary Storage: Firestore (fast, proven)
    ├─ Mirror Storage: Solid Pod (interoperability)
    └─ Sync Strategy: Write to both, read from Firestore

Pros:
- Keep your existing architecture
- Add Solid gradually
- Firestore performance maintained
- Solid interoperability gained

Cons:
- Two systems to manage
- Sync complexity
```

### Option 2: Solid-First (Future State)

```
Your Collider
    ├─ Primary Storage: Solid Pod (all data)
    ├─ Cache Layer: Redis/local (performance)
    └─ Strategy: Read from pod, cache aggressively

Pros:
- True Solid-native
- Maximum interoperability
- No vendor lock-in

Cons:
- Performance considerations
- More complex queries
- Requires Solid server maturity
```

### Option 3: Hybrid Intelligence Layer

```
Solid Pod (Raw Data)
    └─ Documents, contracts, notes
    
Your Collider (Intelligence)
    ├─ Read from Solid Pod
    ├─ Process with YOUR tools
    ├─ Generate insights (embeddings, metadata, knowledge graph)
    ├─ Write insights BACK to Solid Pod
    └─ Other apps can use YOUR enriched data

Pros:
- Best of both worlds
- Solid for data portability
- Your collider adds intelligence
- Value-add to Solid ecosystem

Cons:
- Most complex
- Requires careful schema design
```

---

## 🛠️ Technical Setup

### Step 1: Choose Your Solid Server

#### Community Solid Server (Recommended)
```bash
# Install Community Solid Server
npm install -g @solid/community-server

# Run locally
npx @solid/community-server -p 3000

# Your pod will be at: http://localhost:3000/
```

#### Run in Docker
```bash
# docker-compose.yml
version: '3'
services:
  solid-server:
    image: solidproject/community-server:latest
    ports:
      - "3000:3000"
    volumes:
      - ./solid-data:/data
    environment:
      - CSS_CONFIG=config/file.json
```

---

### Step 2: Python Client for Solid

```bash
# Install Solid client library
pip install solid-python
# OR
pip install rdflib requests
```

---

### Step 3: Create Solid Client Service

```python
# src/solidservice/client.py
"""
Solid Pod client for Tiny Data Collider.
"""

from typing import Dict, Any, Optional
import requests
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, FOAF, DCTERMS
import logging

logger = logging.getLogger(__name__)


class SolidPodClient:
    """Client for interacting with Solid Pods."""
    
    def __init__(self, pod_url: str, webid: str, token: Optional[str] = None):
        """
        Initialize Solid Pod client.
        
        Args:
            pod_url: Base URL of your Solid Pod (e.g., http://localhost:3000/username/)
            webid: Your WebID (Solid identity)
            token: Authentication token (if required)
        """
        self.pod_url = pod_url.rstrip('/') + '/'
        self.webid = webid
        self.token = token
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    async def read_resource(self, path: str) -> Dict[str, Any]:
        """
        Read a resource from Solid Pod.
        
        Args:
            path: Relative path in pod (e.g., 'documents/contract.ttl')
        
        Returns:
            Parsed resource data
        """
        url = self.pod_url + path
        
        response = self.session.get(
            url,
            headers={'Accept': 'text/turtle'}
        )
        
        if response.status_code == 200:
            # Parse RDF data
            graph = Graph()
            graph.parse(data=response.text, format='turtle')
            
            return self._graph_to_dict(graph)
        else:
            logger.error(f"Failed to read {url}: {response.status_code}")
            return {}
    
    async def write_resource(
        self,
        path: str,
        data: Dict[str, Any],
        content_type: str = 'text/turtle'
    ) -> bool:
        """
        Write a resource to Solid Pod.
        
        Args:
            path: Relative path in pod
            data: Data to write
            content_type: Content type (default: Turtle RDF)
        
        Returns:
            Success status
        """
        url = self.pod_url + path
        
        # Convert data to RDF
        graph = self._dict_to_graph(data)
        serialized = graph.serialize(format='turtle')
        
        response = self.session.put(
            url,
            data=serialized,
            headers={'Content-Type': content_type}
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully wrote to {url}")
            return True
        else:
            logger.error(f"Failed to write to {url}: {response.status_code}")
            return False
    
    async def create_container(self, path: str) -> bool:
        """Create a container (folder) in Solid Pod."""
        url = self.pod_url + path
        
        response = self.session.put(
            url,
            headers={'Content-Type': 'text/turtle'}
        )
        
        return response.status_code in [200, 201]
    
    def _dict_to_graph(self, data: Dict[str, Any]) -> Graph:
        """Convert Python dict to RDF graph."""
        graph = Graph()
        
        # Define namespaces
        TDC = Namespace("https://tiny-data-collider.org/ns#")
        graph.bind("tdc", TDC)
        
        # Simple conversion (can be enhanced)
        subject = URIRef(self.pod_url + "resource")
        
        for key, value in data.items():
            predicate = TDC[key]
            
            if isinstance(value, str):
                graph.add((subject, predicate, Literal(value)))
            elif isinstance(value, dict):
                # Nested objects (simplified)
                nested_subject = URIRef(self.pod_url + f"resource/{key}")
                graph.add((subject, predicate, nested_subject))
                for nested_key, nested_value in value.items():
                    graph.add((
                        nested_subject,
                        TDC[nested_key],
                        Literal(nested_value)
                    ))
        
        return graph
    
    def _graph_to_dict(self, graph: Graph) -> Dict[str, Any]:
        """Convert RDF graph to Python dict."""
        result = {}
        
        # Simple extraction (can be enhanced)
        for subj, pred, obj in graph:
            key = str(pred).split('#')[-1]
            value = str(obj)
            result[key] = value
        
        return result


# Example usage:
async def example_solid_integration():
    """Example of using Solid Pod with Tiny Data Collider."""
    
    # 1. Connect to your Solid Pod
    client = SolidPodClient(
        pod_url="http://localhost:3000/your-username/",
        webid="http://localhost:3000/your-username/profile/card#me"
    )
    
    # 2. Create a container for your collider data
    await client.create_container("tiny-data-collider/")
    await client.create_container("tiny-data-collider/sessions/")
    await client.create_container("tiny-data-collider/casefiles/")
    
    # 3. Write a casefile to Solid Pod
    casefile_data = {
        "id": "cf_251001_abc123",
        "title": "Test Casefile",
        "created_at": "2025-10-01T12:00:00",
        "metadata": {
            "tags": ["test", "demo"]
        }
    }
    
    await client.write_resource(
        "tiny-data-collider/casefiles/cf_251001_abc123.ttl",
        casefile_data
    )
    
    # 4. Read it back
    retrieved = await client.read_resource(
        "tiny-data-collider/casefiles/cf_251001_abc123.ttl"
    )
    
    print(f"Retrieved from Solid Pod: {retrieved}")
```

---

### Step 4: Integration with Existing Services

```python
# src/casefileservice/service.py (enhanced)
"""
Enhanced CasefileService with Solid integration.
"""

from ..solidservice.client import SolidPodClient
from ..coreservice.config import get_config

class CasefileService:
    def __init__(self):
        self.repository = CasefileRepository()  # Existing Firestore repo
        
        # Add Solid client
        config = get_config()
        if config.get("SOLID_ENABLED", False):
            self.solid_client = SolidPodClient(
                pod_url=config["SOLID_POD_URL"],
                webid=config["SOLID_WEBID"],
                token=config.get("SOLID_TOKEN")
            )
        else:
            self.solid_client = None
    
    async def create_casefile(self, casefile: CasefileModel) -> str:
        """Create casefile in Firestore AND Solid Pod."""
        
        # 1. Create in Firestore (existing logic)
        casefile_id = await self.repository.create_casefile(casefile)
        
        # 2. Mirror to Solid Pod (if enabled)
        if self.solid_client:
            await self.solid_client.write_resource(
                f"tiny-data-collider/casefiles/{casefile_id}.ttl",
                casefile.model_dump()
            )
            logger.info(f"Mirrored casefile {casefile_id} to Solid Pod")
        
        return casefile_id
    
    async def get_casefile(self, casefile_id: str) -> CasefileModel:
        """Get casefile from Firestore (with Solid backup option)."""
        
        # Try Firestore first
        casefile = await self.repository.get_casefile(casefile_id)
        
        if not casefile and self.solid_client:
            # Fallback to Solid Pod
            data = await self.solid_client.read_resource(
                f"tiny-data-collider/casefiles/{casefile_id}.ttl"
            )
            if data:
                casefile = CasefileModel.model_validate(data)
                logger.info(f"Retrieved casefile {casefile_id} from Solid Pod")
        
        return casefile
```

---

## 📝 Configuration

```python
# .env (add these)
SOLID_ENABLED=true
SOLID_POD_URL=http://localhost:3000/your-username/
SOLID_WEBID=http://localhost:3000/your-username/profile/card#me
SOLID_TOKEN=your_auth_token_here  # Optional, if auth required
```

---

## 🔒 Access Control (Solid ACL)

```python
# src/solidservice/acl.py
"""
Manage Solid Access Control Lists.
"""

class SolidACLManager:
    """Manage permissions for Solid Pod resources."""
    
    async def set_resource_permissions(
        self,
        resource_path: str,
        permissions: Dict[str, list]
    ):
        """
        Set who can access a resource.
        
        Example:
            permissions = {
                "owner": ["read", "write", "control"],  # You
                "public": [],  # Nobody by default
                "trusted_peers": ["read"]  # Specific peers can read
            }
        """
        acl_path = resource_path + ".acl"
        
        acl_graph = self._build_acl_graph(resource_path, permissions)
        
        await self.solid_client.write_resource(
            acl_path,
            acl_graph,
            content_type='text/turtle'
        )
```

---

## 🧪 Testing Plan

1. **Install Solid Server**
   ```bash
   npm install -g @solid/community-server
   npx @solid/community-server -p 3000
   ```

2. **Create Your Pod**
   - Visit http://localhost:3000/
   - Sign up / create pod
   - Note your WebID

3. **Install Python Dependencies**
   ```bash
   pip install rdflib requests
   ```

4. **Test Basic Operations**
   ```python
   # Test script
   python scripts/test_solid_integration.py
   ```

5. **Verify Data in Both Places**
   - Check Firestore (existing)
   - Check Solid Pod (browse at http://localhost:3000/)

---

## 🎯 Next Steps

1. **Tell me which Solid server you found**
2. **Clarify what you mean by "fork"**
3. **We'll build the integration together!**

---

## 📚 Resources

- **Solid Spec:** https://solidproject.org/TR/protocol
- **Community Solid Server:** https://github.com/CommunitySolidServer/CommunitySolidServer
- **Python RDF Library:** https://rdflib.readthedocs.io/
- **Solid Tutorial:** https://solidproject.org/developers/tutorials/getting-started

---

**Ready when you are!** 🚀
