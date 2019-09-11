@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@set IPAddresses=
@for /f "usebackq tokens=2 delims=:" %%f in (`ipconfig ^| findstr /c:"IPv4 Address"`) do (
    call set IPAddresses=%%IPAddresses%%%%f
)

%RunDocker% %DockerImage% "python /ads-deploy/tools/python/find_tsproj.py '/reg/g/pcds/epics/ioc/%SolutionName%/%SolutionFilename%' %IPAddresses%"

@echo Opening the deploy configuration script in notepad.
@echo Close notepad when you have updated the settings to continue...
@cd %IOCPath%
@notepad deploy_config.py

@echo.
@echo ---------------------------------------------------
@echo - Creating IOC boot directories and Makefiles
@CALL %~dp0\create_iocboot.cmd %1 %2 %3 %4 %5 %6 %7

@echo.
@echo ---------------------------------------------------
@echo - Attempting to build the IOC
@CALL %~dp0\build_ioc.cmd %1 %2 %3 %4 %5 %6 %7

@echo.
@echo ---------------------------------------------------
@echo - Creating IOC boot scripts
@CALL %~dp0\make_scripts.cmd %1 %2 %3 %4 %5 %6 %7

@GOTO :eof

:Fail
@echo ** FAILED - see error messages above **
