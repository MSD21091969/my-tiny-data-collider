"""
Method definition model - parallel to tool_definition.py for service methods.

This module defines data structures for MANAGED_METHODS registry:
- MethodMetadata: WHAT the method is
- MethodBusinessRules: WHEN/WHERE to use it
- MethodDefinition: Complete method registration

Design mirrors tool_definition.py for consistency.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Type, Callable, Dict, Any, Optional, List, Awaitable
from enum import Enum
from datetime import datetime


class MethodParameterDef(BaseModel):
    """
    Definition of a method parameter.
    Extracted from Pydantic request model fields.
    """
    name: str = Field(..., description="Parameter name")
    param_type: str = Field(..., description="Python type hint as string")
    required: bool = Field(True, description="Whether parameter is required")
    description: Optional[str] = Field(None, description="Field description from Pydantic")
    default_value: Optional[Any] = Field(None, description="Default value if Optional")
    
    # Validation constraints (from Pydantic Field())
    min_value: Optional[float] = Field(None, description="Minimum value (ge constraint)")
    max_value: Optional[float] = Field(None, description="Maximum value (le constraint)")
    min_length: Optional[int] = Field(None, description="Minimum length (min_length constraint)")
    max_length: Optional[int] = Field(None, description="Maximum length (max_length constraint)")
    pattern: Optional[str] = Field(None, description="Regex pattern")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "casefile_id",
                "param_type": "str",
                "required": True,
                "description": "Casefile identifier",
                "pattern": "^cf_[a-zA-Z0-9]+$"
            }
        }
    )


class MethodMetadata(BaseModel):
    """
    Pure metadata about a service method - the WHAT.
    
    Used for:
    - Discovery (listing methods by classification)
    - Documentation (API reference generation)
    - ToolFactory validation (api_call.method_name exists)
    """
    name: str = Field(..., description="Method name (e.g., 'create_casefile')")
    display_name: Optional[str] = Field(None, description="Human-friendly name")
    description: str = Field(..., description="What this method does")
    service_name: str = Field(..., description="Service class name (e.g., 'CasefileService')")
    module_path: str = Field(..., description="Full module path (e.g., 'src.casefileservice.service')")
    version: str = Field("1.0.0", description="Method version for compatibility")
    
    # Classification (aligns with YAML schema)
    domain: str = Field(..., description="Domain: workspace, communication, automation")
    subdomain: str = Field(..., description="Subdomain: casefile, gmail, tool_session, etc.")
    capability: str = Field(..., description="Capability: create, read, update, delete, process, search")
    complexity: str = Field(..., description="Complexity: atomic, composite, pipeline")
    maturity: str = Field(..., description="Maturity: stable, beta, alpha")
    integration_tier: str = Field(..., description="Integration: internal, external, hybrid")
    
    # Documentation
    docs_url: Optional[str] = Field(None, description="Link to method documentation")
    signature: Optional[str] = Field(None, description="Full method signature")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "create_casefile",
                "display_name": "Create Casefile",
                "description": "Creates new casefile with metadata",
                "service_name": "CasefileService",
                "module_path": "src.casefileservice.service",
                "domain": "workspace",
                "subdomain": "casefile",
                "capability": "create",
                "complexity": "atomic",
                "maturity": "stable",
                "integration_tier": "internal"
            }
        }
    )


class MethodBusinessRules(BaseModel):
    """
    Business logic for method execution - the WHEN/WHERE.
    
    Controls:
    - Availability (enabled, deprecated)
    - Access control (permissions, casefile requirements)
    - Execution constraints (timeout)
    - Versioning (deprecation metadata)
    """
    enabled: bool = Field(True, description="Whether method is available")
    deprecated: bool = Field(False, description="Whether method is deprecated")
    deprecation_message: Optional[str] = Field(None, description="Deprecation notice")
    deprecated_since: Optional[str] = Field(None, description="Version when deprecated (e.g., '1.5.0')")
    removal_version: Optional[str] = Field(None, description="Version when method will be removed (e.g., '2.0.0')")
    replacement_method: Optional[str] = Field(None, description="Recommended replacement method name")
    
    # Access control
    requires_auth: bool = Field(True, description="Authentication required")
    required_permissions: List[str] = Field(
        default_factory=list,
        description="Permissions needed (e.g., ['casefiles:write'])"
    )
    requires_casefile: bool = Field(False, description="Casefile context required")
    casefile_permission_level: Optional[str] = Field(
        None,
        description="Required casefile permission: read, write, admin"
    )
    
    # Execution constraints
    timeout_seconds: int = Field(30, description="Max execution time")
    max_retries: int = Field(0, description="Retry attempts on failure")
    
    # Dependencies
    dependencies: List[str] = Field(
        default_factory=list,
        description="Other methods/services this depends on"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": True,
                "requires_auth": True,
                "required_permissions": ["casefiles:write"],
                "requires_casefile": False,
                "timeout_seconds": 30
            }
        }
    )


class MethodModels(BaseModel):
    """
    Request/Response Pydantic models for method.
    Links to pydantic_models/operations/.
    """
    request_model_name: str = Field(..., description="Request model class name")
    request_model_path: str = Field(..., description="Full import path to request model")
    response_model_name: str = Field(..., description="Response model class name")
    response_model_path: str = Field(..., description="Full import path to response model")
    
    # Optional: actual model classes (if loaded)
    request_model_class: Optional[Type[BaseModel]] = Field(None, description="Request model class reference")
    response_model_class: Optional[Type[BaseModel]] = Field(None, description="Response model class reference")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "request_model_name": "CreateCasefileRequest",
                "request_model_path": "src.pydantic_models.operations.casefile_ops",
                "response_model_name": "CreateCasefileResponse",
                "response_model_path": "src.pydantic_models.operations.casefile_ops"
            }
        }
    )


class ManagedMethodDefinition(BaseModel):
    """
    Complete method definition for MANAGED_METHODS registry.
    
    Parallel to ManagedToolDefinition in tool_definition.py.
    Stores all metadata, business rules, models, and implementation reference.
    """
    metadata: MethodMetadata = Field(..., description="Method metadata (WHAT)")
    business_rules: MethodBusinessRules = Field(..., description="Business rules (WHEN/WHERE)")
    parameters: List[MethodParameterDef] = Field(
        default_factory=list,
        description="Method parameters extracted from request model"
    )
    models: MethodModels = Field(..., description="Request/Response model references")
    
    # Implementation reference (not the actual method, just metadata)
    implementation_class: str = Field(..., description="Service class containing method")
    implementation_method: str = Field(..., description="Method name in service class")
    
    # Registration tracking
    registered_at: datetime = Field(default_factory=datetime.now, description="Registration timestamp")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "metadata": {
                    "name": "create_casefile",
                    "service_name": "CasefileService",
                    "module_path": "src.casefileservice.service",
                    "domain": "workspace",
                    "subdomain": "casefile",
                    "capability": "create",
                    "complexity": "atomic",
                    "maturity": "stable",
                    "integration_tier": "internal",
                    "description": "Creates new casefile"
                },
                "business_rules": {
                    "enabled": True,
                    "requires_auth": True,
                    "required_permissions": ["casefiles:write"],
                    "timeout_seconds": 30
                },
                "parameters": [
                    {
                        "name": "title",
                        "param_type": "str",
                        "required": True,
                        "description": "Casefile title"
                    }
                ],
                "models": {
                    "request_model_name": "CreateCasefileRequest",
                    "request_model_path": "src.pydantic_models.operations.casefile_ops",
                    "response_model_name": "CreateCasefileResponse",
                    "response_model_path": "src.pydantic_models.operations.casefile_ops"
                },
                "implementation_class": "CasefileService",
                "implementation_method": "create_casefile"
            }
        }
    )
    
    def get_hierarchical_path(self) -> str:
        """
        Returns hierarchical path like tool_decorator.get_hierarchical_tool_path().
        Format: {domain}.{subdomain}.{capability}_{method_name}
        Example: workspace.casefile.create_casefile
        """
        return f"{self.metadata.domain}.{self.metadata.subdomain}.{self.metadata.name}"
    
    def get_classification(self) -> Dict[str, str]:
        """
        Returns classification dict matching YAML schema.
        """
        return {
            "domain": self.metadata.domain,
            "subdomain": self.metadata.subdomain,
            "capability": self.metadata.capability,
            "complexity": self.metadata.complexity,
            "maturity": self.metadata.maturity,
            "integration_tier": self.metadata.integration_tier
        }
    
    def to_yaml_compatible(self) -> Dict[str, Any]:
        """
        Exports method definition in YAML-compatible format.
        Can be used for methods_inventory_v1.yaml generation.
        """
        return {
            "name": self.metadata.name,
            "service": self.metadata.service_name,
            "module": self.metadata.module_path,
            "classification": self.get_classification(),
            "description": self.metadata.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.param_type,
                    "required": p.required,
                    "description": p.description
                }
                for p in self.parameters
            ],
            "models": {
                "request": self.models.request_model_name,
                "response": self.models.response_model_name
            },
            "business_rules": {
                "enabled": self.business_rules.enabled,
                "requires_auth": self.business_rules.requires_auth,
                "required_permissions": self.business_rules.required_permissions,
                "requires_casefile": self.business_rules.requires_casefile,
                "timeout_seconds": self.business_rules.timeout_seconds
            },
            "version": self.metadata.version
        }
