"""
`ads-deploy caproto` is a quick utility to create a mock caproto IOC based on
a TwinCAT solution (or tsproj project).
"""

import argparse
import logging
import threading
import time

import pytmc
from caproto.server import PVGroup, pvproperty
from caproto.server import run as caproto_run
from caproto.server import template_arg_parser

from . import typhos_gui, util

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


def create_ioc_from_records(record_pairs, *, class_name, default_values=None,
                            base_class=None):
    '''
    Create an mock-record caproto IOC from a PLC project.

    Parameters
    ----------
    record_pairs : list of (input_record, output_record)
        Where each is :class:`pytmc.record.EPICSRecord` or None.

    default_values : dict, optional
        A mapping of record_type to default value

    class_name : str, optional
        Class name for the generated class

    base_class : class, optional
        Base for the IOC, defaults to PVGroup
    '''
    class_dict = {}

    if default_values is None:
        default_values = {
            'ai': 0.0,
            'ao': 0.0,
            'bi': 0,
            'bo': 0,
            'calc': 0,
            'longin': 0,
            'longout': 0,
            'stringin': "",
            'stringout': "",
            'mbbi': 0,
            'mbbo': 0,
            'waveform': {
                'CHAR': 'unset',
                'SHORT': [0],
                'LONG': [0],
                'FLOAT': [0.],
                'DOUBLE': [0.],
            }
        }

    async def startup_hook(group, instance, async_lib):
        '''
        A startup hook which writes all field defaults
        '''
        for attr, fields in group.startup_fields.items():
            prop = getattr(group, attr)
            for field_name, value in fields.items():
                field = prop.get_field(field_name)
                try:
                    await field.write(value)
                except Exception as ex:
                    logger.warning(
                        'Failed to set initial value for: %s.%s => %s (%s)',
                        attr, field_name, value, ex
                    )

    # Fields to write during the startup hook
    startup_fields = {}

    class_dict['_startup_hook_' + class_name] = pvproperty(
        name='_startup_hook_' + class_name,
        value=0,
        startup=startup_hook,
    )

    def create_pvproperty(attr, record):
        startup_fields[attr] = {}
        default_value = default_values.get(record.record_type, 0)
        if record.record_type == 'waveform':
            ftvl = record.fields.get('FTVL', 'SHORT')
            nelm = int(record.fields.get('NELM', 1))
            default_value = default_value[ftvl]
            if ftvl != 'CHAR':
                default_value = default_value * nelm

        if 'VAL' in record.fields:
            value = type(default_value)(record.fields['VAL'])
        else:
            value = default_value

        prop = pvproperty(
            name=record.pvname,
            value=value,
            record=record.record_type,
        )

        for field_name, value in record.fields.items():
            if field_name != 'VAL':
                startup_fields[attr][field_name] = value

        for alias_idx, alias in enumerate(record.aliases):
            logger.debug('TODO - aliases: %s %s', record, alias)

        class_dict[attr] = prop
        return prop

    for input_record, output_record in record_pairs:
        output_prop = None
        if output_record:
            output_attr = typhos_gui.pvname_to_attribute(output_record.pvname)
            if output_attr:
                output_prop = create_pvproperty(output_attr, output_record)

        input_attr = typhos_gui.pvname_to_attribute(input_record.pvname)
        if not input_attr:
            continue

        _ = create_pvproperty(input_attr, input_record)
        if output_prop:
            @output_prop.putter
            async def output_putter(self, instance, value,
                                    input_attr=input_attr):
                input_prop = getattr(self, input_attr)
                await input_prop.write(value)

    if base_class is None:
        base_class = (PVGroup, )

    ioc_class = type(class_name, base_class, class_dict)
    ioc_class.startup_fields = startup_fields
    return ioc_class


def caproto_ioc_from_plc(plc_name, plc_project, macros, *, includes=None,
                         excludes=None):
    tmc = pytmc.parser.parse(plc_project.tmc_path)
    packages, exceptions = typhos_gui.process(
        tmc, allow_errors=True, show_error_context=True)
    record_pairs = [
        pair for pair in typhos_gui.records_from_packages(packages, macros)
        if util.should_filter(includes, excludes, [pair[0].pvname])
    ]
    return create_ioc_from_records(record_pairs, class_name=plc_name)


def main(project, *, plcs=None, include=None, exclude=None, macro=None):
    macros = util.split_macros(macro or [])
    include = include or []
    exclude = exclude or []
    solution_path, projects = util.get_tsprojects_from_filename(project.name)

    ioc_classes = []
    for tsproj_project in projects:
        parsed_tsproj = pytmc.parser.parse(tsproj_project)
        for plc_name, plc_project in parsed_tsproj.plcs_by_name.items():
            logger.debug('Project: %s PLC: %s', tsproj_project, plc_name)

            if plcs and plc_name not in plcs:
                logger.debug('Skipping; not in valid list: %s', plcs)
                continue

            try:
                ioc = caproto_ioc_from_plc(
                    plc_name, plc_project, macros,
                    includes=include, excludes=exclude)
            except Exception:
                logger.exception('Failed to create IOC for plc %s',
                                 plc_name)
            else:
                ioc_classes.append(ioc)

    parser, split_args = template_arg_parser(
        desc='Auto-generated mock PLC IOC',
        default_prefix='',
        argv=['--list-pvs'],
        macros={},
        supported_async_libs=['asyncio']
    )

    def start_ioc(ioc_class):
        import asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())
        ioc_options, run_options = split_args(
            parser.parse_args(['--list-pvs']))
        ioc = ioc_class(**ioc_options)
        caproto_run(ioc.pvdb, **run_options)

    # if len(ioc_classes) == 1:
    #   start_ioc(ioc_classes[0])
    # else:
    threads = []
    for ioc_class in ioc_classes:
        thread = threading.Thread(target=start_ioc,
                                  kwargs=dict(ioc_class=ioc_class),
                                  daemon=True)
        thread.start()
        threads.append(thread)

    try:
        while any(thread.is_alive() for thread in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        ...
