"""
`ads-deploy typhos` is used to create a quick typhos screen, directly from a
TwinCAT solution (or tsproj project).
"""

import argparse
import logging

import ophyd
import pytmc
from pytmc.bin.db import process

import typhos
import typhos.cli

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
        '--exclude',
        type=str,
        nargs='*',
        help='Exclude signals by name',
    )

    parser.add_argument(
        '--include',
        type=str,
        nargs='*',
        help='Include signals by name',
    )

    parser.add_argument(
        '--macro',
        type=str,
        nargs='*',
        help='Specify an additional macro for the template (VAR=VALUE)'
    )

    parser.add_argument(
        '--plcs',
        type=str,
        action='append',
        help='Specify one or more PLC names to generate'
    )

    return parser


def records_from_packages(packages, macros):
    for package in sorted(packages, key=lambda pkg: pkg.pvname):
        try:
            package.pvname = util.expand_macros(package.pvname, macros)
        except ValueError:
            logger.exception('Macro missing for: %s %s',
                             package.tcname, package.pvname)
            continue

        pkg_records = package.records
        try:
            input_record, output_record = pkg_records
        except ValueError:
            input_record, output_record = pkg_records[0], None

        yield input_record, output_record


def record_to_attribute(record):
    name = record.pvname.strip(' "')
    attr = name.replace(':', '_')
    if not attr.isidentifier():
        logger.warning('Bad attr name; skipping: %s %s', name, attr)
        return
    return attr


def components_from_records(records):
    for input_record, output_record in records:
        attr = record_to_attribute(input_record)
        if not attr:
            continue

        if output_record:
            component = ophyd.Component(
                ophyd.EpicsSignal, input_record.pvname,
                write_pv=output_record.pvname, kind='normal')
        else:
            component = ophyd.Component(
                ophyd.EpicsSignalRO, input_record.pvname, kind='normal')

        yield attr, component


def ophyd_device_from_plc(plc_name, plc_project, macros, *, includes=None,
                          excludes=None):
    tmc = pytmc.parser.parse(plc_project.tmc_path)

    packages, exceptions = process(tmc, allow_errors=True,
                                   show_error_context=True)

    records = records_from_packages(packages, macros)
    components = {
        attr: cpt for attr, cpt in components_from_records(records)
        if util.should_filter(includes, excludes, [attr, cpt.suffix])
    }
    device_cls = ophyd.device.create_device_from_components(
        plc_name.capitalize(), **components)

    return device_cls('', name=plc_name)


def main(project, *, plcs=None, include=None, exclude=None, macro=None):
    macros = util.split_macros(macro or [])
    include = include or []
    exclude = exclude or []

    solution_path, projects = util.get_tsprojects_from_filename(project.name)

    devices = []
    for tsproj_project in projects:
        parsed_tsproj = pytmc.parser.parse(tsproj_project)
        for plc_name, plc_project in parsed_tsproj.plcs_by_name.items():
            logger.debug('Project: %s PLC: %s', tsproj_project, plc_name)

            if plcs and plc_name not in plcs:
                logger.debug('Skipping; not in valid list: %s', plcs)
                continue

            try:
                device = ophyd_device_from_plc(plc_name, plc_project, macros,
                                               includes=include,
                                               excludes=exclude)
            except Exception:
                logger.exception('Failed to create device for plc %s',
                                 plc_name)
        devices.append(device)

    typhos.cli.get_qapp()
    typhos.use_stylesheet()
    suite = typhos.TyphosSuite.from_devices(devices)
    return typhos.cli.launch_suite(suite)
