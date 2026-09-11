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

```bash
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@development#subdirectory=nwm_metrics"
```

#### Install evaluation workflows

```bash
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@development#subdirectory=nwm_eval"
```

#### Install both packages

```bash
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@development#subdirectory=nwm_metrics"
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@development#subdirectory=nwm_eval"
```

---

### Reproducible Install (Pinned Version)

For CI or reproducible workflows, install from a specific commit:

```bash
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@<commit_sha>#subdirectory=nwm_metrics"
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@<commit_sha>#subdirectory=nwm_eval"
```

Example:

```bash
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@87bcac530ca36a604da1ee27401f161a767f5c44#subdirectory=nwm_metrics"
```

---

### Development Install

Create a virtual environment

```bash
/usr/bin/python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

Clone the repository:

```bash
git clone https://github.com/NGWPC/nwm-eval-mgr.git
cd nwm-eval-mgr
```

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

Follow one of the sample config files (see `nwm-eval-mgr/configs`) to set up the configurations for your evaluation/verification application:
- `config_ngencerf.yaml`: ngenCERF-based single-location single-forecast verification
- `config_hindcast.yaml`: ngenCERF-based single-location multiple-hindcast verification
- `config_nwm.yaml`: NWM v30 operational forecasts verification
- `config_ngensim.yaml`: large-scale NGEN simulation evaluation (e.g., from regionalized simulations for a VPU)
- `config_template.yaml`: a template config file containing all available configuration options generated from the pydantic schema, which can be used as a reference for setting up your own config file.

For detailed instructions on how to set up the configuration file, please refer to the [Configuration](https://ngwpc.github.io/nwm-eval-mgr/config.html) and [FAQ](https://ngwpc.github.io/nwm-eval-mgr/faq.html) pages of the `nwm-eval-mgr` [documentation](https://ngwpc.github.io/nwm-eval-mgr/).

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

## Documentation

Documentation is built using Sphinx and located in the `docs/` directory, and hosted on 
[Github Pages](https://ngwpc.github.io/nwm-eval-mgr/).

To build docs:

```bash
pip install -e .[docs]
make -C docs html
```

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

## License

License information to be added.