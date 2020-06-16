SET ADS_DEPLOY_CONDA_ENV=ads-deploy-2.6.5

IF "%UseDocker%" == "0" (
    echo * Using ads-deploy conda environment: %ADS_DEPLOY_CONDA_ENV%
)
