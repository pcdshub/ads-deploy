CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

"C:\Program Files\Docker\Docker\resources\bin\docker.exe" run ^
	-v %DeployRoot%/python:/python ^
	-v %SolutionDir%:%IocMountPath% ^
	-i %DockerImage% ^
	"make -C ${ADS_IOC_PATH}/iocBoot/templates && find %IocMountPath%/iocBoot -type d -maxdepth 1 -name ioc* -exec make -C {} \;"

@GOTO Done

:Fail
@echo ** FAILED **
@echo Some parameters were unset! Did you click the PLC project in Visual Studio before running?

:Done
@echo Done
