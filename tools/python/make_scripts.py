import sys
import pathlib
from runpy import run_path

stcmd, DeployRoot, SolutionDir, IocMountPath, DockerImage = sys.argv[1:]

try:
    settings = run_path(pathlib.Path(IocMountPath) / "deploy_config.py")
except Exception as ex:
    print('ERROR: Unable to load deploy_config.py from your solution directory:')
    print(type(ex), ex)
    print('Did you run the initial configuration step?')
    settings = None


ioc_path = pathlib.Path(stcmd).parent.absolute()

local_net_id = settings.get('local_net_id', 'UNKNOWN')

script = f'''
@echo Your development environment Net ID is: {local_net_id}

@echo You must fully exit TwinCAT for this IOC to work.
@echo Please close TwinCAT now and
@pause

"C:/Program Files/Docker/Docker/resources/bin/docker.exe" run ^
        -v "{DeployRoot}:/ads-deploy" ^
        -v "{SolutionDir}:{IocMountPath}" ^
        -i {DockerImage} ^
        "make -C ${{ADS_IOC_PATH}}/iocBoot/templates && cd '{ioc_path}' && make && sed -i '/^adsIoc_registerRecord.*$/a adsSetLocalAddress({local_net_id})' st.cmd && ./st.cmd"
'''

with open(ioc_path / 'windows_run-ioc-in-docker.cmd', 'wt') as f:
    print('\r\n'.join(script.splitlines()), file=f)


project = settings.get('projects', ['Unknown'])[0]

script = f'''
@echo Starting Typhon...

"C:/Program Files/Docker/Docker/resources/bin/docker.exe" run ^
        -v "{DeployRoot}:/ads-deploy/tools" ^
        -v "{SolutionDir}:{IocMountPath}" ^
	-e DISPLAY=host.docker.internal:0.0 ^
	-i {DockerImage} ^
	"cd '{IocMountPath}' && eval $(python /ads-deploy/tools/python/environment.py) && pytmc stcmd --template-path /ads-deploy/tools/templates --template typhon_display.py --only-motor """{project}""" > /tmp/display.py && python /tmp/display.py"
'''

with open(ioc_path / 'windows_run-typhon-gui.cmd', 'wt') as f:
    print('\r\n'.join(script.splitlines()), file=f)
