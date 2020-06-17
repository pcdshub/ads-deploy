@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

ECHO "ads-deploy typhos arguments: %UserArguments%"

%RunDocker% %DockerImage% "python -m ads_deploy typhos '%SolutionLinuxPath%' %UserArguments%"

if %ERRORLEVEL% NEQ 0 (
    %RunDocker% %DockerImage% "python -m ads_deploy typhos '%SolutionLinuxPath%' --help"
    pause
)

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
