# Tool YAML

**Variables:** `{{METHOD}}` `{{DOMAIN}}` `{{SUBDOMAIN}}` `{{ACTION}}`

**Constraints:**
- Inherit params from method (no manual duplication)
- Use tool_schema_v2.yaml structure
- Location: `config/toolsets/{domain}/{subdomain}/`

**Template:**
```yaml
name: {{METHOD}}
description: "Brief description"
category: {{DOMAIN}}
version: "1.0.0"

classification:
  domain: {{DOMAIN}}
  subdomain: {{SUBDOMAIN}}
  capability: {{ACTION}}
  complexity: atomic
  maturity: stable
  integration_tier: internal

implementation:
  type: api_call
  api_call:
    method_name: {{METHOD}}
```

**Generate:** Run `python scripts/generate_tools.py {{METHOD}}`
