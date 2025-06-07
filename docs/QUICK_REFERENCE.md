# VeeDB Documentation Quick Reference

## 🚀 Quick Start Commands

### Build & Test
```bash
# Build documentation (clean)
cd docs && sphinx-build -W -b html . _build/html

# Run development helper
cd docs && python doc-dev.py build --clean

# Generate status report
cd docs && python generate-status.py
```

### Local Development
```bash
# Start development server
cd docs && python doc-dev.py serve

# Development mode (build + serve + watch)
cd docs && python doc-dev.py dev

# Watch for changes only
cd docs && python doc-dev.py watch
```

### Quality Checks
```bash
# Run comprehensive tests
cd docs && python test-docs.py

# Check for broken links
cd docs && python doc-dev.py check

# PowerShell build script
cd docs && .\build-docs.ps1
```

## 📁 Documentation Structure

```
docs/
├── index.rst              # Main documentation page
├── installation.rst       # Installation guide
├── quickstart.rst         # Quick start guide
├── authentication.rst     # Auth configuration
├── examples.rst           # Usage examples
├── filter_validation.rst  # Filter validation
├── changelog.rst          # Change log
├── contributing.rst       # Contributing guide
├── api/                   # API Reference
│   ├── client.rst         #   Client API
│   ├── exceptions.rst     #   Exceptions
│   ├── types.rst          #   Types
│   └── validation.rst     #   Validation
├── conf.py                # Sphinx configuration
├── requirements.txt       # Documentation deps
└── _build/html/           # Generated HTML
```

## 🎯 Key Features

- ✅ **Zero-warning builds** - Professional quality
- ✅ **Automated GitHub deployment** - Always up-to-date
- ✅ **Comprehensive API coverage** - All public modules
- ✅ **Modern responsive design** - Mobile-friendly
- ✅ **Development tools** - Build, serve, test, watch
- ✅ **Status monitoring** - Metrics and badges

## 🔗 Important URLs

- **GitHub Workflow**: `.github/workflows/docs.yml`
- **GitHub Pages**: Will be at `https://[username].github.io/veedb/`
- **Local Server**: `http://localhost:8000` (when serving)
- **Status Data**: `docs/_static/doc-status.json`

## 📊 Current Stats

- **RST Files**: 12
- **API Files**: 4  
- **Total Lines**: 3,794
- **Build Status**: ✅ Success
- **Last Update**: June 7, 2025

---
Ready for production! 🎉
