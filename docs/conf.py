"""Sphinx configuration."""
project = "PatternCounter"
author = "Joao Felipe Pimentel"
copyright = "2022, Joao Felipe Pimentel"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
