@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

%RunDocker% %DockerImage% "make -C ${ADS_IOC_PATH}/iocBoot/templates && find %IocMountPath%/iocBoot -type d -maxdepth 1 -name 'ioc*' -exec make -C {} \;"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
