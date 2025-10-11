"""Visualize RAR transformation flow for debugging.

This script generates ASCII visualizations of Request-Action-Response
transformation flows to help understand and debug the orchestration pipeline.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic_ai_integration.model_registry import ModelRegistry


def visualize_operation_flow(operation: str, registry: ModelRegistry) -> str:
    """Generate ASCII visualization of RAR flow for an operation.

    Args:
        operation: Operation name to visualize
        registry: ModelRegistry instance

    Returns:
        ASCII art visualization of the flow
    """

    req_payload, resp_payload = registry.get_payload_models(operation)

    # Determine domain model (heuristic)
    domain_model = _infer_domain_model(operation)

    flow = f"""
╔══════════════════════════════════════════════════════════════╗
║  Operation: {operation.upper()}
╠══════════════════════════════════════════════════════════════╣
║
║  1. CLIENT REQUEST
║     └─→ {operation.title().replace('_', '')}Request
║         └─→ Payload: {req_payload.name if req_payload else 'N/A'}
║             • Fields: {_get_payload_fields(req_payload) if req_payload else 'N/A'}
║
║  2. ORCHESTRATION (RequestHub)
║     • Context Injection: session, casefile, user
║     • Hook Execution: metrics, audit
║     • Service Routing: → {_infer_service_name(operation)}.{operation}()
║
║  3. DOMAIN TRANSFORMATION
║     • Mapper: {req_payload.name if req_payload else 'N/A'} → {domain_model}
║     • Business Logic Processing
║     • Persistence Layer
║
║  4. RESPONSE TRANSFORMATION
║     • Mapper: {domain_model} → {resp_payload.name if resp_payload else 'N/A'}
║     • Envelope: {operation.title().replace('_', '')}Response
║
║  5. CLIENT RESPONSE
║     └─→ Status: COMPLETED / FAILED
║     └─→ Payload: {resp_payload.name if resp_payload else 'N/A'}
║
╚══════════════════════════════════════════════════════════════╝
"""
    return flow


def _infer_domain_model(operation: str) -> str:
    """Infer domain model name from operation."""
    if 'casefile' in operation:
        return 'CasefileModel'
    elif 'tool' in operation or 'session' in operation:
        return 'ToolSessionModel'
    elif 'chat' in operation or 'message' in operation:
        return 'ChatSessionModel'
    else:
        return 'DomainModel'


def _infer_service_name(operation: str) -> str:
    """Infer service class name from operation."""
    if 'casefile' in operation:
        return 'CasefileService'
    elif 'tool' in operation or 'session' in operation:
        return 'ToolSessionService'
    elif 'chat' in operation or 'message' in operation:
        return 'CommunicationService'
    else:
        return 'Service'


def _get_payload_fields(payload_model) -> str:
    """Extract field names from payload model."""
    if not payload_model or not hasattr(payload_model, 'model_fields'):
        return 'N/A'

    fields = list(payload_model.model_fields.keys())[:5]  # Show first 5 fields
    if len(payload_model.model_fields) > 5:
        fields.append('...')
    return ', '.join(fields)


def visualize_all_operations(registry: ModelRegistry, max_operations: int = 5) -> str:
    """Generate visualizations for multiple operations.

    Args:
        registry: ModelRegistry instance
        max_operations: Maximum number of operations to visualize

    Returns:
        Combined visualization string
    """
    operations = list(registry._by_operation.keys())[:max_operations]
    visualizations = []

    for operation in operations:
        req_payload, resp_payload = registry.get_payload_models(operation)
        if req_payload and resp_payload:  # Only show operations with both payloads
            visualizations.append(visualize_operation_flow(operation, registry))

    return '\n'.join(visualizations)


def generate_flow_diagram(operation: str, registry: ModelRegistry, format: str = 'ascii') -> str:
    """Generate flow diagram in different formats.

    Args:
        operation: Operation name
        registry: ModelRegistry instance
        format: Output format ('ascii', 'mermaid', 'plantuml')

    Returns:
        Formatted diagram string
    """
    if format == 'mermaid':
        return _generate_mermaid_flow(operation, registry)
    elif format == 'plantuml':
        return _generate_plantuml_flow(operation, registry)
    else:
        return visualize_operation_flow(operation, registry)


def _generate_mermaid_flow(operation: str, registry: ModelRegistry) -> str:
    """Generate Mermaid flowchart for operation flow."""
    req_payload, resp_payload = registry.get_payload_models(operation)
    domain_model = _infer_domain_model(operation)
    service_name = _infer_service_name(operation)

    mermaid = f"""```mermaid
flowchart TD
    A[Client Request<br/>{operation.title().replace('_', '')}Request] --> B[RequestHub]
    B --> C[Context Injection<br/>session, casefile, user]
    C --> D[Hook Execution<br/>metrics, audit]
    D --> E[Service Routing<br/>{service_name}.{operation}()]
    E --> F[Domain Transform<br/>{req_payload.name if req_payload else 'N/A'} → {domain_model}]
    F --> G[Business Logic]
    G --> H[Persistence]
    H --> I[Response Transform<br/>{domain_model} → {resp_payload.name if resp_payload else 'N/A'}]
    I --> J[Response Envelope<br/>{operation.title().replace('_', '')}Response]
    J --> K[Client Response]
```"""
    return mermaid


def _generate_plantuml_flow(operation: str, registry: ModelRegistry) -> str:
    """Generate PlantUML activity diagram for operation flow."""
    req_payload, resp_payload = registry.get_payload_models(operation)
    domain_model = _infer_domain_model(operation)
    service_name = _infer_service_name(operation)

    plantuml = f"""@startuml
title {operation.upper()} Flow

start
:Client Request\\n{operation.title().replace('_', '')}Request;

:RequestHub Orchestration;
:Context Injection\\n(session, casefile, user);
:Hook Execution\\n(metrics, audit);
:Service Routing\\n{service_name}.{operation}();

:Domain Transform\\n{req_payload.name if req_payload else 'N/A'} → {domain_model};
:Business Logic Processing;
:Persistence Layer;

:Response Transform\\n{domain_model} → {resp_payload.name if resp_payload else 'N/A'};
:Response Envelope\\n{operation.title().replace('_', '')}Response;

:Client Response;
stop
@enduml"""
    return plantuml


def export_flows_to_file(registry: ModelRegistry, output_file: str, format: str = 'ascii') -> None:
    """Export operation flows to a file.

    Args:
        registry: ModelRegistry instance
        output_file: Output file path
        format: Diagram format ('ascii', 'mermaid', 'plantuml')
    """
    operations = list(registry._by_operation.keys())

    with open(output_file, 'w') as f:
        f.write(f"# RAR Flow Visualizations ({format.upper()})\n\n")

        for operation in operations:
            req_payload, resp_payload = registry.get_payload_models(operation)
            if req_payload and resp_payload:
                flow = generate_flow_diagram(operation, registry, format)
                f.write(f"## {operation.upper()}\n\n{flow}\n\n---\n\n")

    print(f"✅ Exported flows to: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualize RAR transformation flows")
    parser.add_argument("operation", nargs='?', help="Specific operation to visualize")
    parser.add_argument("--all", action="store_true", help="Visualize all operations")
    parser.add_argument("--format", choices=['ascii', 'mermaid', 'plantuml'],
                       default='ascii', help="Output format")
    parser.add_argument("--export", help="Export to file")
    parser.add_argument("--max-ops", type=int, default=5,
                       help="Maximum operations to show when using --all")

    args = parser.parse_args()

    try:
        registry = ModelRegistry()

        if args.operation:
            # Visualize specific operation
            req_payload, resp_payload = registry.get_payload_models(args.operation)
            if not req_payload or not resp_payload:
                print(f"❌ Operation '{args.operation}' not found or missing payloads")
                sys.exit(1)

            flow = generate_flow_diagram(args.operation, registry, args.format)
            print(flow)

        elif args.all:
            # Visualize all operations
            if args.format == 'ascii':
                flows = visualize_all_operations(registry, args.max_ops)
                print(flows)
            else:
                # For diagram formats, export to file
                if not args.export:
                    print("❌ --export required for diagram formats with --all")
                    sys.exit(1)
                export_flows_to_file(registry, args.export, args.format)

        else:
            # Show usage
            parser.print_help()

        # Export if requested
        if args.export and args.operation:
            with open(args.export, 'w') as f:
                flow = generate_flow_diagram(args.operation, registry, args.format)
                f.write(flow)
            print(f"✅ Exported to: {args.export}")

    except Exception as e:
        print(f"❌ Error during visualization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
 
 