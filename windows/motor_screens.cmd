@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

%RunDocker% %DockerImage% "python -m ads_deploy typhos '%SolutionLinuxPath%' --include motor"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
