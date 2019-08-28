CALL %~dp0\config.cmd %1 %2 %3 %4 %5 %6 %7
@IF [%ConfigSuccess%] == [0] GOTO Fail

@echo Creating run-ioc-in-docker.cmd script...

"C:\Program Files\Docker\Docker\resources\bin\docker.exe" run ^
	-v %DeployRoot%/python:/python ^
	-v %SolutionDir%:%IocMountPath% ^
	-i %DockerImage% ^
	"find %IocMountPath%/iocBoot -type f -name st.cmd -exec python /python/make_scripts.py {} '%DeployRoot%' '%SolutionDir%' '%IocMountPath%' '%DockerImage%' \;"

@echo Running the IOC(s)...
@pushd %SolutionDir%\iocBoot
@FORFILES /S /M run-ioc-in-docker.cmd /c "cmd /c Echo running @path..."
@FORFILES /S /M run-ioc-in-docker.cmd /c "cmd /c start cmd /k @path"
@popd

@GOTO Done

:Fail
@echo ** FAILED **

:Done
@echo Done
