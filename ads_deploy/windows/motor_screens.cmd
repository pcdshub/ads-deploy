@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

IF %AdsDeployUseDocker% EQU 1 (
    %RunDocker% %DockerImage% "python -m ads_deploy typhos '%SolutionLinuxPath%' --include motor"
) ELSE (
    call python -m ads_deploy typhos "%SolutionFullPath%" --include motor
)

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
