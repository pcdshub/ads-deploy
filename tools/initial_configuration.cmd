CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

"C:\Program Files\Docker\Docker\resources\bin\docker.exe" run ^
	-v %DeployRoot%/python:/python ^
	-v %SolutionDir%:%IocMountPath% ^
	-i %DockerImage% ^
	"python /python/find_tsproj.py '/reg/g/pcds/epics/ioc/%SolutionName%/%SolutionFilename%'"

@echo Opening the deploy configuration script...
@cd %IOCPath%
@explorer deploy_config.py

@GOTO Done

:Fail
@echo ** FAILED - see error messages above **

:Done
@echo Done
