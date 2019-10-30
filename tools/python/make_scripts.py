import sys
import pathlib
from runpy import run_path

def write_script(filename, header, script_text, *, pause=True):
    script_lines = (
        ['@echo off'] +
        [(f'echo {line}' if line else 'echo.')
         for line in header.strip().splitlines()
         ] +
        (['pause'] if pause else []) +
        ['echo on'] +
        list(script_text.splitlines())
    )

    with open(ioc_path / filename, 'wt') as f:
        print('\r\n'.join(script_lines), file=f)

    print(f'* Wrote script: {filename}')


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
project = settings.get('projects', ['Unknown'])[0]

spawn_docker = f'''
"C:/Program Files/Docker/Docker/resources/bin/docker.exe" run ^
        -v "{DeployRoot}:/ads-deploy/tools" ^
        -v "{SolutionDir}:{IocMountPath}" ^
	-e DISPLAY=host.docker.internal:0.0 ^
	-i {DockerImage} ^'''

write_script(
    'windows_run-ioc-in-docker.cmd',
    pause=True,
    header=f'''\
Your development environment Net ID is: {local_net_id}

You must fully exit TwinCAT for this IOC to work.
Please close TwinCAT now and
''',

    script_text=f'''\
{spawn_docker}
        "make -C ${{ADS_IOC_PATH}}/iocBoot/templates && cd '{ioc_path}' && make && sed -i '/^adsIoc_registerRecord.*$/a adsSetLocalAddress({local_net_id})' st.cmd && ./st.cmd; echo 'IOC exited.'; sleep 1"
pause
''')


write_script(
    'windows_run-typhon-gui.cmd',
    pause=False,
    header=f'''\
Starting Typhon...
''',

    script_text=f'''\
{spawn_docker}
	"cd '{ioc_path}' && pytmc stcmd --template-path /ads-deploy/tools/templates --template typhon_display.py --only-motor """{IocMountPath}/{project}""" > /tmp/display.py && echo 'Running Typhon...' && python /tmp/display.py"
''')
