# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
sys.path.insert(0, os.path.abspath('../../'))

project = 'pybackend'
copyright = '2023, unicorns'
author = 'unicorns'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'  # Change the theme to 'furo'

html_theme_options = {
    "dark_css_variables": {
        "color-brand-primary": "#ffc107",
        "color-brand-content": "#ffc107",
        "color-admonition-background": "#343a40",
        # ... add more customizations as needed ...
    },
}  # Add this dictionary to set the colors for dark mode

html_static_path = ['_static']