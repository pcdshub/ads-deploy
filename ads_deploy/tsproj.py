"""
`ads-deploy tsproj` is used to list .tsproj projects from a provided solution
file (.sln).
"""

import argparse
import logging
import os

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
        '--relative', action='store_true',
        help='Print paths relative to the solution'
    )

    return parser


def main(project, relative=False):
    solution_path, projects = util.get_tsprojects_from_filename(project.name)

    for project in projects:
        if relative:
            print(os.path.relpath(project, solution_path))
        else:
            print(project)
