@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo Running Qt designer...
pushd %SolutionDir%
IF %AdsDeployUseDocker% EQU 1 (
    %RunDocker% %DockerImage% "source activate && designer; sleep 1"
) ELSE (
    start designer
    echo It may take a while for designer to show.
    pause
)
@popd

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
