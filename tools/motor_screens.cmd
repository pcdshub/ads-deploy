@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

START CMD /K %RunDocker% ^
	-e DISPLAY=host.docker.internal:0.0 ^
	-t %DockerImage% ^
	"echo test; python /ads-deploy/tools/python/display.py"

REM pytmc stcmd --template-path /tmp --template motor_list --plc %SelectedItem% %ProjectFileName%"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
