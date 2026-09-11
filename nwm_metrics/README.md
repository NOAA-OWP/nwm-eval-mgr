# nwm_metrics

Core statistical metrics and evaluation functions for National Water Model (NWM) and NextGen applications.

This package provides reusable, lightweight metric implementations used across calibration, evaluation, and verification workflows.

---

## Purpose

`nwm_metrics` focuses on **computing metrics only**.

It does not handle:
- data retrieval
- data pairing
- plotting
- workflow orchestration

Those responsibilities are handled by `nwm_eval`.

---

## Features

- Standard hydrologic performance metrics (e.g., NSE, KGE, PBIAS, RMSE, CORR)
- Flow duration curve (FDC) based metrics (e.g., HSEG_FDC, MSEG_FDC, LSEG_FDC)
- Categorical metrics (e.g., FAR, POD, CSI, FBIAS)
- Event-based metrics (e.g., PKBIAS, PKTE, EVBIAS)

---

## Installation

### Quick Install (Recommended)
Install directly from GitHub (no cloning required).

```bash
pip install "git+https://github.com/NGWPC/nwm-eval-mgr.git@development#subdirectory=nwm_metrics"
```

### Development install

```bash
pip install -e .
```

---

## Example Usage

```python
from nwm_metrics import metric_functions as mf

kge = mf.kge(observed_flow, simulated_flow)
nse = mf.nse(observed_flow, simulated_flow)
rmse = mf.rmse(observed_flow, simulated_flow)
```

---

## Used By

- `nwm_eval`
- calibration workflows
- verification workflows
- regionalization workflows

---

## Design Philosophy

- Minimal dependencies
- Fast execution
- Reusable across multiple applications
- No workflow or I/O logic