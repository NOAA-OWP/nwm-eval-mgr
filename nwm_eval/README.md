# nwm_eval

End-to-end evaluation and verification workflows for National Water Model (NWM) and NextGen simulations.

This package integrates data handling, pairing, metric computation, and visualization into a unified evaluation framework.

---

## Purpose

`nwm_eval` provides **complete evaluation workflows**, including:

- data retrieval
- observation/model pairing
- metric computation (via `nwm_metrics`)
- visualization

---

## Features

- Retrieval of forecast and observation datasets
- Spatial and temporal data pairing
- Evaluation metric computation (via `nwm_metrics`)
- Plot generation for diagnostics and model performance
- Summary statistics tables
- Config-driven evaluation workflows

---

## Dependency

This package depends on:

- `nwm_metrics`

Make sure it is installed alongside `nwm_eval`.

---

## Installation
### Quick Install (Recommended)
Install directly from GitHub (no cloning required).

```bash
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@development#subdirectory=nwm_metrics"
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@development#subdirectory=nwm_eval"
```

### Development install

```bash
git clone https://github.com/NGWPC/nwm-eval-mgr.git
cd nwm-eval-mgr
pip install -e nwm_metrics
pip install -e nwm_eval
```

---

## Usage

### Set up configuration yaml file

Follow one of the sample config files (see `nwm-eval-mgr/configs`) to set up the configurations for your evaluation/verification application:
- `config_ngencerf.yaml`: ngenCERF-based single-location single-forecast verification
- `config_hindcast.yaml`: ngenCERF-based single-location multiple-hindcast verification
- `config_nwm.yaml`: NWM v30 operational forecasts verification
- `config_ngensim.yaml`: large-scale NGEN simulation evaluation (e.g., from regionalized simulations for a VPU)
- `config_template.yaml`: a template config file containing all available configuration options generated from the pydantic schema, which can be used as a reference for setting up your own config file.

For detailed instructions on how to set up the configuration file, please refer to the [Configuration](https://ngwpc.github.io/nwm-eval-mgr/config.html) and [FAQ](https://ngwpc.github.io/nwm-eval-mgr/faq.html) pages of the `nwm-eval-mgr` [documentation](https://ngwpc.github.io/nwm-eval-mgr/).

### Run evaluation/verification

```bash
python -m nwm_eval <path-to-config-file>
```
Example

```bash
python -m nwm_eval configs/config_hindcast.yaml
```

---

## Outputs

Typical outputs include:

- paired datasets (observations + simulations)
- evaluation metrics tables
- model performance plots

---

## Design Philosophy

- Workflow-driven (not just functions)
- Built on reusable metrics from `nwm_metrics`
- Configurable and extensible
- Focused on reproducible evaluation pipelines

