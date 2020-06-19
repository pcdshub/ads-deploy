SET ADS_DEPLOY_CONDA_ENV=ads-deploy-2.6.5
SET WINDOWS_ADS_IOC_TOP=/c/Repos/ads-ioc/

REM Note: the following is used to fix the path in the ads-ioc Makefile
SET TEMPLATE_PATH=%WINDOWS_ADS_IOC_TOP%iocBoot/templates

IF "%UseDocker%" == "0" (
    echo * Using ads-deploy conda environment: %ADS_DEPLOY_CONDA_ENV%
)
