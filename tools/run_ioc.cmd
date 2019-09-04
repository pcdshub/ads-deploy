@CALL %~dp0\build_ioc.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo Creating run-ioc-in-docker.cmd script...

%RunDocker% %DockerImage% "find %IocMountPath%/iocBoot -type f -name st.cmd -exec python /ads-deploy/tools/python/make_scripts.py {} '%DeployRoot%' '%SolutionDir%' '%IocMountPath%' '%DockerImage%' \;"

@echo Running the IOC(s)...
@pushd %SolutionDir%\iocBoot
@FORFILES /S /M run-ioc-in-docker.cmd /c "cmd /c Echo running @path..."
@FORFILES /S /M run-ioc-in-docker.cmd /c "cmd /c start cmd /k @path"
@popd

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
