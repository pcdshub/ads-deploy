import pathlib
import sys

from runpy import run_path

try:
    settings = run_path("deploy_config.py")
except Exception as ex:
    print('Unable to load deploy_config.py from your solution directory:')
    print(type(ex), ex)
    print('Did you run the initial configuration step?')
    sys.exit(1)

for project in settings['projects']:
    print('export TSPROJ="{}"'.format(pathlib.Path(project).absolute()))
    break
