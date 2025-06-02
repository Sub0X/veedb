from setuptools import setup, find_packages

setup(
    name="veedb",
    version="0.1.0",
    author="Sub01",
    author_email="Sub01@subsoft.dev",
    description="An asynchronous Python wrapper for the VNDB.org API (Kana).",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sub0X/veedb",
    
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    install_requires=[
        "aiohttp>=3.8.0,<4.0.0",
        "dacite>=1.6.0,<2.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Internet",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    package_data={
        "veedb": ["py.typed"],
    },
)
