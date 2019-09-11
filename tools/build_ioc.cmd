@CALL %~dp0\make_scripts.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

%RunDocker% %DockerImage% "find '%IocMountPath%/iocBoot' -type d -maxdepth 1 -name 'ioc*' -exec make PYTMC_ARGS=--debug -C {} \;"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
