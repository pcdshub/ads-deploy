@echo off
@SET DockerImage=pcdshub/ads-deploy:latest

@SET DeployRoot=%~dp0
@SET SolutionDir=%1
@SET SolutionFilename=%2

@SET SolutionDir=%SolutionDir:~1,-1%
@SET SolutionFilename=%SolutionFilename:~1,-1%
@SET SolutionName=%SolutionFilename:~0,-4%

@IF [%SolutionDir:~-2%]==[\\] (
    @SET SolutionDir=%SolutionDir:~0,-1%
)

@SET SolutionFullPath="%SolutionDir%%SolutionName%"
@SET IocMountPath=/reg/g/pcds/epics/ioc/%SolutionName%

@if not [%AdsDeployConfigured%] == [1] (
	@echo ----------------------------------------------------------------------
	@echo Solution directory:      %SolutionDir%
	@echo Solution name:           %SolutionName%
	@echo Solution filename:       %SolutionFilename%
	@echo Solution full path:      %SolutionFullPath%
	@echo IOC mount path:          %IocMountPath%
	@echo ----------------------------------------------------------------------
	@echo.
)

@SET ConfigSuccess=1
@IF "%SolutionDir%" == "" (
	@echo Solution directory unset!
	@SET ConfigSuccess=0
)
@IF "%SolutionFilename%" == "" (
	@echo Solution filename unset!
	@SET ConfigSuccess=0
)

@SET RunDocker=docker run ^
    -v "%DeployRoot%:/ads-deploy/tools" ^
    -v "%SolutionDir%:%IocMountPath%" ^
	-e DISPLAY=host.docker.internal:0.0 ^
    -i

@SET AdsDeployConfigured=1
