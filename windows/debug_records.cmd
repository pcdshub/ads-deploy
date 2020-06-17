@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

IF %AdsDeployUseDocker% EQU 1 (
    %RunDocker% %DockerImage% "find '%IocMountPath%' -type f -name '*.tsproj' -exec pytmc debug '{}' \;"
) ELSE (
    FOR /F "delims= tokens=1" %%F in ('call python -m ads_deploy tsproj "%SolutionFullPath%"') DO pytmc debug "%%F"
)

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
