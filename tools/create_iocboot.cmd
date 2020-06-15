@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

%RunDocker% %DockerImage% "cd '%IocMountPath%' && mkdir -p iocBoot 2> /dev/null && python -m ads_deploy iocboot --destination iocBoot '%SolutionLinuxPath%'"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
