#!/bin/bash
# This script is used to run the evaluation tests for the nwm-eval-mgr project. It builds a Docker image for the project, 
# runs the tests inside a Docker container, and also runs the tests using a local virtual environment.
#
# Usage (run from the root of the nwm-eval-mgr repo):
#   ./utils/run_eval_tests.sh
#
#

set -euo pipefail

# uncomment to remove dangling images and containers to free up space if needed
# docker system prune

# build docker image for nwm_eval
docker build --build-arg APP_ROOT=/my-app --tag nwm_eval .

# run tests with docker container 
# note: the last test is commented out because it requires downloading large amounts of NWM data from GCS, which may take a few hours to complete
docker run -v $(pwd):$(pwd) -v $HOME:$HOME -w $(pwd) nwm_eval verification configs/config_hindcast.yaml
docker run -v $(pwd):$(pwd) -v $HOME:$HOME -w $(pwd) nwm_eval verification configs/config_ngencerf.yaml
docker run -v $(pwd):$(pwd) -v $HOME:$HOME -w $(pwd) nwm_eval verification configs/config_ngensim.yaml
# docker run -v $(pwd):$(pwd) -v $HOME:$HOME -w $(pwd) nwm_eval verification configs/config_nwm.yaml

# run tests with local venv
source venv/bin/activate
python -m nwm_eval configs/config_hindcast.yaml
python -m nwm_eval configs/config_ngencerf.yaml
python -m nwm_eval configs/config_ngensim.yaml
# python -m nwm_eval configs/config_nwm.yaml

echo "All tests passed successfully!"