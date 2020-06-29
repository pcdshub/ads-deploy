"""
`ads-deploy iocboot` is used to create iocBoot directories for the specified
TwinCAT solution (or tsproj project).
"""

import argparse
import getpass
import logging
import os
import pathlib
import sys

import jinja2
import pytmc

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
        '--destination',
        type=str,
        nargs='?',
        help=('iocBoot directory, under which to create per-project IOCs.  '
              'Defaults to the solution root.'
              )
    )

    parser.add_argument(
        '--ioc-template-path',
        type=str,
        nargs='?',
        help='Path to ads-ioc'
    )

    parser.add_argument(
        '--prefix', type=str, default='ioc-',
        help='IOC boot directory prefix [default: ioc-]'
    )

    parser.add_argument(
        '--makefile-name', type=str,
        default='Makefile.ioc',
        help='Jinja2 template for the IOC Makefile [default: Makefile.ioc]',
    )

    parser.add_argument(
        '--overwrite', action='store_true',
        help='Overwrite existing files'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry-run only - do not write files'
    )

    parser.add_argument(
        '--plcs',
        type=str,
        action='append',
        help='Specify one or more PLC names to generate'
    )

    parser.add_argument(
        '--macro',
        type=str,
        nargs='*',
        help='Specify an additional macro for the template (VAR=VALUE)'
    )

    return parser


def create_iocboot_for_plc(tsproj_project, plc, *, ioc_name, makefile_path,
                           destination, overwrite=False, dry_run=False,
                           macros=None):
    """
    Create iocBoot Makefile for a single PLC.

    Parameters
    ----------
    tsproj_project : pathlib.Path
        .tsproj project path

    plc : pytmc.TcItem
        The parsed PLC project from pytmc.

    ioc_name : str
        The IOC name.

    makefile_path : pathlib.Path
        Path to the template Makefile (i.e.,
        ``ads-ioc/iocBoot/templates/Makefile.ioc``)

    destination : pathlib.Path
        Destination directory for the new makefile.

    overwrite : bool, optional
        Overwrite the existing Makefile.

    dry_run : bool, optional
        Print to standard output what would happen instead of writing to files.

    macros : dict, optional
        Additional macros for the template interpolation.
    """
    ioc_template_path = makefile_path.parent
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(ioc_template_path)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    makefile_template = jinja_env.get_template(makefile_path.name)

    ioc_template_path = pathlib.Path(ioc_template_path)

    if not dry_run:
        os.makedirs(destination, exist_ok=True)
    output_makefile = destination / 'Makefile'

    plc_path = pathlib.Path(plc.filename)

    def relative_path(path, start):
        path = os.path.relpath(path, start)
        return path if sys.platform != 'win32' else path.replace(os.sep, '/')

    template_args = dict(
        project_name=tsproj_project.stem,
        plc_name=plc.name,
        tsproj_path=relative_path(tsproj_project, destination),
        plc_path=relative_path(plc_path, destination),
        project_path=relative_path(tsproj_project.parent, destination),
        template_path=ioc_template_path,
        plcproj=relative_path(plc.filename, destination),
        plc_ams_id=plc.ams_id,
        plc_ip=plc.target_ip,
        plc_ads_port=plc.port,
        user=getpass.getuser(),
        **(macros or {})
    )

    rendered = makefile_template.render(**template_args)

    if dry_run:
        print()
        print('--- dry run ---')
        print(output_makefile)
        print('--- dry run ---')

        print(rendered)

        if output_makefile.exists():
            print('** Dry-run: would overwrite **'
                  if overwrite else '!! Dry-run: would fail: already exists')
            print()
    else:
        if output_makefile.exists() and not overwrite:
            raise RuntimeError('Must specify --overwrite to write over'
                               ' existing Makefiles (or delete and try again)')
        with open(output_makefile, 'wt') as f:
            print(rendered, file=f)


def get_template_paths(ioc_template_path, makefile_name='Makefile.ioc'):
    """
    Get the IOC template path and template Makefile path from user parameters.

    Parameters
    ----------
    ioc_template_path : pathlib.Path
        The IOC template path, or None.  If None, this can be inferred from
        environment settings.

    makefile_name : str, optional
        The makefile name.

    Returns
    -------
    ioc_template_path : pathlib.Path
        The corrected/found IOC template path.

    makefile_path : pathlib.Path
        The corrected/found Makefile template path.
    """
    if not ioc_template_path:
        ioc_template_path = util.get_latest_ads_ioc()

    ioc_template_path = pathlib.Path(ioc_template_path)

    if (ioc_template_path / 'iocBoot' / 'templates').exists():
        ioc_template_path = ioc_template_path / 'iocBoot' / 'templates'

    if not (ioc_template_path / makefile_name).exists():
        raise RuntimeError(f'Makefile {makefile_name} not found in '
                           f'{ioc_template_path}')

    makefile_path = ioc_template_path / makefile_name
    return ioc_template_path, makefile_path


def main(project, ioc_template_path, *, destination=None, prefix='ioc-',
         overwrite=False, makefile_name='Makefile.ioc', dry_run=False,
         plcs=None, macro=None):
    solution_path, projects = util.get_tsprojects_from_filename(project.name)

    if not destination:
        destination = solution_path / 'iocBoot'
        destination.mkdir(parents=True, exist_ok=True)

    ioc_template_path, makefile_path = get_template_paths(ioc_template_path,
                                                          makefile_name)
    iocboot_settings = dict(
        makefile_path=makefile_path,
        overwrite=overwrite,
        dry_run=dry_run,
        macros=util.split_macros(macro or []),
    )

    destination = pathlib.Path(destination)

    logger.debug('Solution path: %s', solution_path)
    logger.debug('IOC boot path: %s', destination)
    logger.debug('Template path: %s', ioc_template_path)
    logger.debug('Makefile path: %s', makefile_path)
    logger.debug('Settings     : %s', iocboot_settings)

    for tsproj_project in projects:
        parsed_tsproj = pytmc.parser.parse(tsproj_project)
        for plc_name, plc_project in parsed_tsproj.plcs_by_name.items():
            logger.debug('Project: %s PLC: %s', tsproj_project, plc_name)

            if plcs and plc_name not in plcs:
                logger.debug('Skipping; not in valid list: %s', plcs)
                continue

            ioc_name = plc_name.replace('_', '-').replace(' ', '_')
            ioc_path = destination / f'{prefix}{ioc_name}'
            logger.debug('PLC: %s IOC name: %s IOC path: %s', plc_name,
                         ioc_name, ioc_path)

            try:
                create_iocboot_for_plc(tsproj_project, plc_project,
                                       ioc_name=ioc_name, destination=ioc_path,
                                       **iocboot_settings)
            except RuntimeError as ex:
                logger.error('%s', ex)
