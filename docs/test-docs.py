#!/usr/bin/env python3
"""
Documentation testing and validation for VeeDB.
Runs comprehensive tests to ensure documentation quality.
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import re

class DocTester:
    def __init__(self):
        self.docs_dir = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
    
    def run_test(self, name, test_func):
        """Run a single test and record results"""
        print(f"\n🧪 Testing: {name}")
        try:
            result = test_func()
            status = "PASS" if result else "FAIL"
            print(f"   {status}")
            
            self.results["tests"][name] = {
                "status": status,
                "passed": result,
                "details": getattr(test_func, '_details', None)
            }
            
            if result:
                self.results["summary"]["passed"] += 1
            else:
                self.results["summary"]["failed"] += 1
            
            self.results["summary"]["total"] += 1
            return result
        except Exception as e:
            print(f"   ERROR: {e}")
            self.results["tests"][name] = {
                "status": "ERROR",
                "passed": False,
                "error": str(e)
            }
            self.results["summary"]["failed"] += 1
            self.results["summary"]["total"] += 1
            return False
    
    def test_build_clean(self):
        """Test that documentation builds without warnings"""
        cmd = ["sphinx-build", "-W", "-b", "html", ".", "_build/test"]
        try:
            result = subprocess.run(
                cmd, cwd=self.docs_dir, 
                capture_output=True, text=True, check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.test_build_clean._details = f"Build errors:\n{e.stderr}"
            return False
    
    def test_rst_syntax(self):
        """Test RST file syntax"""
        errors = []
        for rst_file in self.docs_dir.glob("**/*.rst"):
            try:
                with open(rst_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for common RST issues
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    # Check title underlines
                    if i < len(lines) and lines[i].strip() and set(lines[i].strip()) <= set('=-~^'):
                        title_line = lines[i-1] if i > 0 else ""
                        underline = lines[i]
                        if len(title_line.strip()) != len(underline.strip()):
                            errors.append(f"{rst_file}:{i+1} - Title/underline length mismatch")
                
            except Exception as e:
                errors.append(f"{rst_file} - Read error: {e}")
        
        if errors:
            self.test_rst_syntax._details = "\n".join(errors[:10])  # Limit output
            return False
        return True
    
    def test_api_docs_exist(self):
        """Test that API documentation files exist"""
        required_api_docs = ["client.rst", "exceptions.rst", "types.rst", "validation.rst"]
        api_dir = self.docs_dir / "api"
        
        missing = []
        for doc in required_api_docs:
            if not (api_dir / doc).exists():
                missing.append(doc)
        
        if missing:
            self.test_api_docs_exist._details = f"Missing API docs: {', '.join(missing)}"
            return False
        return True
    
    def test_links_internal(self):
        """Test internal documentation links"""
        cmd = ["sphinx-build", "-b", "linkcheck", ".", "_build/linkcheck"]
        try:
            result = subprocess.run(
                cmd, cwd=self.docs_dir,
                capture_output=True, text=True, timeout=60
            )
            
            # Check linkcheck output
            linkcheck_dir = self.docs_dir / "_build" / "linkcheck"
            output_file = linkcheck_dir / "output.txt"
            
            if output_file.exists():
                with open(output_file) as f:
                    content = f.read()
                    if "broken" in content.lower():
                        self.test_links_internal._details = "Broken links found in output.txt"
                        return False
            
            return True
        except subprocess.TimeoutExpired:
            self.test_links_internal._details = "Link check timed out"
            return False
        except Exception as e:
            self.test_links_internal._details = f"Link check error: {e}"
            return False
    
    def test_code_examples(self):
        """Test that code examples are valid"""
        # Find Python code blocks in RST files
        python_blocks = []
        for rst_file in self.docs_dir.glob("**/*.rst"):
            try:
                with open(rst_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract Python code blocks
                in_code_block = False
                code_lines = []
                
                for line in content.split('\n'):
                    if line.strip().startswith('.. code-block:: python'):
                        in_code_block = True
                        code_lines = []
                        continue
                    elif in_code_block and line.strip() and not line.startswith('   '):
                        # End of code block
                        if code_lines:
                            python_blocks.append((rst_file, '\n'.join(code_lines)))
                        in_code_block = False
                        code_lines = []
                    elif in_code_block and line.startswith('   '):
                        code_lines.append(line[4:])  # Remove indentation
                
            except Exception:
                continue
        
        # Test code blocks for syntax errors
        errors = []
        for rst_file, code in python_blocks:
            try:
                compile(code, f"<{rst_file}>", "exec")
            except SyntaxError as e:
                errors.append(f"{rst_file} - Syntax error: {e}")
        
        if errors:
            self.test_code_examples._details = "\n".join(errors[:5])
            return False
        return True
    
    def test_documentation_coverage(self):
        """Test documentation coverage of code"""
        # Check that main modules are documented
        src_dir = self.docs_dir.parent / "src" / "veedb"
        if not src_dir.exists():
            self.test_documentation_coverage._details = "Source directory not found"
            return False
        
        # Get Python files
        py_files = list(src_dir.glob("*.py"))
        if not py_files:
            self.test_documentation_coverage._details = "No Python files found in src"
            return False
        
        # Check if API docs mention the modules
        api_dir = self.docs_dir / "api"
        api_content = ""
        for api_file in api_dir.glob("*.rst"):
            with open(api_file) as f:
                api_content += f.read()
        
        documented_modules = []
        for py_file in py_files:
            module_name = py_file.stem
            if module_name in ["__init__", "test"]:
                continue
            if f"veedb.{module_name}" in api_content:
                documented_modules.append(module_name)
        
        if len(documented_modules) < 2:  # Expect at least client and exceptions
            self.test_documentation_coverage._details = f"Only {len(documented_modules)} modules documented"
            return False
        return True
    
    def test_status_generation(self):
        """Test that status generation works"""
        try:
            result = subprocess.run(
                ["python", "generate-status.py"], 
                cwd=self.docs_dir, 
                capture_output=True, text=True, check=True
            )
            
            # Check that status file was created
            status_file = self.docs_dir / "_static" / "doc-status.json"
            if not status_file.exists():
                self.test_status_generation._details = "Status JSON file not created"
                return False
            
            # Validate JSON
            with open(status_file) as f:
                status_data = json.load(f)
            
            required_keys = ["generated_at", "documentation", "badges"]
            for key in required_keys:
                if key not in status_data:
                    self.test_status_generation._details = f"Missing key in status: {key}"
                    return False
            
            return True
        except Exception as e:
            self.test_status_generation._details = f"Status generation failed: {e}"
            return False
    
    def run_all_tests(self):
        """Run all documentation tests"""
        print("🧪 VeeDB Documentation Test Suite")
        print("=" * 40)
        
        tests = [
            ("RST Syntax", self.test_rst_syntax),
            ("API Docs Exist", self.test_api_docs_exist),
            ("Clean Build", self.test_build_clean),
            ("Status Generation", self.test_status_generation),
            ("Code Examples", self.test_code_examples),
            ("Documentation Coverage", self.test_documentation_coverage),
            ("Internal Links", self.test_links_internal),
        ]
        
        for name, test_func in tests:
            self.run_test(name, test_func)
        
        # Print summary
        print("\n" + "=" * 40)
        print("📊 Test Summary:")
        print(f"   ✅ Passed: {self.results['summary']['passed']}")
        print(f"   ❌ Failed: {self.results['summary']['failed']}")
        print(f"   📝 Total:  {self.results['summary']['total']}")
        
        success_rate = (self.results['summary']['passed'] / self.results['summary']['total']) * 100
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        results_file = self.docs_dir / "_build" / "test-results.json"
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return self.results['summary']['failed'] == 0

def main():
    tester = DocTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
