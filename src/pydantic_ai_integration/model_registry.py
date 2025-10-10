"""
Model Registry - Discovery and validation for Pydantic models
Created: 2025-10-08
Purpose: Load models_inventory_v1.yaml and provide lookup APIs
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ModelInfo:
    """Model metadata from inventory"""
    name: str
    file: str
    layer: str
    domain: Optional[str] = None
    operation: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[str]] = None
    type: Optional[str] = None
    api: Optional[str] = None


class ModelRegistry:
    """Registry for discovering and validating Pydantic models"""
    
    def __init__(self, inventory_path: Optional[Path] = None):
        """
        Initialize registry from YAML inventory
        
        Args:
            inventory_path: Path to models_inventory_v1.yaml
        """
        if inventory_path is None:
            # Default path relative to project root
            inventory_path = Path(__file__).parent.parent.parent / "config" / "models_inventory_v1.yaml"
        
        self.inventory_path = inventory_path
        self._models: Dict[str, ModelInfo] = {}
        self._by_layer: Dict[str, List[ModelInfo]] = {}
        self._by_domain: Dict[str, List[ModelInfo]] = {}
        self._by_operation: Dict[str, List[ModelInfo]] = {}
        
        self._load_inventory()
    
    def _load_inventory(self) -> None:
        """Load and index models from YAML inventory"""
        if not self.inventory_path.exists():
            raise FileNotFoundError(f"Model inventory not found: {self.inventory_path}")
        
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        layers = data.get('layers', {})
        
        # Parse Layer 0: Base
        layer_0 = layers.get('layer_0_base', {})
        for model_data in layer_0.get('models', []):
            self._add_model('layer_0_base', None, model_data)
        
        # Parse Layer 1: Payloads
        layer_1 = layers.get('layer_1_payloads', {})
        for domain_key in ['casefile_domain', 'tool_session_domain', 'chat_session_domain']:
            domain_data = layer_1.get(domain_key, {})
            for model_data in domain_data.get('models', []):
                self._add_model('layer_1_payloads', domain_key, model_data)
        
        # Parse Layer 2: DTOs (list format)
        layer_2 = layers.get('layer_2_dtos', {})
        for operation_group, model_names in layer_2.items():
            if operation_group == 'description':
                continue
            for model_name in model_names:
                model_data = {'name': model_name}
                self._add_model('layer_2_dtos', operation_group, model_data)
        
        # Parse Layer 3: Canonical
        layer_3 = layers.get('layer_3_canonical', {})
        for model_data in layer_3.get('models', []):
            self._add_model('layer_3_canonical', 'canonical', model_data)
        
        # Parse Layer 4: External
        layer_4 = layers.get('layer_4_external', {})
        for model_data in layer_4.get('models', []):
            self._add_model('layer_4_external', 'workspace', model_data)
        
        # Parse Layer 5: Views
        layer_5 = layers.get('layer_5_views', {})
        for model_data in layer_5.get('models', []):
            self._add_model('layer_5_views', 'views', model_data)
    
    def _add_model(self, layer: str, domain: Optional[str], model_data: Dict[str, Any]) -> None:
        """Add model to registry and indices"""
        model_info = ModelInfo(
            name=model_data['name'],
            file=model_data.get('file', ''),
            layer=layer,
            domain=domain,
            operation=model_data.get('operation'),
            description=model_data.get('description'),
            fields=model_data.get('fields'),
            type=model_data.get('type'),
            api=model_data.get('api')
        )
        
        # Primary index
        self._models[model_info.name] = model_info
        
        # Layer index
        if layer not in self._by_layer:
            self._by_layer[layer] = []
        self._by_layer[layer].append(model_info)
        
        # Domain index
        if domain:
            if domain not in self._by_domain:
                self._by_domain[domain] = []
            self._by_domain[domain].append(model_info)
        
        # Operation index
        if model_info.operation:
            if model_info.operation not in self._by_operation:
                self._by_operation[model_info.operation] = []
            self._by_operation[model_info.operation].append(model_info)
    
    def get_model(self, name: str) -> Optional[ModelInfo]:
        """Get model by name"""
        return self._models.get(name)
    
    def list_by_layer(self, layer: str) -> List[ModelInfo]:
        """Get all models in a layer"""
        return self._by_layer.get(layer, [])
    
    def list_by_domain(self, domain: str) -> List[ModelInfo]:
        """Get all models in a domain"""
        return self._by_domain.get(domain, [])
    
    def list_by_operation(self, operation: str) -> List[ModelInfo]:
        """Get all models for an operation"""
        return self._by_operation.get(operation, [])
    
    def get_payload_models(self, operation: str) -> tuple[Optional[ModelInfo], Optional[ModelInfo]]:
        """
        Get request and response payload models for an operation
        
        Returns:
            (request_payload, response_payload) tuple
        """
        models = self.list_by_operation(operation)
        request_payload = None
        response_payload = None
        
        for model in models:
            if model.name.endswith('Payload') and not any(
                suffix in model.name for suffix in ['Result', 'Created', 'Response']
            ):
                request_payload = model
            elif any(suffix in model.name for suffix in ['Result', 'Created', 'Response']):
                response_payload = model
        
        return request_payload, response_payload
    
    def validate_model_exists(self, name: str) -> bool:
        """Check if model exists in registry"""
        return name in self._models
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'total_models': len(self._models),
            'by_layer': {layer: len(models) for layer, models in self._by_layer.items()},
            'by_domain': {domain: len(models) for domain, models in self._by_domain.items()},
            'layers': list(self._by_layer.keys()),
            'domains': list(self._by_domain.keys()),
            'operations': list(self._by_operation.keys())
        }


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    """Get or create global model registry instance"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


def get_model(name: str) -> Optional[ModelInfo]:
    """Get model by name from global registry"""
    return get_model_registry().get_model(name)


def list_models_by_layer(layer: str) -> List[ModelInfo]:
    """Get all models in a layer from global registry"""
    return get_model_registry().list_by_layer(layer)


def list_models_by_domain(domain: str) -> List[ModelInfo]:
    """Get all models in a domain from global registry"""
    return get_model_registry().list_by_domain(domain)


def validate_model_exists(name: str) -> bool:
    """Check if model exists in global registry"""
    return get_model_registry().validate_model_exists(name)


if __name__ == "__main__":
    # Test registry
    registry = ModelRegistry()
    stats = registry.get_statistics()
    
    print("Model Registry Statistics:")
    print(f"Total models: {stats['total_models']}")
    print(f"\nBy layer:")
    for layer, count in stats['by_layer'].items():
        print(f"  {layer}: {count}")
    print(f"\nBy domain:")
    for domain, count in stats['by_domain'].items():
        print(f"  {domain}: {count}")
    print(f"\nOperations: {len(stats['operations'])}")
    
    # Test lookups
    print("\n--- Test Lookups ---")
    casefile_payload = registry.get_model("CreateCasefilePayload")
    if casefile_payload:
        print(f"\nCreateCasefilePayload:")
        print(f"  File: {casefile_payload.file}")
        print(f"  Layer: {casefile_payload.layer}")
        print(f"  Operation: {casefile_payload.operation}")
        print(f"  Fields: {casefile_payload.fields}")
    
    # Test operation lookup
    chat_models = registry.list_by_operation("chat")
    print(f"\nChat operation models: {[m.name for m in chat_models]}")
    
    # Test payload extraction
    req_payload, resp_payload = registry.get_payload_models("create_casefile")
    print(f"\ncreate_casefile payloads:")
    print(f"  Request: {req_payload.name if req_payload else None}")
    print(f"  Response: {resp_payload.name if resp_payload else None}")
