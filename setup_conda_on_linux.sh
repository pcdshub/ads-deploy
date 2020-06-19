#!/bin/bash

echo "* Checking conda is installed..."
if ! command -v conda; then
    echo "!! Conda not found.  Check your environment or install conda 3.7 from:"
    echo "https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

conda deactivate

. ads_deploy/windows/conda_config.sh

echo ""
echo "* Creating the environment $ADS_DEPLOY_CONDA_ENV..."

conda create -y --name $ADS_DEPLOY_CONDA_ENV --override-channels --channel conda-forge --channel defaults --file conda_env_base.yml

if [ $? -ne 0 ]; then
    echo "Failed to create the ads-deploy conda environment."
    exit 1
fi

echo ""
echo "* Changing to the new conda environment..."
conda activate $ADS_DEPLOY_CONDA_ENV

echo.
echo * Installing ads-deploy with pip...
pip install -e .

if [ $? -ne 0 ]; then
    echo "Failed to install ads-deploy with pip."
    exit 1
fi

echo ""
echo "* Checking the ads-deploy command-line tool..."
ads-deploy --help

if [ $? -ne 0 ]; then
    echo "Failed to verify ads-deploy."
    exit 1
fi

echo "Success."
