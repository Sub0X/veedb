#!/usr/bin/env python3
"""
Development helper for VeeDB documentation.
Provides commands for building, serving, and testing documentation locally.
"""

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os

def build_docs(clean=False, warnings_as_errors=True):
    """Build the documentation"""
    docs_dir = Path(__file__).parent
    build_dir = docs_dir / "_build"
    
    if clean and build_dir.exists():
        print("🧹 Cleaning build directory...")
        import shutil
        shutil.rmtree(build_dir)
    
    print("📚 Building documentation...")
    cmd = ["sphinx-build", "-b", "html", ".", "_build/html"]
    if warnings_as_errors:
        cmd.append("-W")
    
    try:
        result = subprocess.run(cmd, cwd=docs_dir, check=True, capture_output=True, text=True)
        print("✅ Documentation built successfully!")
        print(f"📁 Output: {build_dir / 'html' / 'index.html'}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def serve_docs(port=8000, open_browser=True):
    """Serve documentation locally"""
    docs_dir = Path(__file__).parent
    html_dir = docs_dir / "_build" / "html"
    
    if not html_dir.exists():
        print("❌ No built documentation found. Run 'build' first.")
        return False
    
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(html_dir), **kwargs)
    
    server = HTTPServer(('localhost', port), Handler)
    url = f"http://localhost:{port}"
    
    print(f"🌐 Serving documentation at {url}")
    print("Press Ctrl+C to stop the server")
    
    if open_browser:
        # Give server a moment to start
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()
        return True

def watch_and_rebuild():
    """Watch for changes and rebuild automatically"""
    try:
        import watchdog
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("❌ watchdog not installed. Install with: pip install watchdog")
        return False
    
    docs_dir = Path(__file__).parent
    
    class DocHandler(FileSystemEventHandler):
        def __init__(self):
            self.last_rebuild = 0
            
        def on_modified(self, event):
            if event.is_directory:
                return
            
            # Only rebuild for relevant files
            if not any(event.src_path.endswith(ext) for ext in ['.rst', '.py', '.toml']):
                return
                
            # Avoid rebuilding too frequently
            now = time.time()
            if now - self.last_rebuild < 2:
                return
            
            self.last_rebuild = now
            print(f"\n📝 Change detected: {event.src_path}")
            build_docs(clean=False, warnings_as_errors=False)
    
    event_handler = DocHandler()
    observer = Observer()
    observer.schedule(event_handler, str(docs_dir), recursive=True)
    observer.start()
    
    print("👀 Watching for changes... Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Stopped watching")
    
    observer.join()
    return True

def check_links():
    """Check for broken links in documentation"""
    docs_dir = Path(__file__).parent
    print("🔗 Checking links...")
    
    cmd = ["sphinx-build", "-b", "linkcheck", ".", "_build/linkcheck"]
    
    try:
        result = subprocess.run(cmd, cwd=docs_dir, check=True, capture_output=True, text=True)
        print("✅ Link check completed!")
        
        # Show results
        linkcheck_dir = docs_dir / "_build" / "linkcheck"
        output_file = linkcheck_dir / "output.txt"
        if output_file.exists():
            print(f"📄 Results saved to: {output_file}")
            with open(output_file) as f:
                content = f.read()
                if "broken" in content.lower():
                    print("⚠️  Some broken links found:")
                    print(content)
                else:
                    print("✅ No broken links found!")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Link check failed!")
        print("STDERR:", e.stderr)
        return False

def generate_status():
    """Generate documentation status and badges"""
    docs_dir = Path(__file__).parent
    print("📊 Generating documentation status...")
    
    try:
        result = subprocess.run(["python", "generate-status.py"], cwd=docs_dir, check=True)
        print("✅ Status generated successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Status generation failed!")
        return False

def main():
    parser = argparse.ArgumentParser(description="VeeDB Documentation Development Helper")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build documentation")
    build_parser.add_argument("--clean", action="store_true", help="Clean build directory first")
    build_parser.add_argument("--no-warnings-as-errors", action="store_true", help="Don't treat warnings as errors")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Serve documentation locally")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    serve_parser.add_argument("--no-open", action="store_true", help="Don't open browser automatically")
    
    # Watch command
    subparsers.add_parser("watch", help="Watch for changes and rebuild automatically")
    
    # Check command
    subparsers.add_parser("check", help="Check for broken links")
    
    # Status command
    subparsers.add_parser("status", help="Generate documentation status")
    
    # Dev command (build + serve + watch)
    dev_parser = subparsers.add_parser("dev", help="Development mode: build, serve, and watch")
    dev_parser.add_argument("--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "build":
        success = build_docs(
            clean=args.clean,
            warnings_as_errors=not args.no_warnings_as_errors
        )
        sys.exit(0 if success else 1)
    
    elif args.command == "serve":
        success = serve_docs(port=args.port, open_browser=not args.no_open)
        sys.exit(0 if success else 1)
    
    elif args.command == "watch":
        success = watch_and_rebuild()
        sys.exit(0 if success else 1)
    
    elif args.command == "check":
        success = check_links()
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        success = generate_status()
        sys.exit(0 if success else 1)
    
    elif args.command == "dev":
        # Development mode: build, then serve with watch in background
        print("🚀 Starting development mode...")
        
        # Build first
        if not build_docs(clean=False, warnings_as_errors=False):
            print("❌ Initial build failed")
            sys.exit(1)
        
        # Start watch in background thread
        def watch_thread():
            watch_and_rebuild()
        
        watcher = threading.Thread(target=watch_thread, daemon=True)
        watcher.start()
        
        # Serve (this will block until Ctrl+C)
        serve_docs(port=args.port, open_browser=True)

if __name__ == "__main__":
    main()
