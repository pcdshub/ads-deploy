@CALL %~dp0\build_ioc.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail
@CALL %~dp0\make_scripts.cmd %1 %2 %3 %4 %5 %6 %7

@echo Running the IOC(s)...
@pushd %SolutionDir%\iocBoot
@FORFILES /S /M windows_run-ioc-in-docker.cmd /c "cmd /c Echo running @path..."
@FORFILES /S /M windows_run-ioc-in-docker.cmd /c "cmd /c start cmd /k @path"
@popd

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
