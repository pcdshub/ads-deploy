@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

%RunDocker% %DockerImage% "find %IocMountPath% -type f -name '*.tsproj' -exec pytmc pragmalint '{}' \;"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
