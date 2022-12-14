# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'Conservator CLI'
copyright = '2022, Teledyne FLIR LLC'
author = 'Teledyne FLIR LLC'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']

html_favicon = "_static/favicon.ico"
html_logo = "_static/logo.webp"

html_theme = 'sphinx_rtd_theme'

# --------------


html_show_sphinx = False
html_show_sourcelink = False

html_logo    = "_static/conservator-cli-guide.svg"
html_favicon = '_static/favicon.ico'
html_theme_options = {
    'logo_only': True,
}

exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']