# Podman Support (Additive Path)

This repository maintains Docker as its primary documented and production CI path. Podman is supported as an **additional** option for local development, rootless execution, and container build/smoke verification.

Existing Docker workflows (`.github/workflows/ci-cd.yml`), Apptainer SIF pipelines, and production release tags remain untouched and active.

---

## Prerequisites

Verify that Podman is installed on your workstation:

```bash
podman version
podman info
```

For Ubuntu 24.04+ (Noble) or RHEL 8/9, Podman 4.9+ is recommended.

---

## Building with Podman

Build the image directly using the existing `Dockerfile`. Following NOAA-OWP/WRES conventions, use `--format docker` to ensure standard OCI/Docker compatibility:

```bash
podman build --format docker -t local/nwm-eval-mgr:podman-test .
```

*Note: The Dockerfile uses BuildKit syntax (`# syntax=docker/dockerfile:1.4`) and `--mount=type=cache` for pip and apt. Modern Podman (via Buildah $\ge$ 1.24) natively resolves these cache mounts locally without requiring a Docker daemon.*

---

## Smoke Verification

The application entrypoint script (`docker/run-nwm-eval-mgr.sh`) requires a subcommand (such as `verification`). When invoked with `--help` or without arguments, it prints usage information and returns exit code `1`.

### 1. Test Entrypoint & CLI Usage
```bash
podman run --rm local/nwm-eval-mgr:podman-test --help
# Expected: prints 'Usage: run-nwm-eval-mgr <command> <config_file> [stdout_file]' (exit code 1)
```

### 2. Verify Python Virtual Environment & Installed Packages
To verify that the internal Python virtual environment (`/ngen-app/nwm-eval-mgr-python`) and installed packages (`nwm_eval`, `nwm_metrics`) are healthy:
```bash
podman run --rm --entrypoint python local/nwm-eval-mgr:podman-test \
  -c "import nwm_metrics, nwm_eval; print('Packages verified successfully.')"
# Expected: prints verification message (exit code 0)
```

---

## Running Evaluation Workflows

To run an evaluation workflow locally mounting host data:

```bash
podman run --rm \
  -v "$(pwd):$(pwd):z" \
  -w "$(pwd)" \
  local/nwm-eval-mgr:podman-test \
  verification "$(pwd)/configs/config_hindcast.yaml"
```

> **SELinux Note:** On SELinux-enforcing systems (e.g., RHEL or Fedora), the `:z` (shared) or `:Z` (private) mount flag is required so the rootless container has read/write permissions to mounted host paths.

---

## CI / Automation

* **Workflow:** `.github/workflows/podman-smoke.yml`
* **Trigger:** Manual (`workflow_dispatch`)
* **Runner Environment:** Pinned to `ubuntu-24.04` (aligning with NOAA-OWP Noble baseline and Buildah cache-mount requirements).
* **Registry Policy:** By default, builds remain local to the runner. When `push_images=true` is dispatched, only `:podman-test` and `:<sha>-podman-test` tags are published to GHCR. Production aliases (`:latest`, timestamped tags) are never modified.
