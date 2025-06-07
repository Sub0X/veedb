# 📚 Read the Docs Setup Guide for VeeDB

## 🚀 Quick Setup Steps

### 1. **Create Read the Docs Account**
1. Go to [https://readthedocs.org/](https://readthedocs.org/)
2. Sign up with your GitHub account
3. Authorize Read the Docs to access your repositories

### 2. **Import Your Project**
1. Click "Import a Project" on your Read the Docs dashboard
2. Select "Import from GitHub"
3. Find and select your `veedb` repository
4. Click "Import Project"

### 3. **Configure Project Settings**
The project will be automatically configured using our `.readthedocs.yaml` file, but you can customize:

**Project Details:**
- **Name**: `veedb` (will create URL: `https://veedb.readthedocs.io/`)
- **Description**: "An asynchronous Python wrapper for the VNDB API (Kana)"
- **Language**: English
- **Programming Language**: Python

**Advanced Settings:**
- **Default branch**: `main` or `master`
- **Default version**: `latest`
- **Privacy Level**: Public (recommended for open source)

### 4. **Webhook Configuration** ✅
Read the Docs automatically creates webhooks when you import via GitHub, so documentation will rebuild automatically on:
- Push to main/master branch
- New releases/tags
- Pull requests (for preview builds)

## 📋 What's Already Configured

### ✅ **Read the Docs Configuration** (`.readthedocs.yaml`)
```yaml
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: "3.11"
sphinx:
  builder: html
  configuration: docs/conf.py
  fail_on_warning: true
formats:
  - pdf
  - epub
python:
  install:
    - method: pip
      path: .
    - requirements: docs/requirements.txt
```

### ✅ **Sphinx Configuration** (`docs/conf.py`)
- Read the Docs theme integration
- GitHub integration for "Edit on GitHub" links
- Optimized navigation and search
- PDF/ePub support

### ✅ **GitHub Workflow** (`.github/workflows/docs.yml`)
- Tests documentation builds locally before Read the Docs
- Validates Read the Docs configuration
- Provides build previews for pull requests
- Generates documentation metrics

## 🌐 Documentation URLs

After setup, your documentation will be available at:

### **Main Documentation**
- **Latest**: `https://veedb.readthedocs.io/en/latest/`
- **Stable**: `https://veedb.readthedocs.io/en/stable/`

### **Version-Specific**
- **By Tag**: `https://veedb.readthedocs.io/en/v1.0.0/`
- **By Branch**: `https://veedb.readthedocs.io/en/main/`

### **Additional Formats**
- **PDF**: `https://veedb.readthedocs.io/_/downloads/en/latest/pdf/`
- **ePub**: `https://veedb.readthedocs.io/_/downloads/en/latest/epub/`

## 🔧 Advanced Configuration

### **Custom Domain** (Optional)
1. Go to your project settings on Read the Docs
2. Navigate to "Domains" section
3. Add your custom domain (e.g., `docs.yourdomain.com`)
4. Configure DNS CNAME record pointing to `readthedocs.io`

### **Notifications**
1. Go to project settings → "Notifications"
2. Configure email notifications for build failures
3. Set up Slack/Discord webhooks if desired

### **Versioning Strategy**
Read the Docs will automatically:
- Build `latest` from your default branch
- Build `stable` from your latest tag
- Build specific versions for each Git tag

## 🎯 Best Practices

### **Branch Strategy**
- **main/master**: Always deployable, triggers `latest` docs
- **Tags**: Create Git tags for releases, triggers versioned docs
- **Feature branches**: Can be configured for preview builds

### **Documentation Workflow**
1. **Development**: Write docs in feature branches
2. **Review**: GitHub workflow validates builds on PR
3. **Merge**: Automatic deployment to `latest` on merge
4. **Release**: Tag releases for stable versioned docs

### **Maintenance**
- Monitor build status on Read the Docs dashboard
- Check build logs for any issues
- Update dependencies in `docs/requirements.txt` as needed

## 🔍 Troubleshooting

### **Build Failures**
1. Check Read the Docs build logs
2. Test locally: `cd docs && sphinx-build -b html . _build/html -W`
3. Verify all dependencies in `docs/requirements.txt`

### **Missing Content**
1. Ensure all RST files are properly linked in `index.rst`
2. Check for typos in cross-references
3. Validate with: `python docs/test-docs.py`

### **GitHub Integration Issues**
1. Re-sync repository in Read the Docs settings
2. Check webhook configuration in GitHub repo settings
3. Verify permissions for Read the Docs GitHub app

## ✅ Validation Checklist

Before going live, verify:
- [ ] Project imported successfully on Read the Docs
- [ ] First build completed without errors
- [ ] Documentation accessible at `https://veedb.readthedocs.io/`
- [ ] GitHub webhooks working (push to trigger rebuild)
- [ ] PDF/ePub downloads available
- [ ] Search functionality working
- [ ] "Edit on GitHub" links functional

## 🎉 You're All Set!

Once configured, your VeeDB documentation will:
- ✅ **Auto-deploy** on every push to main
- ✅ **Version automatically** with Git tags
- ✅ **Provide multiple formats** (HTML, PDF, ePub)
- ✅ **Include search** functionality
- ✅ **Support themes** and customization
- ✅ **Integrate with GitHub** for easy editing

---
**Next Step**: Import your project at [readthedocs.org](https://readthedocs.org/) and start enjoying professional documentation hosting! 🚀
