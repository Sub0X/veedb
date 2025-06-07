#!/usr/bin/env python3
"""
Prepare documentation for release
This script updates version info and generates release-ready documentation
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def get_version():
    """Get current version from VERSION file or git tag"""
    version_file = Path("../src/veedb/VERSION")
    if version_file.exists():
        return version_file.read_text().strip()
    
    # Try to get from git
    try:
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "development"

def update_changelog():
    """Update changelog with release information"""
    changelog_path = Path("changelog.rst")
    version = get_version()
    
    if not changelog_path.exists():
        return
    
    content = changelog_path.read_text()
    
    # Check if this version is already in changelog
    if f"Version {version}" in content:
        print(f"Version {version} already exists in changelog")
        return
    
    # Add new version entry
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"""
Version {version} ({today})
{'-' * (len(f'Version {version} ({today})'))}

* Documentation improvements and updates
* API documentation enhancements

"""
    
    # Insert after the header
    lines = content.split('\n')
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith('='):
            header_end = i + 1
            break
    
    lines.insert(header_end + 1, new_entry)
    changelog_path.write_text('\n'.join(lines))
    print(f"Updated changelog with version {version}")

def update_conf_py():
    """Update conf.py with current version"""
    conf_path = Path("conf.py")
    version = get_version()
    
    if not conf_path.exists():
        return
    
    content = conf_path.read_text()
    
    # Update version and release
    content = re.sub(r"version = '[^']*'", f"version = '{version}'", content)
    content = re.sub(r"release = '[^']*'", f"release = '{version}'", content)
    
    conf_path.write_text(content)
    print(f"Updated conf.py with version {version}")

def generate_api_docs():
    """Generate API documentation using sphinx-apidoc"""
    try:
        subprocess.run([
            'sphinx-apidoc', '-f', '-o', 'api', '../src/veedb', 
            '--module-first', '--no-toc'
        ], check=True)
        print("Generated API documentation")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate API docs: {e}")

def build_docs():
    """Build documentation"""
    try:
        subprocess.run(['sphinx-build', '-b', 'html', '.', '_build/html', '-W'], 
                      check=True)
        print("Documentation built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build documentation: {e}")
        return False

def main():
    """Main release preparation"""
    print("🚀 Preparing VeeDB Documentation for Release")
    print("=" * 50)
    
    os.chdir(Path(__file__).parent)
    
    version = get_version()
    print(f"Current version: {version}")
    
    # Update version information
    update_conf_py()
    update_changelog()
    
    # Generate API documentation
    generate_api_docs()
    
    # Build documentation
    if build_docs():
        print("\n✅ Documentation release preparation complete!")
        print(f"Documentation built for version {version}")
        print("Ready for deployment to GitHub Pages")
    else:
        print("\n❌ Documentation build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
