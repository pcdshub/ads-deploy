@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

START CMD /K %RunDocker% ^
	-e DISPLAY=host.docker.internal:0.0 ^
	-t %DockerImage% ^
	"cd %IocMountPath% && eval $(python /ads-deploy/tools/python/environment.py) && pytmc stcmd --template-path /ads-deploy/tools/templates --template typhon_display.py --only-motor """${TSPROJ}""" > /tmp/display.py && python /tmp/display.py"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
