# VeeDB Documentation Build Script for PowerShell
# Usage: .\build-docs.ps1 [command] [options]

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "serve", "clean", "check", "install-deps")]
    [string]$Command = "build",
      [switch]$Clean,
    [string]$ServerHost = "localhost",
    [int]$Port = 8000,
    [switch]$Help
)

function Show-Help {
    Write-Host ""
    Write-Host "VeeDB Documentation Build Script" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  build        Build HTML documentation (default)"
    Write-Host "  serve        Start development server with hot-reload"
    Write-Host "  clean        Clean build directory"
    Write-Host "  check        Build with strict error checking"
    Write-Host "  install-deps Install documentation dependencies"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Clean       Clean build directory before building"
    Write-Host "  -Host        Host for serve command (default: localhost)"
    Write-Host "  -Port        Port for serve command (default: 8000)"
    Write-Host "  -Help        Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\build-docs.ps1 build"
    Write-Host "  .\build-docs.ps1 serve -Port 8080"
    Write-Host "  .\build-docs.ps1 build -Clean"
    Write-Host "  .\build-docs.ps1 check"
    Write-Host ""
}

function Test-Dependencies {
    try {
        $null = Get-Command python -ErrorAction Stop
        $sphinxResult = python -c "import sphinx; print('OK')" 2>$null
        if ($sphinxResult -ne "OK") {
            Write-Host "❌ Sphinx not found. Run: .\build-docs.ps1 install-deps" -ForegroundColor Red
            return $false
        }
        return $true
    }
    catch {
        Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
        return $false
    }
}

function Install-Dependencies {
    Write-Host "📦 Installing documentation dependencies..." -ForegroundColor Blue
    
    # Navigate to project root to install package
    Push-Location ..
    try {
        python -m pip install --upgrade pip
        python -m pip install -e .
        python -m pip install -r docs/requirements.txt
        python -m pip install dacite sphinx-autobuild
        Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to install dependencies: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        Pop-Location
    }
    return $true
}

function Build-Documentation {
    param([bool]$StrictMode = $false)
    
    Write-Host "🔨 Building documentation..." -ForegroundColor Blue
    
    if ($Clean -and (Test-Path "_build")) {
        Write-Host "🧹 Cleaning build directory..." -ForegroundColor Yellow
        Remove-Item "_build" -Recurse -Force
    }
    
    $buildArgs = @("sphinx-build", "-b", "html", ".", "_build/html")
    if ($StrictMode) {
        $buildArgs += "-W"
        Write-Host "🔍 Running in strict mode (warnings as errors)" -ForegroundColor Yellow
    }
    
    Push-Location docs
    try {        $buildResult = & python -m $buildArgs
        if ($LASTEXITCODE -eq 0) {
            $indexPath = Resolve-Path "_build/html/index.html"
            Write-Host ""
            Write-Host "✅ Documentation built successfully!" -ForegroundColor Green
            Write-Host "📄 Open: file:///$($indexPath.Path.Replace('\', '/'))" -ForegroundColor Cyan
            Write-Host ""
        }
        else {
            Write-Host "❌ Documentation build failed!" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Build error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        Pop-Location
    }
    return $true
}

function Start-DevServer {
    Write-Host "🚀 Starting documentation development server..." -ForegroundColor Blue
    Write-Host "📍 Server: http://$Host`:$Port" -ForegroundColor Cyan
    Write-Host "📝 Auto-rebuild on file changes enabled" -ForegroundColor Green
    Write-Host "🛑 Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    Push-Location docs
    try {
        python -m sphinx_autobuild . _build/html --host $Host --port $Port --open-browser --watch ../src
    }
    catch {
        Write-Host "❌ Server error: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Pop-Location
    }
}

function Remove-BuildDirectory {
    if (Test-Path "docs/_build") {
        Write-Host "🧹 Cleaning build directory..." -ForegroundColor Yellow
        Remove-Item "docs/_build" -Recurse -Force
        Write-Host "✅ Build directory cleaned!" -ForegroundColor Green
    }
    else {
        Write-Host "ℹ️ Build directory already clean." -ForegroundColor Blue
    }
}

# Main script logic
if ($Help) {
    Show-Help
    exit 0
}

if (-not (Test-Dependencies)) {
    Write-Host ""
    Write-Host "💡 Run '.\build-docs.ps1 install-deps' to install required dependencies." -ForegroundColor Yellow
    exit 1
}

switch ($Command) {
    "build" {
        Build-Documentation
    }
    "serve" {
        Start-DevServer
    }
    "clean" {
        Clean-BuildDirectory
    }
    "check" {
        Build-Documentation -StrictMode $true
    }
    "install-deps" {
        Install-Dependencies
    }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
