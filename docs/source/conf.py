"""
Configuration file for the Sphinx documentation builder.
"""

import os
import sys
from pathlib import Path

import nwm_eval

# ---------------------------------------------------------------------
# Ensure both packages are importable from src/ layout
# ---------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT / "nwm_eval" / "src"))
sys.path.insert(0, str(ROOT / "nwm_metrics" / "src"))

# ---------------------------------------------------------------------
# Import version safely (do NOT rely on __version__)
# ---------------------------------------------------------------------
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version

try:
    version = get_version("nwm_eval")
except PackageNotFoundError:
    version = "development"

release = version

# ---------------------------------------------------------------------
# Project information
# ---------------------------------------------------------------------
project = "nwm_eval"
copyright = "2026, RTX"
author = "Yuqiong Liu"

# ---------------------------------------------------------------------
# General configuration
# ---------------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "sphinx.ext.doctest",
    "myst_parser",
    "sphinx.ext.napoleon",
    "sphinx_design",
    "sphinx.ext.viewcode",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "amsmath",
    "substitution",
]

autosummary_generate = True
autosummary_generate_overwrite = True
templates_path = ["./_templates"]
exclude_patterns = ["production"]

master_doc = "index"

# ---------------------------------------------------------------------
# HTML output
# ---------------------------------------------------------------------
html_theme = "pydata_sphinx_theme"

html_css_files = ["custom.css"]

html_static_path = ["_static", "_images"]

html_js_files = [
    "form2yaml.js",
    "components/form-field.js",
    "https://unpkg.com/@popperjs/core@2",
    "https://unpkg.com/tippy.js@6",
]

html_theme_options = {
    "navbar_start": ["navbar-logo", "navbar-version"],
    "navbar_center": ["navbar-nav"],
    "navbar_persistent": ["search-button"],
    "navbar_align": "content",
    "header_links_before_dropdown": 5,
    # "show_toc_level": 3,
}

html_sidebars = {
    "user_guide": [],
    "faq": [],
}

# Substitutions
version = str(nwm_eval.__version__)

GITHUB_ORG = os.getenv("GITHUB_ORG", "NGWPC")

myst_substitutions = {
    "github_org": GITHUB_ORG,
    "github_org_lower": GITHUB_ORG.lower(),
    "pip_install_metrics": f"""```bash
pip install "git+https://github.com/{GITHUB_ORG}/nwm-eval-mgr.git@development#subdirectory=nwm_metrics"
```""",
    "pip_install_eval": f"""```bash
pip install "git+https://github.com/{GITHUB_ORG}/nwm-eval-mgr.git@development#subdirectory=nwm_eval"
```""",
    "pip_install_both": f"""```bash
pip install "git+https://github.com/{GITHUB_ORG}/nwm-eval-mgr.git@development#subdirectory=nwm_metrics"
pip install "git+https://github.com/{GITHUB_ORG}/nwm-eval-mgr.git@development#subdirectory=nwm_eval"
```""",
    "reproducible_install": f"""```bash
pip install "git+https://github.com/{GITHUB_ORG}/nwm-eval-mgr.git@<commit_sha>#subdirectory=nwm_metrics"
pip install "git+https://github.com/{GITHUB_ORG}/nwm-eval-mgr.git@<commit_sha>#subdirectory=nwm_eval"
```""",
    "reproducible_install_ex": f"""```bash
pip install "git+https://github.com/{GITHUB_ORG}/nwm-eval-mgr.git@87bcac530ca36a604da1ee27401f161a767f5c44#subdirectory=nwm_metrics"
```""",
    "clone_repo": f"""```bash
git clone https://github.com/{GITHUB_ORG}/nwm-eval-mgr.git
cd nwm-eval-mgr
```""",
}
