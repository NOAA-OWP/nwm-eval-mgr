# nwm-eval-mgr

A monorepo for evaluation and verification tools for the National Water Model (NWM) and NextGen simulations.

This repository provides two Python packages:

| Package | Description |
|----------|-------------|
| `nwm_metrics` | Core statistical metrics and evaluation functions |
| `nwm_eval` | End-to-end workflows for data retrieval, pairing, metrics calculation, and visualization |

---

## Repository Structure

```text
nwm-eval-mgr/
├── nwm_metrics/     # Core metrics library
├── nwm_eval/        # Evaluation workflow package
├── configs/         # Sample configuration files for nwm_eval workflows
├── docs/            # Sphinx documentation
└── tests/           # Shared test suite
```

---

## Package Relationship

```text
nwm_eval
    └── depends on
        nwm_metrics
```

- `nwm_metrics` provides reusable statistical and hydrologic evaluation functions.
- `nwm_eval` builds on these metrics to implement full evaluation and verification workflows.

---

## Installation

### Quick Install (Recommended)

Install directly from GitHub (no cloning required).

#### Install metrics only

{{ pip_install_metrics }}

#### Install evaluation workflows

{{ pip_install_eval }}

#### Install both packages

{{ pip_install_both }}

---

### Reproducible Install (Pinned Version)

For CI or reproducible workflows, install from a specific commit:

{{ reproducible_install }}

Example:

{{ reproducible_install_ex }}

---

### Development Install

Create a virtual environment

```bash
/usr/bin/python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

Clone the repository:

{{ clone_repo }}

Install packages in editable mode:

```bash
pip install -e nwm_metrics
pip install -e nwm_eval
```

Install development and documentation dependencies:

```bash
pip install -e .[dev,docs]
```

---

## Usage

### Using `nwm_metrics`

```python
from nwm_metrics import metric_functions as mf

kge = mf.kge(obs, sim)
nse = mf.nse(obs, sim)
```

---

### Running an evaluation workflow using `nwm_eval`

#### Set up configuration yaml file

Follow one of the sample config files at `configs/` to set up the configurations for your evaluation/verification application:
- `config_ngencerf.yaml`: ngenCERF-based single-location single-forecast verification
- `config_hindcast.yaml`: ngenCERF-based single-location multiple-hindcast verification
- `config_nwm.yaml`: NWM v30 operational forecasts verification
- `config_ngensim.yaml`: large-scale NGEN simulation evaluation (e.g., from regionalized simulations for a VPU)
- `config_template.yaml`: a template config file containing all available configuration options generated from the pydantic schema, which can be used as a reference for setting up your own config file.

{{ 'For detailed instructions on how to set up the configuration file, please refer to the [Configuration](https://{}.github.io/nwm-eval-mgr/config.html) and [FAQ](https://{}.github.io/nwm-eval-mgr/faq.html) pages of the `nwm-eval-mgr` [documentation](https://{}.github.io/nwm-eval-mgr/)'.format(github_org_lower, github_org_lower, github_org_lower) }}

#### Run evaluation/verification

```bash
python -m nwm_eval <path-to-config-file>
```
Example

```bash
python -m nwm_eval configs/config_hindcast.yaml
```

---

## Development

### Run tests

```bash
pytest
```

Markers available:

- `unit` – fast unit tests
- `integration` – pipeline integration tests
- `functional` – full workflow tests
- `slow` – long-running tests

Example:

```bash
pytest -m unit
```

---

### Code style

This project uses `ruff` for linting and formatting:

```bash
ruff check .
ruff format .
```

---

## Develop and build documentation

The project documentation is built with Sphinx and MyST. Several helper scripts under `docs/scripts/` generate content 
used by the documentation, including data schemas, configuration schema documentation, and input/output directory trees.

### Generate documentation content

Run the following scripts from the repository root when updating the corresponding documentation sections.

#### Generate data schemas

`docs/scripts/data_schemas.py` generates input and output data schema documentation in two steps.

First, create draft data description CSV files from sample files stored in S3:

```bash
python docs/scripts/data_schemas.py --step draft
```

Existing description CSV files are preserved, while missing files are created. The draft files are stored under:

```text
docs/scripts/data_desc/inputs/
docs/scripts/data_desc/outputs/
```

Manually update the draft CSV files to provide dataset and variable/column descriptions.

Then generate the RST schema documentation:

```bash
python docs/scripts/data_schemas.py --step schema
```

This reads the sample files from S3 together with the manually updated description CSV files and generates:

```text
docs/source/tech_reference/input_data.rst
docs/source/tech_reference/output_data.rst
```

AWS credentials must be available through environment variables or a `.env` file before running the script.

#### Generate configuration documentation

`docs/scripts/config_schemas.py` generates documentation for the configuration schemas and sample configuration files. It creates example YAML configuration files and Markdown tables describing configuration fields, including their types, descriptions, default values, and examples.

Run:

```bash
python docs/scripts/config_schemas.py
```

The generated documentation is saved to:

```text
docs/source/config_builder/index.md
```

#### Generate output directory tree

`docs/scripts/create_output_tree.py` generates Markdown directory trees for the sample output data. 

### Build the documentation

After generating or updating the documentation content, build the Sphinx documentation from the repository root:

```bash
make -C docs html
```

The generated HTML documentation will be available under:

```text
docs/build/
```

Open `docs/build/index.html` in a browser to review the documentation locally.

When developing documentation, regenerate the affected content first, then rebuild the html to verify that generated pages, cross-references, images, and formatting render correctly.

## Docker Container

### Requirements

To build and run `nwm_eval`, you will need:

* Docker Engine

### Build

From the repository root, build the container image:

```bash
docker build --tag nwm_eval .
```

### Container help

To display the container help message:

```bash
docker run nwm_eval
```

This will print the available commands supported by the container CLI:

```text
Usage: run-nwm-eval-mgr.sh <command> <config_file> [stdout_file]

COMMAND:
  verification          Run verification script.

CONFIG_FILE: Path to the configuration YAML file for a verification run.
STDOUT_FILE (optional): Path to a file where console output will be saved.

Examples:
  run-nwm-eval-mgr.sh verification test_data/verf_config.yaml
  run-nwm-eval-mgr.sh verification test_data/verf_config.yaml /path/to/output/nwm-eval.log
```

### Running a Verification Workflow

When running an evaluation or verification workflow, you will typically need to mount local data and configuration files into the container.

Example:

  ```bash
  docker run \
    -v $(pwd):$(pwd) \
    -w $(pwd) \
    nwm_eval \
    verification $(pwd)/configs/verf_config.yaml
  ```

Optionally redirect output to a file:

  ```bash
  docker run \
    -v $(pwd):$(pwd) \
    -w $(pwd) \
    nwm_eval \
    verification $(pwd)/configs/verf_config.yaml \
    $(pwd)/nwm_eval_output.log
  ```
### Notes

* File paths provided to the container must correspond to paths visible from within the container.
* Any paths referenced in the configuration file must also be valid within the container environment.
* If your workflow requires access to external datasets, ensure the corresponding directories are mounted into the container using Docker volume mounts (`-v`).


---
