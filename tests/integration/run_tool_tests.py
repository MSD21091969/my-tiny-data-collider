"""
Test runner for comprehensive tool execution tests.

Usage:
    python run_tool_tests.py                    # Run all tests
    python run_tool_tests.py --mode direct      # Run direct execution tests only
    python run_tool_tests.py --mode mock        # Run mock tests only
    python run_tool_tests.py --tool create_casefile_tool  # Test specific tool
"""

import sys
import subprocess
from pathlib import Path


def run_tests(mode=None, tool=None, verbose=True):
    """Run test suite with specified filters."""
    
    cmd = ["pytest", "tests/integration/test_tool_execution_modes.py"]
    
    if verbose:
        cmd.extend(["-v", "-s"])
    
    # Filter by mode
    if mode == "direct":
        cmd.extend(["-k", "TestDirectToolExecution"])
    elif mode == "dto":
        cmd.extend(["-k", "TestToolExecutionViaRequestDTO"])
    elif mode == "mock":
        cmd.extend(["-k", "TestToolExecutionMockMode"])
    elif mode == "dryrun":
        cmd.extend(["-k", "TestDryRunMode"])
    elif mode == "verify":
        cmd.extend(["-k", "TestToolResultVerification"])
    elif mode == "error":
        cmd.extend(["-k", "TestToolErrorHandling"])
    elif mode == "performance":
        cmd.extend(["-k", "TestToolPerformance"])
    
    # Filter by tool
    if tool:
        cmd.extend(["-k", tool])
    
    # Add markers
    cmd.extend(["-m", "integration or mock"])
    
    print(f"Running: {' '.join(cmd)}\n")
    return subprocess.run(cmd)


def show_help():
    """Show usage information."""
    print("""
Test Suite for Tool Execution
==============================

Modes:
  direct       - Test direct tool.implementation() calls
  dto          - Test via Request DTO pattern
  mock         - Test with mocked services (no real calls)
  dryrun       - Test dry run mode
  verify       - Test result structure verification
  error        - Test error handling
  performance  - Test execution performance

Examples:
  python run_tool_tests.py
  python run_tool_tests.py --mode direct
  python run_tool_tests.py --mode mock
  python run_tool_tests.py --tool create_casefile_tool
  python run_tool_tests.py --mode verify --tool create_casefile

Quick Test Scenarios:
  
  1. Basic Functionality:
     python run_tool_tests.py --mode direct
  
  2. Mock Mode (No Firestore needed):
     python run_tool_tests.py --mode mock
  
  3. Dry Run (Preview only):
     python run_tool_tests.py --mode dryrun
  
  4. Result Verification:
     python run_tool_tests.py --mode verify
  
  5. Test Specific Tool:
     python run_tool_tests.py --tool create_casefile_tool

Available Tools:
  - create_casefile_tool
  - get_casefile_tool
  - list_casefiles_tool
  - update_casefile_tool
  - delete_casefile_tool
  ... and 29 more
""")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tool execution tests")
    parser.add_argument("--mode", choices=["direct", "dto", "mock", "dryrun", "verify", "error", "performance"],
                       help="Test mode to run")
    parser.add_argument("--tool", help="Specific tool to test")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    parser.add_argument("--help-extended", action="store_true", help="Show extended help")
    
    args = parser.parse_args()
    
    if args.help_extended:
        show_help()
        sys.exit(0)
    
    result = run_tests(mode=args.mode, tool=args.tool, verbose=not args.quiet)
    sys.exit(result.returncode)
