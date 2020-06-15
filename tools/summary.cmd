@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo on
@%RunDocker% %DockerImage% "pytmc summary --all --code --markdown '%SolutionLinuxPath%'"  > %SolutionName%.summary.txt && notepad %SolutionName%.summary.txt

@GOTO :eof

:Fail
@echo ** FAILED **
