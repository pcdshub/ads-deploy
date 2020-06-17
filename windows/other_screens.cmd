@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

ECHO "ads-deploy typhos arguments: %UserArguments%"

IF %AdsDeployUseDocker% EQU 1 (
    %RunDocker% %DockerImage% "python -m ads_deploy typhos '%SolutionLinuxPath%' %UserArguments%"

    if %ERRORLEVEL% NEQ 0 (
        %RunDocker% %DockerImage% "python -m ads_deploy typhos --help"
        pause
    )
) ELSE (
    call python -m ads_deploy typhos "%SolutionFullPath%" %UserArguments%
    if %ERRORLEVEL% NEQ 0 (
        call python -m ads_deploy typhos --help
        pause
    )
)

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
