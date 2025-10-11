"""Analyze model transformation paths and identify mapping opportunities.

This script analyzes the current model landscape using the ModelRegistry
to identify transformation paths between Request/Response payloads and
domain models, helping identify where explicit mappers are needed.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic_ai_integration.model_registry import ModelRegistry


def analyze_transformation_paths(registry: ModelRegistry) -> dict[str, list[tuple[str, str]]]:
    """Map out potential Request → Payload → Domain → Response transformation chains.

    Since operations aren't tagged in the inventory, we'll analyze based on naming patterns.
    """
    paths = {}

    # Get all models
    all_models = list(registry._models.values())

    # Group by potential operations based on naming patterns
    operation_patterns = {}

    for model in all_models:
        name = model.name

        # Extract operation from name patterns
        operation = None
        if name.startswith('Create') and name.endswith('Payload'):
            operation = f"create_{name.replace('Create', '').replace('Payload', '').lower()}"
        elif name.startswith('Get') and name.endswith('Payload'):
            operation = f"get_{name.replace('Get', '').replace('Payload', '').lower()}"
        elif name.startswith('Update') and name.endswith('Payload'):
            operation = f"update_{name.replace('Update', '').replace('Payload', '').lower()}"
        elif name.startswith('Delete') and name.endswith('Payload'):
            operation = f"delete_{name.replace('Delete', '').replace('Payload', '').lower()}"
        elif name.endswith('Result') or name.endswith('Created') or name.endswith('Response'):
            # Response payloads
            base_name = name.replace('Result', '').replace('Created', '').replace('Response', '')
            operation = f"create_{base_name.lower()}"  # Assume create operation

        if operation:
            if operation not in operation_patterns:
                operation_patterns[operation] = []
            operation_patterns[operation].append(model)

    # Build transformation paths
    for operation, models in operation_patterns.items():
        req_payloads = [m for m in models if not any(suffix in m.name for suffix in ['Result', 'Created', 'Response'])]
        resp_payloads = [m for m in models if any(suffix in m.name for suffix in ['Result', 'Created', 'Response'])]

        if req_payloads or resp_payloads:
            paths[operation] = [
                ("Request", f"{operation}_request"),
                ("RequestPayload", req_payloads[0].name if req_payloads else "N/A"),
                ("ResponsePayload", resp_payloads[0].name if resp_payloads else "N/A"),
                ("Response", f"{operation}_response")
            ]

    return paths


def find_missing_mappers(registry: ModelRegistry) -> list[str]:
    """Identify operations that need explicit mapper implementations.

    Args:
        registry: The ModelRegistry instance to analyze

    Returns:
        List of operations that need mapper implementations
    """
    missing = []
    paths = analyze_transformation_paths(registry)

    for operation in paths.keys():
        # For now, assume all operations need mappers
        mapper_name = f"{operation.title().replace('_', '')}Mapper"
        missing.append(f"{operation} → {mapper_name}")

    return missing


def analyze_model_coverage(registry: ModelRegistry) -> dict[str, int]:
    """Analyze how well operations are covered by models.

    Args:
        registry: The ModelRegistry instance to analyze

    Returns:
        Statistics about model coverage
    """
    paths = analyze_transformation_paths(registry)
    total_operations = len(paths)

    operations_with_payloads = 0
    operations_with_both_payloads = 0

    for _operation, path in paths.items():
        req_payload = path[1][1] if path[1][1] != "N/A" else None
        resp_payload = path[2][1] if path[2][1] != "N/A" else None

        if req_payload or resp_payload:
            operations_with_payloads += 1
        if req_payload and resp_payload:
            operations_with_both_payloads += 1

    return {
        "total_operations": total_operations,
        "operations_with_payloads": operations_with_payloads,
        "operations_with_both_payloads": operations_with_both_payloads,
        "coverage_percentage": (operations_with_both_payloads / total_operations * 100) if total_operations > 0 else 0
    }


def print_transformation_report(registry: ModelRegistry) -> None:
    """Print a comprehensive transformation analysis report.

    Args:
        registry: The ModelRegistry instance to analyze
    """
    print("=" * 80)
    print("MODEL TRANSFORMATION ANALYSIS REPORT")
    print("=" * 80)

    # Coverage statistics
    coverage = analyze_model_coverage(registry)
    print("\nCOVERAGE STATISTICS:")
    print(f"  Total Operations: {coverage['total_operations']}")
    print(f"  With Payloads: {coverage['operations_with_payloads']}")
    print(f"  With Both Payloads: {coverage['operations_with_both_payloads']}")
    print(f"  Coverage: {coverage['coverage_percentage']:.1f}%")

    # Transformation paths
    print("\nTRANSFORMATION PATHS:")
    paths = analyze_transformation_paths(registry)

    for operation, path in list(paths.items())[:10]:  # Show first 10
        print(f"\n  {operation.upper()}:")
        for step, model in path:
            print(f"    {step:20} -> {model}")

    if len(paths) > 10:
        print(f"\n  ... and {len(paths) - 10} more operations")

    # Missing mappers
    print("\nMISSING MAPPERS:")
    missing = find_missing_mappers(registry)

    for mapper in missing[:10]:  # Show first 10
        print(f"  • {mapper}")

    if len(missing) > 10:
        print(f"\n  ... and {len(missing) - 10} more missing mappers")

    print("\nRECOMMENDATIONS:")
    print("  1. Implement mappers for operations with both request and response payloads")
    print("  2. Focus on core business operations first (create, update, get)")
    print("  3. Use the generate_mapper.py script to create boilerplate")
    print("  4. Add transformation tests to validate mappings")

    print("=" * 80)


def export_transformation_matrix(registry: ModelRegistry, output_file: str) -> None:
    """Export transformation matrix to a file for further analysis.

    Args:
        registry: ModelRegistry instance
        output_file: Path to output file
    """
    paths = analyze_transformation_paths(registry)

    with open(output_file, 'w') as f:
        f.write("Operation,Request,RequestPayload,ResponsePayload,Response\n")

        for operation, path in paths.items():
            row = [operation]
            for _, model in path:
                row.append(model)
            f.write(",".join(row) + "\n")

    print(f"✅ Transformation matrix exported to: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze model transformation paths")
    parser.add_argument("--export", help="Export transformation matrix to CSV file")
    parser.add_argument("--operation", help="Analyze specific operation")

    args = parser.parse_args()

    try:
        registry = ModelRegistry()

        if args.operation:
            # Analyze specific operation
            req_payload, resp_payload = registry.get_payload_models(args.operation)
            if req_payload and resp_payload:
                print(f"\n🔍 Analyzing operation: {args.operation}")
                print(f"  Request Payload: {req_payload.name}")
                print(f"  Response Payload: {resp_payload.name}")
                print(f"  Suggested Mapper: {args.operation.title().replace('_', '')}Mapper")
            else:
                print(f"❌ Operation '{args.operation}' not found or missing payloads")
        else:
            # Full analysis
            print_transformation_report(registry)

            if args.export:
                export_transformation_matrix(registry, args.export)

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)
