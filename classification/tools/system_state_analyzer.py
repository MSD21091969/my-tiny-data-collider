#!/usr/bin/env python3
"""
System State Analyzer Tool
Version: 1.0.0
Purpose: Analyze current system state for classification, versioning, and tool relationships
This serves as both a test tool and documentation of current practices.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))

from pydantic_ai_integration.tool_decorator import MANAGED_TOOLS
from pydantic_ai_integration.method_registry import MANAGED_METHODS


def analyze_tool_classifications() -> dict[str, Any]:
    """Analyze tool classifications and versioning patterns."""
    tools = list(MANAGED_TOOLS.values())

    analysis = {
        "total_tools": len(tools),
        "version_distribution": {},
        "category_distribution": {},
        "tag_patterns": {},
        "method_references": {},
        "classification_completeness": {
            "has_category": 0,
            "has_tags": 0,
            "has_method_reference": 0,
            "has_version": 0,
        },
    }

    for tool in tools:
        # Version analysis
        version = getattr(tool, "version", "unknown")
        analysis["version_distribution"][version] = (
            analysis["version_distribution"].get(version, 0) + 1
        )

        # Category analysis
        category = getattr(tool, "category", "unknown")
        analysis["category_distribution"][category] = (
            analysis["category_distribution"].get(category, 0) + 1
        )

        # Tag patterns
        tags = getattr(tool, "tags", [])
        for tag in tags:
            analysis["tag_patterns"][tag] = analysis["tag_patterns"].get(tag, 0) + 1

        # Method references
        method_name = getattr(tool, "method_name", None)
        if method_name:
            analysis["method_references"][method_name] = (
                analysis["method_references"].get(method_name, 0) + 1
            )

        # Completeness checks
        if category and category != "general":
            analysis["classification_completeness"]["has_category"] += 1
        if tags:
            analysis["classification_completeness"]["has_tags"] += 1
        if method_name:
            analysis["classification_completeness"]["has_method_reference"] += 1
        if version and version != "1.0.0":
            analysis["classification_completeness"]["has_version"] += 1

    return analysis


def analyze_method_classifications() -> dict[str, Any]:
    """Analyze method classifications and relationships."""
    methods = list(MANAGED_METHODS.values())

    analysis = {
        "total_methods": len(methods),
        "domain_distribution": {},
        "capability_distribution": {},
        "complexity_distribution": {},
        "maturity_distribution": {},
        "integration_distribution": {},
        "tool_coverage": {},
    }

    for method in methods:
        # Classification distributions
        domain = getattr(method, "domain", "unknown")
        capability = getattr(method, "capability", "unknown")
        complexity = getattr(method, "complexity", "unknown")
        maturity = getattr(method, "maturity", "unknown")
        integration = getattr(method, "integration_tier", "unknown")

        analysis["domain_distribution"][domain] = analysis["domain_distribution"].get(domain, 0) + 1
        analysis["capability_distribution"][capability] = (
            analysis["capability_distribution"].get(capability, 0) + 1
        )
        analysis["complexity_distribution"][complexity] = (
            analysis["complexity_distribution"].get(complexity, 0) + 1
        )
        analysis["maturity_distribution"][maturity] = (
            analysis["maturity_distribution"].get(maturity, 0) + 1
        )
        analysis["integration_distribution"][integration] = (
            analysis["integration_distribution"].get(integration, 0) + 1
        )

        # Tool coverage
        method_name = getattr(method, "name", "unknown")
        tool_count = sum(
            1
            for tool in MANAGED_TOOLS.values()
            if getattr(tool, "method_name", None) == method_name
        )
        analysis["tool_coverage"][method_name] = tool_count

    return analysis


def analyze_tool_method_relationships() -> dict[str, Any]:
    """Analyze relationships between tools and methods."""
    relationships = {
        "tools_with_methods": 0,
        "tools_without_methods": 0,
        "methods_with_tools": 0,
        "methods_without_tools": 0,
        "orphaned_tools": [],
        "orphaned_methods": [],
    }

    # Check tools
    for tool_name, tool in MANAGED_TOOLS.items():
        method_name = getattr(tool, "method_name", None)
        if method_name and method_name in MANAGED_METHODS:
            relationships["tools_with_methods"] += 1
        else:
            relationships["tools_without_methods"] += 1
            relationships["orphaned_tools"].append(tool_name)

    # Check methods
    for method_name, _method in MANAGED_METHODS.items():
        has_tools = any(
            getattr(tool, "method_name", None) == method_name for tool in MANAGED_TOOLS.values()
        )
        if has_tools:
            relationships["methods_with_tools"] += 1
        else:
            relationships["methods_without_tools"] += 1
            relationships["orphaned_methods"].append(method_name)

    return relationships


def generate_system_report() -> str:
    """Generate comprehensive system state report."""
    tool_analysis = analyze_tool_classifications()
    method_analysis = analyze_method_classifications()
    relationship_analysis = analyze_tool_method_relationships()

    report = f"""
# System State Analysis Report
Generated: {__import__("datetime").datetime.now().isoformat()}

## Tool Analysis
- Total Tools: {tool_analysis["total_tools"]}
- Version Distribution: {json.dumps(tool_analysis["version_distribution"], indent=2)}
- Category Distribution: {json.dumps(tool_analysis["category_distribution"], indent=2)}
- Tag Patterns: {json.dumps(tool_analysis["tag_patterns"], indent=2)}
- Method References: {json.dumps(tool_analysis["method_references"], indent=2)}
- Classification Completeness: {json.dumps(tool_analysis["classification_completeness"], indent=2)}

## Method Analysis
- Total Methods: {method_analysis["total_methods"]}
- Domain Distribution: {json.dumps(method_analysis["domain_distribution"], indent=2)}
- Capability Distribution: {json.dumps(method_analysis["capability_distribution"], indent=2)}
- Complexity Distribution: {json.dumps(method_analysis["complexity_distribution"], indent=2)}
- Maturity Distribution: {json.dumps(method_analysis["maturity_distribution"], indent=2)}
- Integration Distribution: {json.dumps(method_analysis["integration_distribution"], indent=2)}
- Tool Coverage: {json.dumps(method_analysis["tool_coverage"], indent=2)}

## Relationships
- Tools with Methods: {relationship_analysis["tools_with_methods"]}
- Tools without Methods: {relationship_analysis["tools_without_methods"]}
- Methods with Tools: {relationship_analysis["methods_with_tools"]}
- Methods without Tools: {relationship_analysis["methods_without_tools"]}
- Orphaned Tools: {relationship_analysis["orphaned_tools"]}
- Orphaned Methods: {relationship_analysis["orphaned_methods"]}

## Key Insights
1. Classification Coverage: {tool_analysis["classification_completeness"]["has_category"] / tool_analysis["total_tools"] * 100:.1f}% tools have meaningful categories
2. Versioning Maturity: {tool_analysis["classification_completeness"]["has_version"] / tool_analysis["total_tools"] * 100:.1f}% tools have custom versions
3. Method Integration: {relationship_analysis["tools_with_methods"] / tool_analysis["total_tools"] * 100:.1f}% tools reference methods
4. Tool Coverage: {relationship_analysis["methods_with_tools"] / method_analysis["total_methods"] * 100:.1f}% methods have tool wrappers

## Recommendations
- Focus on standardizing tool classifications (categories, tags)
- Implement systematic versioning practices
- Ensure all tools reference methods for parameter inheritance
- Document orphaned tools/methods and decide on retention
"""

    return report


if __name__ == "__main__":
    print("Analyzing system state...")
    report = generate_system_report()
    print(report)

    # Save to file
    output_path = repo_root / "classification" / "docs" / "SYSTEM_STATE_ANALYSIS.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {output_path}")
