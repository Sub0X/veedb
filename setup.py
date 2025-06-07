from setuptools import setup, find_packages
import os

def get_version():
    """Read version from VERSION file."""
    version_file = os.path.join(os.path.dirname(__file__), "src", "veedb", "VERSION")
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.1.0"  # fallback version

def get_long_description():
    """Read the long description from README.md"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "An asynchronous Python wrapper for the VNDB API (Kana)."

setup(
    name="veedb",
    version=get_version(),
    author="Sub01",
    author_email="Sub01@subsoft.dev",    description="An asynchronous Python wrapper for the VNDB API (Kana).",    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sub0X/veedb",
    project_urls={
        "Documentation": "https://veedb.readthedocs.io/en/latest/",
        "Source Code": "https://github.com/Sub0X/veedb",
        "Bug Tracker": "https://github.com/Sub0X/veedb/issues",
        "Changelog": "https://veedb.readthedocs.io/en/latest/changelog.html",
    },
    
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    install_requires=[
        "aiohttp>=3.8.0,<4.0.0",
        "dacite>=1.6.0,<2.0.0",
    ],    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment",
        "Framework :: AsyncIO",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",    package_data={
        "veedb": ["py.typed", "VERSION"],
    },
)
