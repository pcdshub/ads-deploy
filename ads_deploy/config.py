"""
`ads-deploy config` is used to create initial directories and configuration
for a given TwinCAT solution (or tsproj project).
"""

import argparse
import logging

from . import util

DESCRIPTION = __doc__
logger = logging.getLogger(__name__)


def build_arg_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser()

    parser.description = DESCRIPTION
    parser.formatter_class = argparse.RawTextHelpFormatter

    parser.add_argument(
        'project', metavar="INPUT",
        type=argparse.FileType('rt', encoding='utf-8'),
        help='Path to the solution (.sln) or project (.tsproj) file'
    )

    parser.add_argument(
        '--net-id',
        action='store_true',
        help=('Configure the AMS Net ID settings in the deploy configuration. '
              'Not required unless intending to run the IOC with Docker.'),
    )

    parser.add_argument(
        '--ip',
        nargs='*',
        type=str,
        help=('IP address(es) to determine an AMS Net ID for docker-based IOC '
              'usage. Not required unless intending to run the IOC with '
              'Docker.')
    )

    return parser


def write_deploy_config(solution_path, projects, write_net_id, ip_addresses):
    with open(solution_path / "deploy_config.py", 'wt', newline='\r\n') as f:
        solution_path = solution_path.resolve()
        projects = [str(filename.relative_to(solution_path))
                    for filename in projects]
        print(f'projects = {projects!r}', file=f)
        if not write_net_id:
            return

        ip_error = None
        if not ip_addresses:
            print('local_net_id = "UNKNOWN"', file=f)
            ip_error = '\n'.join(
                ('Unable to find an IP address to match with the local NetID.',
                 'This must be set for the IOC to work.')
            )
        else:
            for index, ip_address in enumerate(ip_addresses):
                comment = '' if index == 0 else '# '
                print(f'{comment}local_net_id = "{ip_address}.1.1"', file=f)

            if len(ip_addresses) > 1:
                ip_error = '\n'.join(
                    ('Multiple IP addresses found. You may need to specify ',
                     'the correct local_net_id in deploy_config.py')
                )

        if ip_error:
            print()
            print('* NOTE *')
            print(ip_error)
            print('* NOTE *')
            print()
            print('# TODO: check local_net_id above; it should match Windows',
                  file=f)


def main(project, *, net_id=False, ip=None):
    solution_path, projects = util.get_tsprojects_from_filename(project.name)
    write_deploy_config(solution_path, projects, net_id, ip)
    print(f'Wrote deploy configuration to "{solution_path}".')
