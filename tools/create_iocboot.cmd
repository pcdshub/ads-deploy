@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

%RunDocker% %DockerImage% "cd %IocMountPath% && eval $(python /ads-deploy/tools/python/environment.py) && mkdir -p iocBoot 2> /dev/null; cd iocBoot && pytmc iocboot """${TSPROJ}""" ${ADS_IOC_PATH}/iocBoot/templates"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
