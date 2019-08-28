CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

"C:\Program Files\Docker\Docker\resources\bin\docker.exe" run ^
	-v %DeployRoot%/python:/python ^
	-v %SolutionDir%:%IocMountPath% ^
	-i %DockerImage% ^
	"cd %IocMountPath% && eval $(python /python/environment.py) && mkdir -p iocBoot 2> /dev/null; cd iocBoot && pytmc iocboot ${TSPROJ} ${ADS_IOC_PATH}/iocBoot/templates"

@REM @echo Opening up explorer to IOC path...
@REM @cd %IOCPath%
@REM @explorer .

@GOTO Done

:Fail
@echo ** FAILED **

:Done
@echo (Done)
