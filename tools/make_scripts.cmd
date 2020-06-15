@CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo Creating windows_run-ioc-in-docker.cmd and windows_run-typhos-gui.cmd...

%RunDocker% %DockerImage% "find '%IocMountPath%/iocBoot/' -maxdepth 1 -type d ! -path '%IocMountPath%/iocBoot/' -exec python /ads-deploy/tools/python/make_scripts.py {} '%DeployRoot%' '%SolutionDir%' '%SolutionFilename%' '%IocMountPath%' '%DockerImage%' \;"

@echo Done
@GOTO :eof

:Fail
@echo ** FAILED **
