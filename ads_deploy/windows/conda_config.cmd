SET ADS_DEPLOY_CONDA_ENV=ads-deploy-2.6.5
SET WINDOWS_ADS_IOC_TOP=c:/Repos/ads-ioc/R0.2.4

IF "%UseDocker%" == "0" (
    echo * Using ads-deploy conda environment: %ADS_DEPLOY_CONDA_ENV%
)
