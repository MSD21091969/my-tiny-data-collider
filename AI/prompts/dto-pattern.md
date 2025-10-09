# DTO Pattern

**Variables:** `{{ACTION}}` `{{ENTITY}}`

**Constraints:**
- R-A-R pattern (Request/Response with Payload)
- BaseRequest/BaseResponse generics
- Payload = business data only
- Location: `src/pydantic_models/operations/`

**Template:**
```python
from pydantic import BaseModel, Field
from typing import Literal
from ..base import BaseRequest, BaseResponse

class {{ACTION}}{{ENTITY}}Payload(BaseModel):
    field1: str = Field(..., description="Description")
    field2: int = Field(default=0, ge=0)

class {{ACTION}}{{ENTITY}}Request(BaseRequest[{{ACTION}}{{ENTITY}}Payload]):
    operation: Literal["{{ACTION}}_{{ENTITY}}"] = "{{ACTION}}_{{ENTITY}}"

class {{ACTION}}{{ENTITY}}Response(BaseResponse[{{ACTION}}{{ENTITY}}Payload]):
    pass
```

**Rule:** Define params once in Payload, inherit everywhere.
