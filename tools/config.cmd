@echo off
SET DockerImage=pcdshub/ads-deploy:latest
REM The default, which can be overridden in `select_conda_or_docker.cmd`
SET AdsDeployUseDocker=1

SET DeployRoot=%~dp0%..\

SET SolutionDir=%1
SET SolutionFilename=%2
SET UserArguments=%3 %4 %5 %6 %7 %8 %9

SET SolutionDir=%SolutionDir:~1,-1%
SET SolutionFilename=%SolutionFilename:~1,-1%
SET SolutionName=%SolutionFilename:~0,-4%

IF [%SolutionDir:~-2%]==[\\] (
    SET SolutionDir=%SolutionDir:~0,-1%
)

SET "SolutionFullPath=%SolutionDir%%SolutionFilename%"
SET IocMountPath=/reg/g/pcds/epics/ioc/%SolutionName%
SET SolutionLinuxPath=/reg/g/pcds/epics/ioc/%SolutionName%/%SolutionFilename%
SET Divider=------------------------------------------------------------------------------------------------------------------------

if not [%AdsDeployConfigured%] == [1] (
	echo %Divider%
	echo Solution directory:      %SolutionDir%
	echo Solution name:           %SolutionName%
	echo Solution filename:       %SolutionFilename%
	echo Solution full path:      %SolutionFullPath%
	echo IOC mount path:          %IocMountPath%
	echo %Divider%
	echo.
)

SET ConfigSuccess=1
IF "%SolutionDir%" == "" (
	echo Solution directory unset!
	SET ConfigSuccess=0
)
IF "%SolutionFilename%" == "" (
	echo Solution filename unset!
	SET ConfigSuccess=0
)

SET RunDocker=docker run ^
    -v "%DeployRoot%:/ads-deploy" ^
    -v "%SolutionDir%:%IocMountPath%" ^
	-e PYTHONPATH=/ads-deploy ^
	-e DISPLAY=host.docker.internal:0.0 ^
    -i

CALL %DeployRoot%\tools\conda_config.cmd
CALL %DeployRoot%\tools\select_conda_or_docker.cmd

IF %AdsDeployUseDocker% EQU 1 (
    echo ** Docker mode **
) ELSE (
    echo ** Conda mode **
    call conda activate %ADS_DEPLOY_CONDA_ENV%
    IF %ERRORLEVEL% NEQ 0 (
        echo Conda not installed correctly.
        EXIT 1
    )

    set ADS_DEPLOY_CONDA_ENV

    REM The following is handy (but so slow)...
    REM echo.
    REM echo * ADS deploy version:
    REM call python -m ads_deploy --version 2>nul

)

SET AdsDeployConfigured=1
