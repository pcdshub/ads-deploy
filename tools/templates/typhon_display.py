import glob
import re

import typhon

from ophyd import Device, EpicsMotor, EpicsSignal, Component as Cpt
from qtpy.QtWidgets import QApplication


RECORD_RE = re.compile('^record\((.*),(.*)\).*$')


def components_from_db(fn):
    with open(fn, 'rt') as f:
        db_text = f.read()

    components = {}
    for line in db_text.splitlines():
        if line.startswith('record') and '$' not in line:
            m = RECORD_RE.match(line)
            if m:
                rtyp, name = m.groups()

                name = name.strip(' "')
                attr = name.split(':')[-1] if ':' in name else name
                attr = attr.replace(' ', '_')
                components[attr] = Cpt(EpicsSignal, name, kind='normal')
                print(f'Adding component {attr} ({name})')
    return components


class PLCDevice(Device):
    # Hack in some additional signals (normally, this would not be recommended...)
    _dev_namespace = locals()
    for dbfn in glob.glob("*.db"):
        cpts = components_from_db(dbfn)
        _dev_namespace.update(cpts)
# TODO: replace this with make_device_from_components()

device = PLCDevice('', name='{{name}}')

app = QApplication([])
# typhon.use_stylesheet()
suite = typhon.TyphonSuite()

{% for motor in symbols.Symbol_FB_MotionStage | sort(attribute='nc_axis.axis_number') %}
axis_{{motor.nc_axis.axis_number}} = EpicsMotor("{{motor|epics_prefix}}{{motor|epics_suffix}}", name='{{motor.name}}')
suite.add_device(axis_{{motor.nc_axis.axis_number}}, category='Motors')
{% endfor %}

suite.add_device(device)

suite.show()
app.exec_()
