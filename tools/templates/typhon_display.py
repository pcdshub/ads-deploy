import glob
import re

import ophyd
import typhon

from ophyd import EpicsMotor, EpicsSignal, EpicsSignalRO, Component as Cpt
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
                cls = EpicsSignalRO if name.endswith('_RBV') else EpicsSignal
                components[attr] = Cpt(cls, name, kind='normal')
                print(f'Adding component {cls} {attr} ({name})')
    return components


def create_device_from_components(name, *, docstring=None,
                                  base_class=ophyd.Device, class_kwargs=None,
                                  **components):
    '''
    Factory function to make a Device from Components

    (Borrowed / simplified from ophyd, as we're still on an older version)

    Parameters
    ----------
    name : str
        Class name to create
    docstring : str, optional
        Docstring to attach to the class
    base_class : Device or sub-class, optional
        Class to inherit from, defaults to Device
    **components : dict
        Keyword arguments are used to map component attribute names to
        Components.

    Returns
    -------
    cls : Device
        Newly generated Device class
    '''
    if docstring is None:
        docstring = f'{name} Device'

    if not isinstance(base_class, tuple):
        base_class = (base_class, )

    if class_kwargs is None:
        class_kwargs = {}

    clsdict = {
        '__doc__': docstring,
        **components
    }

    return type(name, base_class, clsdict, **class_kwargs)


def create_plc_device_class():
    components = {}
    for dbfn in glob.glob("*.db"):
        db_cpts = components_from_db(dbfn)
        components.update(db_cpts)
        print(f'Found database file {dbfn}')
        print(f'    - creating {len(db_cpts)} components on PLCDevice')

    # TODO: use ophyd.create_device_from_components after upgrade
    return create_device_from_components(
        'PLCDevice', base_class=ophyd.Device, **components)

PLCDevice = create_plc_device_class()
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
