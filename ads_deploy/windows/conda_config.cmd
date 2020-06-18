SET ADS_DEPLOY_CONDA_ENV=ads-deploy-2.6.5
SET TEMPLATE_PATH=/c/Repos/ads-ioc/iocBoot/templates

IF "%UseDocker%" == "0" (
    echo * Using ads-deploy conda environment: %ADS_DEPLOY_CONDA_ENV%
)
