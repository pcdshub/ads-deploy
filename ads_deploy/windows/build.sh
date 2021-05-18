#!/bin/bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
IOC_INSTANCE_PATH=$1
ADS_IOC_PATH=$2
IOC_NAME=$(basename $IOC_INSTANCE_PATH)

cd "$IOC_INSTANCE_PATH"

if [ ! -f Makefile ]; then
    if [ "${IOC_NAME}" != "iocBoot" ]; then
        echo "* No makefile found in $IOC_INSTANCE_PATH; skipping."
    fi
    exit 0
fi

echo "* Building $IOC_NAME"

if [ -d .pytmc_build ]; then
    echo "* Cleaning old build directory..."
    rm -rf .pytmc_build
fi

# Ensure we have access to pytmc, ads-deploy:
source "${SCRIPT_PATH}/conda_config.sh"
conda activate $ADS_DEPLOY_CONDA_ENV

# Fix the path for the Makefile, as we ignore it in the following step anyway:
sed -i -e 's#^IOC_TOP\s*=\s*C:.*\(R.*\)\s*$#IOC_TOP=/reg/g/pcds/epics/ioc/common/ads-ioc/\1#' Makefile

# Temporarily replace ADS_IOC in the Makefile to point to WINDOWS_ADS_IOC_TOP:
make IOC_TOP="${ADS_IOC_PATH}/" TEMPLATE_PATH="${ADS_IOC_PATH}/iocBoot/templates" build clean
