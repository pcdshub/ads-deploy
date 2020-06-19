@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

IF %AdsDeployUseDocker% EQU 1 (
    %RunDocker% %DockerImage% "cd '%IocMountPath%' && mkdir -p iocBoot 2> /dev/null && python -m ads_deploy iocboot --destination iocBoot '%SolutionLinuxPath%'"
) ELSE (
    IF NOT EXIST "%SolutionDir%\iocBoot" (
        echo Creating the top-level IOC boot directory.
        mkdir "%SolutionDir%\iocBoot"
    )
    python -m ads_deploy iocboot --destination "%SolutionDir%\iocBoot" "%SolutionFullPath%"
)


@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
