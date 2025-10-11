"""Generate mapper boilerplate from YAML model inventory.

This script generates mapper class boilerplate for operations that need
explicit transformations between DTOs and domain models.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic_ai_integration.model_registry import ModelRegistry


def generate_mapper_code(operation: str, registry: ModelRegistry) -> str:
    """Generate mapper class code for an operation.

    Args:
        operation: Operation name (e.g., 'create_casefile')
        registry: ModelRegistry instance

    Returns:
        Generated mapper class code as string
    """

    # For now, use naming patterns since operations aren't tagged
    req_payload_name = None
    resp_payload_name = None

    # Find payloads by naming pattern
    for model_name, _model_info in registry._models.items():
        if operation.replace('create_', '').replace('get_', '').replace('update_', '').replace('delete_', '') in model_name.lower():
            if model_name.endswith('Payload') and not any(suffix in model_name for suffix in ['Result', 'Created', 'Response']):
                req_payload_name = model_name
            elif any(suffix in model_name for suffix in ['Result', 'Created', 'Response']):
                resp_payload_name = model_name

    if not req_payload_name and not resp_payload_name:
        return f"# No payloads found for operation '{operation}'"

    class_name = f"{operation.title().replace('_', '')}Mapper"

    # Infer domain model name
    domain_model_name = _infer_domain_model_name(operation)

    code = f'''"""Auto-generated mapper for {operation} operation."""

from pydantic_models.base.transformations import BaseMapper
from pydantic_models.operations.{operation.split('_')[1] if len(operation.split('_')) > 1 else operation}_ops import (
    {req_payload_name or "BaseRequest"},
    {resp_payload_name or "BaseResponse"}
)
from pydantic_models.canonical.{operation.split('_')[1] if len(operation.split('_')) > 1 else operation} import {domain_model_name}


class {class_name}(BaseMapper[{req_payload_name or "BaseRequest"}, {domain_model_name}]):
    """Transforms {operation} payloads to/from domain models."""

    @classmethod
    def to_domain(cls, payload: {req_payload_name or "BaseRequest"}) -> {domain_model_name}:
        """Transform request payload to domain model."""
        # TODO: Implement transformation logic
        return {domain_model_name}(
            # Map fields here - customize based on your domain model
            id=cls._generate_id(),
            # Add field mappings...
        )

    @classmethod
    def to_dto(cls, domain: {domain_model_name}) -> {resp_payload_name or "BaseResponse"}:
        """Transform domain model to response payload."""
        # TODO: Implement transformation logic
        return {resp_payload_name or "BaseResponse"}(
            # Map fields here - customize based on your response model
            # Add field mappings...
        )

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique identifier."""
        import uuid
        return str(uuid.uuid4())
'''
    return code


def _infer_domain_model_name(operation: str) -> str:
    """Infer the domain model name from operation."""
    parts = operation.split('_')
    if len(parts) > 1:
        domain = parts[1]
        if domain == 'casefile':
            return 'CasefileModel'
        elif domain in ['tool', 'session']:
            return 'ToolSessionModel'
        elif domain in ['chat', 'chatsession']:
            return 'ChatSessionModel'
    return 'DomainModel'


def generate_all_mappers(registry: ModelRegistry, output_dir: str = "src/pydantic_models/mappers") -> list[str]:
    """Generate mapper classes for all operations that need them.

    Args:
        registry: ModelRegistry instance
        output_dir: Directory to output mapper files

    Returns:
        List of generated file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Generate for core operations
    core_operations = [
        'create_casefile', 'get_casefile', 'update_casefile', 'delete_casefile',
        'create_session', 'get_session',
        'create_chatsession', 'get_chatsession'
    ]

    for operation in core_operations:
        code = generate_mapper_code(operation, registry)

        if not code.startswith("#"):
            file_path = output_path / f"{operation}_mapper.py"
            file_path.write_text(code)
            generated_files.append(str(file_path))
            print(f"✅ Generated mapper: {file_path}")

    return generated_files


def list_operations_needing_mappers(registry: ModelRegistry) -> list[tuple[str, str, str]]:
    """List all operations that need mapper implementations.

    Args:
        registry: ModelRegistry instance

    Returns:
        List of (operation, request_payload, response_payload) tuples
    """
    operations = []

    # Check core operations
    core_operations = [
        'create_casefile', 'get_casefile', 'update_casefile', 'delete_casefile',
        'create_session', 'get_session',
        'create_chatsession', 'get_chatsession'
    ]

    for operation in core_operations:
        req_payload = None
        resp_payload = None

        # Find payloads by naming pattern
        for model_name, _model_info in registry._models.items():
            if operation.split('_')[-1] in model_name.lower():
                if model_name.endswith('Payload') and not any(suffix in model_name for suffix in ['Result', 'Created', 'Response']):
                    req_payload = model_name
                elif any(suffix in model_name for suffix in ['Result', 'Created', 'Response']):
                    resp_payload = model_name

        operations.append((operation, req_payload or 'N/A', resp_payload or 'N/A'))

    return operations


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate mapper boilerplate from model inventory")
    parser.add_argument("operation", nargs='?', help="Specific operation to generate mapper for")
    parser.add_argument("--all", action="store_true", help="Generate mappers for all operations")
    parser.add_argument("--list", action="store_true", help="List operations that need mappers")
    parser.add_argument("--output-dir", default="src/pydantic_models/mappers",
                       help="Output directory for generated mappers")

    args = parser.parse_args()

    try:
        registry = ModelRegistry()

        if args.list:
            # List operations needing mappers
            operations = list_operations_needing_mappers(registry)
            print(f"Operations needing mappers ({len(operations)}):")
            for op, req, resp in operations:
                print(f"  {op}: {req} → {resp}")

        elif args.all:
            # Generate all mappers
            generated = generate_all_mappers(registry, args.output_dir)
            print(f"\nGenerated {len(generated)} mapper files in {args.output_dir}")

        elif args.operation:
            # Generate specific mapper
            operations = [op for op, _, _ in list_operations_needing_mappers(registry)]
            if args.operation not in operations:
                print(f"❌ Operation '{args.operation}' not found or doesn't need a mapper")
                print(f"Available operations: {', '.join(operations)}")
                sys.exit(1)

            code = generate_mapper_code(args.operation, registry)
            print(code)

        else:
            # Show usage
            parser.print_help()

    except Exception as e:
        print(f"❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
