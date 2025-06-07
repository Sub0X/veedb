#!/usr/bin/env python3
"""
Generate documentation status badges and metrics for VeeDB
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

def get_doc_stats():
    """Get documentation statistics"""
    docs_dir = Path(".")  # We're already in docs directory
    stats = {
        "rst_files": 0,
        "api_files": 0,
        "total_lines": 0,
        "last_build": None,
        "build_status": "unknown"
    }
      # Count RST files
    for rst_file in docs_dir.glob("**/*.rst"):
        stats["rst_files"] += 1
        # Check if file is in api subdirectory
        if rst_file.parent.name == "api":
            stats["api_files"] += 1
        
        # Count lines
        try:
            with open(rst_file, 'r', encoding='utf-8') as f:
                stats["total_lines"] += len(f.readlines())
        except:
            pass
    
    # Check build directory
    build_dir = docs_dir / "_build" / "html"
    if build_dir.exists():
        index_file = build_dir / "index.html"
        if index_file.exists():
            stats["last_build"] = datetime.fromtimestamp(
                index_file.stat().st_mtime
            ).isoformat()
            stats["build_status"] = "success"
    
    return stats

def generate_badges():
    """Generate badge URLs for documentation"""
    stats = get_doc_stats()
    badges = {
    "docs_status": f"https://img.shields.io/badge/docs-{stats['build_status']}-{'green' if stats['build_status'] == 'success' else 'red'}",
    "rst_files": f"https://img.shields.io/badge/RST%20files-{stats['rst_files']}-blue",
    "api_docs": f"https://img.shields.io/badge/API%20docs-{stats['api_files']}-blue",
    "lines": f"https://img.shields.io/badge/doc%20lines-{stats['total_lines']}-blue",
    "readthedocs": "https://img.shields.io/readthedocs/veedb?label=Read%20the%20Docs",
    "rtd_version": "https://img.shields.io/readthedocs/veedb/latest?label=latest"
    }
    
    return badges, stats

def generate_status_json():
    """Generate JSON status file for GitHub Pages"""
    badges, stats = generate_badges()
    
    status_data = {
        "generated_at": datetime.now().isoformat(),
        "documentation": {
            "status": stats["build_status"],
            "last_build": stats["last_build"],
            "statistics": {
                "rst_files": stats["rst_files"],
                "api_files": stats["api_files"],
                "total_lines": stats["total_lines"]
            }
        },
        "badges": badges
    }
      # Write to docs directory for inclusion in build
    status_file = Path("_static/doc-status.json")
    status_file.parent.mkdir(exist_ok=True)
    
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    return status_data

def print_status():
    """Print documentation status to console"""
    status = generate_status_json()
    
    print("📚 VeeDB Documentation Status")
    print("=" * 30)
    print(f"Build Status: {status['documentation']['status']}")
    print(f"RST Files: {status['documentation']['statistics']['rst_files']}")
    print(f"API Files: {status['documentation']['statistics']['api_files']}")
    print(f"Total Lines: {status['documentation']['statistics']['total_lines']}")
    
    if status['documentation']['last_build']:
        build_time = datetime.fromisoformat(status['documentation']['last_build'])
        print(f"Last Build: {build_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🏷️ Badge URLs:")
    for name, url in status['badges'].items():
        print(f"{name}: {url}")

if __name__ == "__main__":
    print_status()
