SET ADS_DEPLOY_CONDA_ENV=ads-deploy-2.9.1
SET WINDOWS_ADS_IOC_TOP=c:/Repos/ads-ioc/R0.6.0

IF "%UseDocker%" == "0" (
    echo * Using ads-deploy conda environment: %ADS_DEPLOY_CONDA_ENV%
)
