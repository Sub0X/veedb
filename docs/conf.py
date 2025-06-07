# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.abspath('../src'))

def get_version():
    """Read version from VERSION file."""
    version_file = os.path.join(os.path.dirname(__file__), "..", "src", "veedb", "VERSION")
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.1.0"  # fallback version

# Check if we're building on Read the Docs
on_rtd = os.environ.get('READTHEDOCS') == 'True'

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'VeeDB'
copyright = f'{datetime.now().year}, Sub0X'
author = 'Sub0X'
release = get_version()
version = release  # Short version for Read the Docs

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon', # For Google and NumPy style docstrings
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

# Add Read the Docs specific extensions
if on_rtd:
    extensions.append('sphinx.ext.githubpages')
else:
    extensions.append('sphinx_rtd_theme')

templates_path = ['_templates']
exclude_patterns = [
    '_build', 
    'Thumbs.db', 
    '.DS_Store',
    'doc-status.json',  # Exclude our status file from builds
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Read the Docs theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
}

# Additional Read the Docs configuration
html_title = f"{project} v{version}"
html_short_title = project
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

# For Read the Docs builds
if on_rtd:
    html_context = {
        'display_github': True,
        'github_user': 'Sub01',  # Replace with your GitHub username
        'github_repo': 'veedb',  # Replace with your repo name
        'github_version': 'main',
        'conf_py_path': '/docs/',
    }

# -- Autodoc options ---------------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '__init__',
    'show-inheritance': True,
}

# -- Napoleon settings -----------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Intersphinx mapping -----------------------------------------------------
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# -- EPUB options -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-epub-output

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_language = 'en'

# Exclude problematic files from EPUB builds
epub_exclude_files = [
    '.nojekyll',
    'doc-status.json',
]

# Handle unknown MIME types by excluding them
epub_pre_files = []
epub_post_files = []

# Additional EPUB configuration to prevent warnings
epub_use_index = True
epub_show_urls = 'footnote'
epub_basename = 'VeeDB'
