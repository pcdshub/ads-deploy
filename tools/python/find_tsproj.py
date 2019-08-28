# vi: sw=4 ts=4 sts=4 expandtab
import pathlib
import re
import sys

project_re = re.compile(
    r"^Project.*?=\s*\"(.*?)\",\s*\"(.*?)\"\s*,\s*(.*?)\"\s*$",
    re.MULTILINE
    )

solution_fn = sys.argv[1]
solution_path = pathlib.Path(solution_fn).parent

with open(solution_fn, 'rt') as f:
    solution_text = f.read()


projects = [match[1].replace('\\', '/')
            for match in project_re.findall(solution_text)]
print('Found projects:\n    ', '\n    '.join(projects), file=sys.stderr)

with open(solution_path / "deploy_config.py", 'wt') as f:
    print(f'projects = {projects!r}', file=f)
