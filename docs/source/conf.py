# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ssmixtwins"
copyright = "2025, Yu Akagi, MD"
author = "Yu Akagi, MD"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Extended by the author --
html_show_sourcelink = False
autodoc_default_options = {}
html_css_files = [
    "color_theme.css",
]

# -- Hide or show the Sphinx link in the HTML output --
html_show_sphinx = False

# -- Custom logo and theme options ------------------------------------------
html_logo = "_static/logo.png"
html_theme_options = {
    "logo_only": True,  # Only show the logo (no title text)
    "display_version": False,  # Optional: hides the version string
}


def setup(app):
    app.add_css_file("color_theme.css")
