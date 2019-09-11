FROM pcdshub/ads-ioc:v0.0.2

LABEL maintainer="K Lauer <klauer@slac.stanford.edu>"
USER root

# Install miniconda3 (adapted from conda/miniconda3-centos7)
# and also the necessary X11 libraries for pyqt5
RUN yum -y update \
    && yum -y install curl bzip2 mesa-libGL libXi libxkbcommon-x11 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local/ \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3.7 \
    && conda update conda \
    && conda clean --all --yes \
    && yum clean all

# --- Version settings
ENV PYTMC_VERSION      fix_motionstage_pragmas
ENV ADS_IOC_VERSION    v0.0.2
# --- Version settings

ADD pytmc_env.yml pytmc_env.yml

RUN pip install --upgrade pip
RUN conda config --add channels conda-forge
RUN conda install --channel conda-forge --file pytmc_env.yml

RUN pip install git+https://github.com/klauer/pytmc.git@${PYTMC_VERSION}
RUN pip install git+https://github.com/epicsdeb/pypdb.git@4ad4016
RUN pip install git+https://github.com/slaclab/pydm@v1.7.3
RUN pip install git+https://github.com/stlehmann/pyads@3.2.0

RUN conda install typhon -c conda-forge -c pcds-tag
RUN conda install epics-base -c conda-forge

# TODO this (especially) needs cleaning
ENV ADS_IOC_ROOT /reg/g/pcds/epics/${BASE_MODULE_VERSION}/ioc/ads-ioc
ENV ADS_IOC_PATH ${ADS_IOC_ROOT}/${ADS_IOC_VERSION}
WORKDIR ${ADS_IOC_ROOT}

RUN cp -R /epics/iocs/ads-ioc/ ${ADS_IOC_PATH}
RUN ls $ADS_IOC_PATH
RUN make -C ${ADS_IOC_PATH} all

WORKDIR ${ADS_IOC_PATH}
ENTRYPOINT ["/bin/bash", "-c"]
