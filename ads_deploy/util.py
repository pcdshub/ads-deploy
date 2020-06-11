import distutils.version
import logging
import os
import pathlib

import pytmc

logger = logging.getLogger(__name__)

ADS_IOC_LOCATION = pathlib.Path(
    os.environ.get('ADS_IOC_LOCATION', '/reg/g/pcds/epics/ioc/common/ads-ioc')
)


def get_latest_ads_ioc():
    """
    Get the latest ADS IOC path based on environment settings.

    Returns
    -------
    pathlib.Path
    """
    if not ADS_IOC_LOCATION.exists():
        raise RuntimeError(
            f'ADS_IOC_LOCATION={ADS_IOC_LOCATION} does not exist.  Cannot '
            'automatically find latest version of ads-ioc.'
        )

    if (ADS_IOC_LOCATION / 'iocBoot' / 'templates').exists():
        return ADS_IOC_LOCATION

    def get_version(path):
        try:
            version = path.name.lstrip('Rv').replace('-', '.')
            return tuple(distutils.version.LooseVersion(version).version)
        except Exception:
            ...

    paths = {
        get_version(path): path for path in ADS_IOC_LOCATION.iterdir()
        if get_version(path) is not None
    }

    if not paths:
        raise RuntimeError(
            f'No versions in ADS_IOC_LOCATION={ADS_IOC_LOCATION} were found. '
            'Cannot automatically find latest version of ads-ioc.'
        )

    latest_version = paths[max(paths)]
    if (latest_version / 'iocBoot' / 'templates').exists():
        logger.info('Found latest ads-ioc: %s', latest_version)
        return latest_version

    raise RuntimeError(
        f'The latest version in ADS_IOC_LOCATION={ADS_IOC_LOCATION} was '
        f'determined to be {max(paths)} ({latest_version}), but there is no '
        'corresponding Makefile.  Cannot automatically find latest version of '
        'ads-ioc.'
    )


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
