@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo on
%RunDocker% %DockerImage% "find '%IocMountPath%' -type f -name '*.tsproj' -exec pytmc debug '{}' \;"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
