@echo off
REM Build script for VeeDB documentation on Windows
REM Usage: make.bat [target]
REM   where target can be: html, clean, livehtml, etc.

pushd %~dp0

if "%1" == "" goto help
if "%1" == "clean" goto clean
if "%1" == "html" goto html
if "%1" == "livehtml" goto livehtml
if "%1" == "check" goto check
goto help

:help
echo.
echo VeeDB Documentation Build Script
echo ================================
echo.
echo Available targets:
echo   html      - Build HTML documentation
echo   clean     - Clean build directory
echo   livehtml  - Start live-reload server for development
echo   check     - Build and check for warnings/errors
echo.
goto end

:clean
echo Cleaning build directory...
if exist _build rmdir /s /q _build
echo Done.
goto end

:html
echo Building HTML documentation...
sphinx-build -b html . _build/html
if errorlevel 1 (
    echo Build failed!
    exit /b 1
)
echo.
echo Build finished. Documentation is in _build\html\index.html
goto end

:livehtml
echo Starting live-reload server...
echo Install sphinx-autobuild if not available: pip install sphinx-autobuild
sphinx-autobuild . _build/html --open-browser
goto end

:check
echo Building documentation with strict error checking...
sphinx-build -b html . _build/html -W
if errorlevel 1 (
    echo Build failed with warnings/errors!
    exit /b 1
)
echo.
echo Build passed all checks!
goto end

:end
popd
