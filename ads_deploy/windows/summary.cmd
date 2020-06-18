@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo on
IF %AdsDeployUseDocker% EQU 1 (
    @%RunDocker% %DockerImage% "pytmc summary --all --code --markdown '%SolutionLinuxPath%'"  > %SolutionName%.summary.txt
) ELSE (
    call pytmc summary --all --code --markdown "%SolutionFullPath%" > %SolutionName%.summary.txt
)

IF EXIST %SolutionName%.summary.txt (
    start /max %SolutionName%.summary.txt
) ELSE (
    echo Project summary not generated! Check for errors above.
)

@GOTO :eof

:Fail
@echo ** FAILED **
