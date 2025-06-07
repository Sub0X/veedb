#!/usr/bin/env python3
"""
Documentation development server for VeeDB
Provides easy local development with hot-reload functionality
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import sphinx
        import sphinx_autobuild
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install sphinx sphinx-autobuild")
        return False
    return True

def build_docs(source_dir=".", build_dir="_build/html", clean=False):
    """Build documentation once"""
    if clean and os.path.exists(build_dir):
        import shutil
        shutil.rmtree(build_dir)
        print(f"Cleaned {build_dir}")
    
    cmd = ["sphinx-build", "-b", "html", source_dir, build_dir, "-W"]
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd="docs")
    if result.returncode == 0:
        print(f"\n✅ Documentation built successfully!")
        print(f"📄 Open: file://{Path('docs').absolute() / build_dir / 'index.html'}")
    else:
        print(f"\n❌ Documentation build failed!")
        sys.exit(1)

def serve_docs(host="localhost", port=8000, source_dir=".", build_dir="_build/html"):
    """Serve documentation with hot-reload"""
    cmd = [
        "sphinx-autobuild",
        source_dir,
        build_dir,
        "--host", host,
        "--port", str(port),
        "--open-browser",
        "--watch", "../src",  # Watch source code changes too
    ]
    
    print(f"🚀 Starting documentation server at http://{host}:{port}")
    print("📝 Documentation will auto-rebuild on changes")
    print("🔍 Watching: docs/ and src/ directories")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        subprocess.run(cmd, cwd="docs")
    except KeyboardInterrupt:
        print("\n👋 Documentation server stopped")

def main():
    parser = argparse.ArgumentParser(description="VeeDB Documentation Development Tool")
    parser.add_argument("command", choices=["build", "serve"], help="Command to run")
    parser.add_argument("--clean", action="store_true", help="Clean build directory first")
    parser.add_argument("--host", default="localhost", help="Host for serve command")
    parser.add_argument("--port", type=int, default=8000, help="Port for serve command")
    
    args = parser.parse_args()
    
    if not check_dependencies():
        sys.exit(1)
    
    if args.command == "build":
        build_docs(clean=args.clean)
    elif args.command == "serve":
        serve_docs(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
