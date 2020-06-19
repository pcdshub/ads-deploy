"""
`ads-deploy typhos` is used to create a quick typhos screen, directly from a
TwinCAT solution (or tsproj project).
"""

import argparse
import logging

import ophyd
import pytmc
import pytmc.bin.stcmd
from pytmc.bin.db import process

import typhos
import typhos.cli

from . import util

try:
    import pcdsdevices
    import pcdsdevices.epics_motor
except ImportError:
    # TODO: pcdsdevices is a heavy import with many requirements
    pcdsdevices = None
    MOTOR_CLASS = ophyd.EpicsMotor
else:
    MOTOR_CLASS = pcdsdevices.epics_motor.BeckhoffAxis


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

    parser.add_argument(
        '--flat',
        action='store_true',
        help='Create a flat device hierarchy'
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


def pvname_to_attribute(pvname):
    name = pvname.strip(' "')
    attr = name.replace(':', '_')
    if not attr.isidentifier():
        return f'_{attr}'
    return attr


def component_from_record_pair(input_record, output_record):
    rtyp = input_record.record_type
    string = (rtyp == 'stringin' or
              (rtyp == 'waveform' and input_record.fields['FTVL'] == 'CHAR')
              )

    if output_record:
        return ophyd.Component(ophyd.EpicsSignal,
                               input_record.pvname,
                               write_pv=output_record.pvname, kind='normal',
                               string=string,
                               )
    return ophyd.Component(ophyd.EpicsSignalRO, input_record.pvname,
                           string=string,
                           kind='normal')


class Node:
    def __init__(self, prefix, parent=None, children=None):
        self.children = children or {}
        self.parent = parent
        self.pairs = []
        self.prefix = prefix
        self.device_class = None

    @property
    def size(self):
        child_size = sum(child.size for child in self.children.values())
        return len(self.pairs) + child_size

    def add(self, item, pair):
        prefix, *suffix = item
        if not suffix:
            return self.pairs.append(pair)

        if prefix not in self.children:
            self.children[prefix] = Node(prefix=self.prefix + [prefix],
                                         parent=self)
        self.children[prefix].add(suffix, pair)

    def _create_device_class(self, threshold, components):
        components = dict(components)
        for prefix, child in sorted(self.children.items(),
                                    key=lambda kv: kv[1].prefix[-1]):
            attr = pvname_to_attribute(child.prefix[-1])
            components[attr] = ophyd.Component(
                child.create_device_class(threshold=threshold,
                                          components={}),
                '',   # full PVname, no prefix combining
                # child.prefix[-1] + ':'
            )

        for input_record, output_record in self.pairs:
            attr = pvname_to_attribute(input_record.pvname)
            components[attr] = component_from_record_pair(input_record,
                                                          output_record)

        name = (pvname_to_attribute(self.prefix[-1].capitalize())
                if self.prefix else 'PLC')
        self.device_class = ophyd.device.create_device_from_components(
            name, **components
        )
        return self.device_class

    def _squash_children(self):
        def add_pairs(descendent):
            self.pairs.extend(descendent.pairs)

        for child in self.children.values():
            add_pairs(child)
            for descendent in child.walk_depth_first():
                add_pairs(descendent)
        self.children.clear()

    def create_device_class(self, threshold, components):
        if self.size < threshold:
            self._squash_children()
        return self._create_device_class(threshold, components)

    def walk_depth_first(self):
        for prefix, child in self.children.items():
            yield from child.walk_depth_first()
        yield self

    @classmethod
    def build_tree(cls, attr_to_pairs, delim=':'):
        root = cls(prefix=[])
        for attr, (input_record, output_record) in attr_to_pairs.items():
            root.add(input_record.pvname.split(delim), (input_record,
                                                        output_record))
        return root


def ophyd_device_from_plc(plc_name, plc_project, macros, *, includes=None,
                          excludes=None, flat=False):
    tmc = pytmc.parser.parse(plc_project.tmc_path)

    packages, exceptions = process(tmc, allow_errors=True,
                                   show_error_context=True)

    attr_to_pairs = {
        pvname_to_attribute(input_record.pvname): (input_record, output_record)
        for input_record, output_record in records_from_packages(packages,
                                                                 macros)
        if pvname_to_attribute(input_record.pvname)
    }

    attr_to_pairs = {
        attr: (input_record, output_record)
        for attr, (input_record, output_record) in attr_to_pairs.items()
        if util.should_filter(includes, excludes, [attr, input_record.pvname])
    }

    motors = {}
    for motor in tmc.find(pytmc.parser.Symbol_DUT_MotionStage):
        if motor.is_pointer:
            continue

        if not util.should_filter(includes, excludes, ['motor', motor.name]):
            continue

        prefix = ''.join(
            pytmc.bin.stcmd.get_name(motor, {'prefix': plc_name, 'delim': ':'})
        )

        attr = pvname_to_attribute(prefix)
        motors[attr] = ophyd.Component(MOTOR_CLASS, prefix)

    if flat:
        components = {
            attr: component_from_record_pair(input_record, output_record)
            for attr, (input_record, output_record) in attr_to_pairs.items()
        }
        device_cls = ophyd.device.create_device_from_components(
            plc_name.capitalize(), **components, **motors)
    else:
        root = Node.build_tree(attr_to_pairs)
        device_cls = root.create_device_class(threshold=50, components=motors)

    return device_cls('', name=plc_name)


def main(project, *, plcs=None, include=None, exclude=None, macro=None,
         flat=False):
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
                                               excludes=exclude,
                                               flat=flat)
            except Exception:
                logger.exception('Failed to create device for plc %s',
                                 plc_name)
                raise

        for sig in typhos.utils.get_all_signals_from_device(device):
            logger.debug("Signal: %s", sig)

        devices.append(device)

    typhos.cli.get_qapp()
    typhos.use_stylesheet()
    suite = typhos.TyphosSuite.from_devices(devices)
    return typhos.cli.launch_suite(suite)
