@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo.
@echo %Divider%
@echo - Creating IOC boot directories and Makefiles
@CALL %~dp0\create_iocboot.cmd %1 %2 %3 %4 %5 %6 %7

@echo.
IF %AdsDeployUseDocker% EQU 1 (
    @echo %Divider%
    @echo - Attempting to build the IOC
    %RunDocker% %DockerImage% "find '%IocMountPath%/iocBoot' -type d -maxdepth 1 -name 'ioc*' -exec make -C {} \;"
) ELSE (
    bash --login -c "find '%SolutionDir:\=/%/iocBoot' -type d -maxdepth 1 -name 'ioc*' -exec bash --login %AdsDeployWindowsScripts:\=/%/build.sh '{}' '%WINDOWS_ADS_IOC_TOP:\=/%/' \;"
)

if %ERRORLEVEL% NEQ 0 (
    GOTO :Fail
)

@GOTO :eof

:Fail
@echo ** FAILED - see error messages above **
