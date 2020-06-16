@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

IF "%UseDocker%" == "1" (
    %RunDocker% %DockerImage% "find '%IocMountPath%' -type f -name '*.tsproj' -exec pytmc pragmalint '{}' \;"
) ELSE (
    FOR /F "delims= tokens=1" %%F in ('call python -m ads_deploy tsproj "%SolutionFullPath%"') DO pytmc pragmalint "%%F"
)

if %ERRORLEVEL% NEQ 0 (
    @echo ** FAILED - see error messages above **
)

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED - see error messages above **
