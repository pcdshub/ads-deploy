import sys
import pathlib

stcmd, DeployRoot, SolutionDir, IocMountPath, DockerImage = sys.argv[1:]

ioc_path = pathlib.Path(stcmd).parent.absolute()

script = f'''
"C:/Program Files/Docker/Docker/resources/bin/docker.exe" run ^
        -v {DeployRoot}/python:/python ^
        -v {SolutionDir}:{IocMountPath} ^
        -i {DockerImage} ^
        "make -C ${{ADS_IOC_PATH}}/iocBoot/templates && cd {ioc_path} && make && ./st.cmd"
'''

with open(ioc_path / 'run-ioc-in-docker.cmd', 'wt') as f:
    print('\r\n'.join(script.splitlines()), file=f)
