"""
Automated version release script for methods registry.

This script helps create new releases by:
1. Validating current state (no uncommitted changes)
2. Updating version in YAML
3. Updating CHANGELOG template
4. Regenerating documentation
5. Committing changes
6. Creating git tag
7. Printing next steps

Usage:
    python scripts/release_version.py --type patch
    python scripts/release_version.py --type minor --changelog "Add archive functionality"
    python scripts/release_version.py --type major --changelog "Unified parameter naming"
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import yaml
import re


def run_command(cmd: str, check: bool = True) -> tuple[int, str, str]:
    """Run shell command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"   Error: {result.stderr}")
        sys.exit(1)
    
    return result.returncode, result.stdout, result.stderr


def check_git_status():
    """Ensure no uncommitted changes."""
    print("\n[1/8] Checking git status...")
    
    returncode, stdout, _ = run_command("git status --porcelain", check=False)
    
    if stdout.strip():
        print("❌ Uncommitted changes detected. Please commit or stash them first.")
        print("\nUncommitted files:")
        print(stdout)
        sys.exit(1)
    
    print("✅ Working directory clean")


def get_current_version() -> str:
    """Get current version from YAML."""
    yaml_path = Path("config/methods_inventory_v1.yaml")
    
    if not yaml_path.exists():
        print(f"❌ YAML not found: {yaml_path}")
        sys.exit(1)
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data.get('version', '1.0.0')


def bump_version(current: str, bump_type: str) -> str:
    """Calculate new version based on bump type."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', current)
    if not match:
        print(f"❌ Invalid version format: {current}")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups())
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        print(f"❌ Invalid bump type: {bump_type}")
        sys.exit(1)


def update_yaml_version(new_version: str, bump_type: str):
    """Update version in YAML file."""
    print(f"\n[2/8] Updating YAML version to {new_version}...")
    
    yaml_path = Path("config/methods_inventory_v1.yaml")
    
    # Read current content
    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update version line
    content = re.sub(
        r'version:\s*["\']?\d+\.\d+\.\d+["\']?',
        f'version: "{new_version}"',
        content
    )
    
    # Update updated_at
    today = datetime.now().strftime('%Y-%m-%d')
    content = re.sub(
        r'updated_at:\s*["\']?\d{4}-\d{2}-\d{2}["\']?',
        f'updated_at: "{today}"',
        content
    )
    
    # For MAJOR/MINOR, suggest creating new file
    if bump_type in ['major', 'minor']:
        new_yaml_path = yaml_path.parent / f"methods_inventory_v{new_version.split('.')[0]}.yaml"
        print(f"   💡 Consider copying to: {new_yaml_path}")
    
    # Write back
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {yaml_path}")


def update_changelog(new_version: str, bump_type: str, changelog_msg: str):
    """Add new version entry to CHANGELOG."""
    print(f"\n[3/8] Updating CHANGELOG...")
    
    changelog_path = Path("docs/METHODS_CHANGELOG.md")
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Create new version section
    if bump_type == 'patch':
        section = f"""
## [{new_version}] - {today}

### Fixed
- {changelog_msg or 'Bug fixes and improvements'}

---

"""
    elif bump_type == 'minor':
        section = f"""
## [{new_version}] - {today}

### Added
- {changelog_msg or 'New features and enhancements'}

---

"""
    elif bump_type == 'major':
        section = f"""
## [{new_version}] - {today}

### Changed
- **[BREAKING]** {changelog_msg or 'Breaking changes requiring migration'}

### Migration Guide
TODO: Add detailed migration instructions

---

"""
    
    # Insert after [Unreleased] section
    unreleased_pattern = r'(## \[Unreleased\].*?\n---\n)'
    if re.search(unreleased_pattern, content, re.DOTALL):
        content = re.sub(
            unreleased_pattern,
            r'\1' + section,
            content,
            flags=re.DOTALL
        )
    else:
        # Insert after header
        content = content.replace(
            '## [1.0.0]',
            section + '## [1.0.0]'
        )
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {changelog_path}")
    
    if bump_type == 'major':
        print("   ⚠️  Please add detailed migration guide to CHANGELOG")


def regenerate_docs():
    """Regenerate method documentation."""
    print(f"\n[4/8] Regenerating documentation...")
    
    returncode, stdout, stderr = run_command(
        "python scripts/generate_method_docs.py",
        check=False
    )
    
    if returncode != 0:
        print("❌ Documentation generation failed")
        print(stderr)
        sys.exit(1)
    
    print("✅ Documentation regenerated")


def run_tests():
    """Run test suite."""
    print(f"\n[5/8] Running tests...")
    
    # Check if pytest is available
    returncode, _, _ = run_command("python -m pytest --version", check=False)
    
    if returncode != 0:
        print("⚠️  pytest not available, skipping tests")
        return
    
    returncode, stdout, stderr = run_command(
        "python -m pytest tests/ -v",
        check=False
    )
    
    if returncode != 0:
        print("❌ Tests failed")
        print(stderr)
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✅ All tests passed")


def commit_changes(new_version: str, bump_type: str):
    """Commit version changes."""
    print(f"\n[6/8] Committing changes...")
    
    # Stage files
    files = [
        "config/methods_inventory_v1.yaml",
        "docs/METHODS_CHANGELOG.md",
        "docs/methods/"
    ]
    
    for file in files:
        run_command(f"git add {file}")
    
    # Commit
    commit_msg = f"chore: Release v{new_version}"
    if bump_type == 'major':
        commit_msg += " [BREAKING]"
    
    run_command(f'git commit -m "{commit_msg}"')
    
    print(f"✅ Committed changes")


def create_tag(new_version: str, changelog_msg: str):
    """Create git tag."""
    print(f"\n[7/8] Creating git tag...")
    
    tag_name = f"v{new_version}"
    tag_msg = changelog_msg or f"Release v{new_version}"
    
    run_command(f'git tag -a {tag_name} -m "{tag_msg}"')
    
    print(f"✅ Created tag: {tag_name}")


def print_next_steps(new_version: str, bump_type: str):
    """Print manual next steps."""
    print(f"\n[8/8] Next Steps:")
    print("=" * 60)
    print(f"✅ Version {new_version} prepared successfully!")
    print("\nManual steps required:\n")
    
    print("1. Review changes:")
    print(f"   git show v{new_version}")
    print(f"   git log -1 --stat")
    
    print("\n2. Push to remote:")
    print(f"   git push origin develop")
    print(f"   git push origin v{new_version}")
    
    if bump_type == 'major':
        print("\n3. Complete migration guide:")
        print("   - Edit docs/METHODS_CHANGELOG.md")
        print("   - Add detailed step-by-step migration instructions")
        print("   - Include code examples (before/after)")
    
    print("\n4. Create GitHub release:")
    print(f"   - Go to: https://github.com/MSD21091969/my-tiny-data-collider/releases/new")
    print(f"   - Select tag: v{new_version}")
    print(f"   - Copy content from CHANGELOG")
    print("   - Publish release")
    
    print("\n5. Communicate:")
    print("   - Post in team chat")
    print("   - Update documentation site")
    if bump_type == 'major':
        print("   - Email stakeholders about breaking changes")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Release new version of methods registry"
    )
    parser.add_argument(
        '--type',
        choices=['patch', 'minor', 'major'],
        required=True,
        help='Type of version bump'
    )
    parser.add_argument(
        '--changelog',
        default='',
        help='Changelog message for this release'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip test execution'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    print("=" * 60)
    print("METHODS REGISTRY VERSION RELEASE")
    print("=" * 60)
    
    # Get current version
    current_version = get_current_version()
    new_version = bump_version(current_version, args.type)
    
    print(f"\nCurrent version: {current_version}")
    print(f"New version:     {new_version}")
    print(f"Bump type:       {args.type.upper()}")
    
    if args.type == 'major':
        print("\n⚠️  WARNING: MAJOR release includes BREAKING CHANGES")
        print("   Users will need to update their code!")
    
    # Confirm
    if not args.dry_run:
        response = input(f"\nProceed with {args.type} release? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Execute release steps
    if not args.dry_run:
        check_git_status()
        update_yaml_version(new_version, args.type)
        update_changelog(new_version, args.type, args.changelog)
        regenerate_docs()
        
        if not args.skip_tests:
            run_tests()
        
        commit_changes(new_version, args.type)
        create_tag(new_version, args.changelog)
        print_next_steps(new_version, args.type)
    else:
        print("\n🔍 Dry run complete - no changes made")
        print(f"\nWould create version: {new_version}")


if __name__ == "__main__":
    main()
