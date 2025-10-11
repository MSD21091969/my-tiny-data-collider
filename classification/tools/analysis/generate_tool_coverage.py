#!/usr/bin/env python3
"""
Generate tool coverage report.
Compares registered tools against available service methods.
"""

import yaml
from pathlib import Path


def generate_tool_coverage_report():
    """Analyze tool coverage across services."""

    print("# Tool Coverage Report\n")

    # Read methods inventory
    methods_path = Path("config/methods_inventory_v1.yaml")
    with open(methods_path) as f:
        methods_inv = yaml.safe_load(f)

    # Count tool definitions
    tool_dir = Path("config/methodtools_v1")
    tool_files = list(tool_dir.glob("*.yaml"))

    print(f"## Summary")
    print(f"- **Total Tool Files:** {len(tool_files)}")
    print(f"- **Methods Inventory Version:** {methods_inv.get('version', 'N/A')}")
    print(f"- **Last Updated:** {methods_inv.get('generated_at', 'N/A')}\n")

    # Group by service
    services = {}
    for tool_file in tool_files:
        service_name = tool_file.stem.split("_")[0]
        if service_name not in services:
            services[service_name] = []
        services[service_name].append(tool_file.stem)

    print("## Tools by Service\n")
    for service, tools in sorted(services.items()):
        print(f"### {service}")
        print(f"- **Tool Count:** {len(tools)}")
        for tool in sorted(tools):
            print(f"  - `{tool}`")
        print()


if __name__ == "__main__":
    generate_tool_coverage_report()
