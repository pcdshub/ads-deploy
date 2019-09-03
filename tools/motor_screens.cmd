CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

START CMD /K docker run ^
 	-v %ProjectDir%:/reg/g/pcds/epics/ioc/%ProjectFileName% ^
	-v %DeployRoot%/python:/python ^
	-e DISPLAY=host.docker.internal:0.0 ^
 	-i %DockerImage% ^
 	"python /python/display.py"


REM pytmc stcmd --template-path /tmp --template motor_list --plc %SelectedItem% %ProjectFileName%"

@REM echo Opening up explorer to IOC path...
@REM cd %IOCPath%
@REM @explorer .

@GOTO Done

:Fail
@echo ** FAILED **

:Done
@echo Done
