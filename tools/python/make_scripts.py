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

local_net_id = getattr(settings, 'local_net_id', 'UNKNOWN')

script = f'''
@echo Your development environment Net ID is: {local_net_id}

@echo You must fully exit TwinCAT for this IOC to work.
@echo Please close TwinCAT now and
@pause

"C:/Program Files/Docker/Docker/resources/bin/docker.exe" run ^
        -v {DeployRoot}/python:/python ^
        -v {SolutionDir}:{IocMountPath} ^
        -i {DockerImage} ^
        "make -C ${{ADS_IOC_PATH}}/iocBoot/templates && cd {ioc_path} && make && ./st.cmd"
'''

with open(ioc_path / 'run-ioc-in-docker.cmd', 'wt') as f:
    print('\r\n'.join(script.splitlines()), file=f)
