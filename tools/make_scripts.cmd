@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo Creating windows_run-ioc-in-docker.cmd and windows_run-typhon-gui.cmd...

%RunDocker% %DockerImage% "find %IocMountPath%/iocBoot -type f -name st.cmd -exec python /ads-deploy/tools/python/make_scripts.py {} '%DeployRoot%' '%SolutionDir%' '%IocMountPath%' '%DockerImage%' \;"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
