import distutils.version
import os
import pathlib

import pytmc

ADS_IOC_LOCATION = pathlib.Path(os.environ.get('ADS_IOC_LOCATION',
                                '/reg/g/pcds/epics/ioc/common/ads-ioc'))


def get_latest_ads_ioc():
    if not ADS_IOC_LOCATION.exists():
        raise RuntimeError(
            f'ADS_IOC_LOCATION={ADS_IOC_LOCATION} does not exist.  Cannot '
            'automatically find latest version of ads-ioc.'
        )

    if (ADS_IOC_LOCATION / 'iocBoot' / 'templates').exists():
        return ADS_IOC_LOCATION

    def get_version(path):
        try:
            return distutils.version.LooseVersion(path)
        except Exception:
            ...

    paths = {
        get_version(path): path for path in ADS_IOC_LOCATION.iterdir()
        if get_version(path) is not None
    }

    if not paths:
        raise RuntimeError(
            f'ADS_IOC_LOCATION={ADS_IOC_LOCATION} does not exist.  Cannot '
            'automatically find latest version of ads-ioc.'
        )

    latest_version = max(paths)
    return paths[latest_version]


def get_tsprojects_from_filename(filename):
    """
    From a TwinCAT solution (.sln) or .tsproj, return all tsproj projects.

    Returns
    -------
    root : pathlib.Path
        Project root directory (where the solution or provided tsproj is
        located).

    projects : list
        List of tsproj projects.
    """
    filename = pathlib.Path(filename)
    if filename.suffix == '.tsproj':
        return filename.parent, [filename]
    if filename.suffix == '.sln':
        return filename.parent, pytmc.parser.projects_from_solution(filename)

    raise RuntimeError(f'Expected a .tsproj/.sln file; got {filename.suffix}')
