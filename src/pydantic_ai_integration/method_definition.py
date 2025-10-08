"""
Method definition model - SLIM VERSION for MANAGED_METHODS registry.

After R-A-R pattern implementation, all validation/constraints live in Pydantic Request models.
This registry stores only execution essentials + classification metadata.

DELETED (40+ fields → 16 fields):
- MethodParameterDef: Extract on-demand from request_model_class
- MethodMetadata: Flattened into parent
- MethodModels: Flattened into parent  
- MethodBusinessRules: All unused (auth/permissions handled in R-A-R models)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Type, Dict, Any
from datetime import datetime


class MethodParameterDef(BaseModel):
    """
    Parameter definition for Tool inheritance only.
    NOT stored in registry - extracted on-demand from request_model_class.
    """
    name: str
    param_type: str
    required: bool
    description: str | None = None
    default_value: Any = None
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None


class ManagedMethodDefinition(BaseModel):
    """
    SLIM method definition for MANAGED_METHODS registry.
    16 fields - pure essentials only.
    """
    # Identity
    name: str = Field(..., description="Method name (e.g., 'create_casefile')")
    description: str = Field(..., description="What this method does")
    version: str = Field("1.0.0", description="Method version")
    
    # Classification (YAML schema requirement)
    domain: str = Field(..., description="Domain: workspace, communication, automation")
    subdomain: str = Field(..., description="Subdomain: casefile, gmail, tool_session, etc.")
    capability: str = Field(..., description="Capability: create, read, update, delete, process, search")
    complexity: str = Field(..., description="Complexity: atomic, composite, pipeline")
    maturity: str = Field(..., description="Maturity: stable, beta, alpha")
    integration_tier: str = Field(..., description="Integration: internal, external, hybrid")
    
    # Execution (essential)
    request_model_class: Type[BaseModel] | None = Field(None, description="Pydantic request model")
    response_model_class: Type[BaseModel] | None = Field(None, description="Pydantic response model")
    implementation_class: str = Field(..., description="Service class name")
    implementation_method: str = Field(..., description="Method name in service")
    
    # Tracking
    registered_at: datetime = Field(default_factory=datetime.now, description="Registration timestamp")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "create_casefile",
                "description": "Creates new casefile with metadata",
                "version": "1.0.0",
                "domain": "workspace",
                "subdomain": "casefile",
                "capability": "create",
                "complexity": "atomic",
                "maturity": "stable",
                "integration_tier": "internal",
                "implementation_class": "CasefileService",
                "implementation_method": "create_casefile"
            }
        }
    )
    
    def get_hierarchical_path(self) -> str:
        """
        Returns hierarchical path: {domain}.{subdomain}.{name}
        Example: workspace.casefile.create_casefile
        """
        return f"{self.domain}.{self.subdomain}.{self.name}"
    
    def get_classification(self) -> Dict[str, str]:
        """Returns classification dict matching YAML schema."""
        return {
            "domain": self.domain,
            "subdomain": self.subdomain,
            "capability": self.capability,
            "complexity": self.complexity,
            "maturity": self.maturity,
            "integration_tier": self.integration_tier
        }
    
    def to_yaml_compatible(self) -> Dict[str, Any]:
        """
        Exports method definition in YAML-compatible format.
        Parameters extracted on-demand (not stored).
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "classification": self.get_classification(),
            "models": {
                "request": self.request_model_class.__name__,
                "response": self.response_model_class.__name__
            },
            "implementation": {
                "class": self.implementation_class,
                "method": self.implementation_method
            }
        }
