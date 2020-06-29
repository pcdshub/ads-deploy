@ECHO OFF

SETLOCAL UseDocker=0

COLOR
echo * Checking conda is installed...
call conda --version

IF %ERRORLEVEL% NEQ 0 (
    echo !! Conda not installed correctly.  Please install conda 3.7 from:
    echo https://docs.conda.io/en/latest/miniconda.html#windows-installers
    GOTO :Failed
)

call conda deactivate

REM Source conda configuration env
CALL %~dp0\ads_deploy\windows\conda_config.cmd

echo.
echo * Creating the environment %ADS_DEPLOY_CONDA_ENV%...
call conda create -y --name %ADS_DEPLOY_CONDA_ENV% --override-channels --channel conda-forge --channel defaults --file conda_env_base.yml

IF %ERRORLEVEL% NEQ 0 (
    setlocal FAIL_REASON=Failed to create the ads-deploy conda environment.
    GOTO :ConfigureFailure
)

call conda install -y --name %ADS_DEPLOY_CONDA_ENV% --override-channels --channel conda-forge --channel defaults --file conda_env_windows_extras.yml

echo.
echo * Changing to the new conda environment...
call conda activate %ADS_DEPLOY_CONDA_ENV%

echo.
echo * Installing ads-deploy with pip...
call pip install -e .

IF %ERRORLEVEL% NEQ 0 (
    setlocal FAIL_REASON=Failed to install ads-deploy with pip
    GOTO :ConfigureFailure
)
echo.
echo * Checking the ads-deploy command-line tool...
ads-deploy --help

IF %ERRORLEVEL% NEQ 0 (
    setlocal FAIL_REASON=Failed to verify ads-deploy
    GOTO :ConfigureFailure
)

echo.
echo * Enabling conda in git-bash...
bash --login -c 'conda init bash'

IF %ERRORLEVEL% NEQ 0 (
    setlocal FAIL_REASON=Failed to configure git-bash
    GOTO :ConfigureFailure
)

bash -c "git clone https://github.com/pcdshub/ads-ioc/ '%WINDOWS_ADS_IOC_TOP%'/master || (cd '%WINDOWS_ADS_IOC_TOP%'/master && git pull origin master)"
bash -c "git clone --single-branch --branch R0.2.4 '%WINDOWS_ADS_IOC_TOP%'/master '%WINDOWS_ADS_IOC_TOP%'/R0.2.4"

REM NOTE: bash -c "mkdir -p /reg/g/pcds/epics/ioc/common/ads-ioc"
REM these paths are possible, but eventually are broken by how make mangles
REM paths during the build phase.

:Success
echo.
echo Success.

GOTO :Done

:ConfigureFailure
COLOR CF
echo.
echo.
echo !! %FAIL_REASON%
echo !! Failed to configure conda environment.
echo Visual Studio integration will _not_ work.
echo (type `color` to reset the terminal color)

:Done
