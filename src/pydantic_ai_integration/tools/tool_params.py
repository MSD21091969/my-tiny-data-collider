"""
Parameter models for MDS tools.

Each tool gets its own Pydantic model that defines:
- WHAT parameters it accepts (field names and types)
- WHAT constraints apply (ge=, le=, min_length=, etc.) - the GUARDRAILS
- WHAT documentation to show (Field descriptions)

These models serve as:
1. Validation schemas (Pydantic enforces at runtime)
2. Type hints (MyPy/Pylance check at compile time)
3. OpenAPI documentation (FastAPI generates Swagger UI forms)

FIELD ANNOTATIONS:
Use Field() to add guardrails and metadata:
- ge=, le= : Numeric min/max (guardrail)
- min_length=, max_length= : String length constraints (guardrail)
- pattern= : Regex validation (guardrail)
- description= : API documentation (metadata)
- examples= : Show usage patterns (metadata)
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class ExampleToolParams(BaseModel):
    """
    Parameters for example_tool.
    
    METADATA:
    - Tool: example_tool
    - Purpose: Process numeric values (square, cube, even/odd)
    
    GUARDRAILS:
    - value: Must be >= 0 (no negative numbers)
    - value: Must be <= 10000 (prevent overflow)
    """
    value: int = Field(
        ...,
        ge=0,
        le=10000,
        description="The numeric value to process",
        examples=[42, 100, 1000]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "value": 42
            }
        }


class AnotherExampleToolParams(BaseModel):
    """
    Parameters for another_example_tool.
    
    METADATA:
    - Tool: another_example_tool
    - Purpose: Generate personalized greeting messages
    
    GUARDRAILS:
    - name: Min 1 char (can't be empty)
    - name: Max 100 chars (prevent abuse)
    - count: Between 1-10 (reasonable range)
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name to use in greeting messages",
        examples=["Alice", "Bob", "Dr. Smith"]
    )
    count: int = Field(
        1,
        ge=1,
        le=10,
        description="Number of messages to generate",
        examples=[1, 3, 5]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Alice",
                "count": 3
            }
        }


class AdvancedToolParams(BaseModel):
    """
    Parameters for advanced_tool.
    
    METADATA:
    - Tool: advanced_tool
    - Purpose: Complex data processing with options
    
    GUARDRAILS:
    - input_data: Must be provided (required)
    - options.mode: Only specific values allowed
    - options.include_stats: Must be boolean
    """
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data dictionary to process",
        examples=[
            {"name": "test", "value": 42},
            {"text": "hello", "number": 123}
        ]
    )
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional processing configuration",
        examples=[
            {"mode": "standard", "include_stats": True},
            {"mode": "numeric", "include_stats": False}
        ]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_data": {"name": "test", "value": 42},
                "options": {"mode": "standard", "include_stats": True}
            }
        }


# NOTES ON ADDING NEW TOOL PARAMETERS:
#
# 1. Create a new class inheriting from BaseModel
# 2. Name it <ToolName>Params (convention)
# 3. Add Field() for each parameter with:
#    - Type annotation (int, str, bool, Dict, etc.)
#    - ... or default value
#    - Constraints (ge=, le=, min_length=, pattern=, etc.) <- GUARDRAILS
#    - description= for API docs <- METADATA
#    - examples= for Swagger UI <- METADATA
# 4. Add Config with json_schema_extra example <- METADATA
#
# Example:
#   class NewToolParams(BaseModel):
#       field_name: str = Field(
#           ...,                    # Required (no default)
#           min_length=1,           # GUARDRAIL
#           max_length=50,          # GUARDRAIL
#           description="What it does",  # METADATA
#           examples=["example1"]   # METADATA
#       )
