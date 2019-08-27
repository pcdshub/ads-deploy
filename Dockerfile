FROM pcdshub/ads-ioc:v0.0.1-1-ge039050

LABEL maintainer="K Lauer <klauer@slac.stanford.edu>"
USER root

# Install miniconda3 (adapted from conda/miniconda3-centos7)
RUN yum -y update \
    && yum -y install curl bzip2 mesa-libGL libXi \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local/ \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3.7 \
    && conda update conda \
    && conda clean --all --yes \
    && yum clean all

# --- Version settings
ENV PYTMC_VERSION      v2.0.0rc1
# --- Version settings

ADD pytmc_env.yml pytmc_env.yml

RUN pip install --upgrade pip
RUN conda config --add channels conda-forge
RUN conda install --channel conda-forge --file pytmc_env.yml

RUN pip install git+https://github.com/slaclab/pytmc.git@${PYTMC_VERSION}
RUN pip install git+https://github.com/epicsdeb/pypdb.git@4ad4016
