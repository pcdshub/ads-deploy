"""
`ads-deploy docs` is used to generate Sphinx-compatible markdown for TwinCAT
projects that contain pytmc pragmas.

This can also be used in conjunction with
[doctr](https://github.com/drdoctr/doctr) to generate documentation with
continuous integration.  LCLS maintains its own tools for that in
[pcds-ci-helpers](https://github.com/pcdshub/pcds-ci-helpers/).
"""

import argparse
import functools
import logging
import pathlib
import re
import sys
from typing import Callable, Dict, List, Optional, Union

import jinja2

import pytmc
import pytmc.bin.db
import pytmc.bin.pragmalint
import pytmc.bin.summary
from pytmc import parser as pytmc_parser
from pytmc.bin.template import get_boxes
from pytmc.bin.template import get_jinja_filters as get_pytmc_jinja_filters
from pytmc.bin.template import (get_linter_results, get_plc_records,
                                get_render_context, helpers)

from . import util

DESCRIPTION = __doc__
MODULE_PATH = pathlib.Path(__file__).parent
TEMPLATE_PATH = MODULE_PATH / "templates"
DEFAULT_TEMPLATES = list(TEMPLATE_PATH.glob("*.rst"))
logger = logging.getLogger(__name__)


def build_arg_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser()

    parser.description = DESCRIPTION
    parser.formatter_class = argparse.RawTextHelpFormatter

    parser.add_argument(
        "project",
        metavar="INPUT",
        type=str,
        help="Path to the solution (.sln) or project (.tsproj) file",
    )

    parser.add_argument(
        "--plcs",
        type=str,
        action="append",
        help="Specify one or more PLC names to generate specifically",
    )

    parser.add_argument(
        "--template",
        dest="templates",
        type=str,
        action="append",
        help="Specify the template (or templates) for documentation",
    )

    parser.add_argument(
        "--dbd",
        "-d",
        default=None,
        type=str,
        help="Specify an expanded .dbd file for validating record fields",
    )

    parser.add_argument(
        "--dry-run", action="store_true",
        help="Dry-run only - do not write files"
    )

    parser.add_argument(
        "--output",
        dest="output_path",
        default=".",
        type=str,
        help="Write documentation to this location",
    )

    return parser


def build_template_kwargs(
    solution_path: pathlib.Path,
    projects: List[pathlib.Path],
    *,
    plcs: Optional[List[str]] = None,
    dbd: Optional[str] = None
) -> dict:
    """
    Get the top-level template rendering context dictionary.

    Parameters
    ----------
    solution_path : pathlib.Path
        The path to the solution file.

    projects : list of pathlib.Path
        The projects from the solution.

    plcs : list of str, optional
        List of PLC names to limit to.

    dbd : str, optional
        The database definition path, if available.

    Returns
    -------
    dict
        The dictionary used to render all documentation templates.
    """
    solution_name = solution_path.stem if solution_path is not None else None
    render_args = {
        "solution": solution_path,
        "solution_name": solution_name,
        "tsprojects": [],
    }

    for tsproj_project in projects:
        parsed_tsproj = pytmc.parser.parse(tsproj_project)

        box_by_id = {
            int(box.attributes["Id"]): box
            for box in get_boxes(parsed_tsproj)
        }
        proj_info = dict(
            directory=tsproj_project.parent,
            name=tsproj_project.stem,
            filename=tsproj_project.name,
            plcs=[],  # Filled below
            obj=parsed_tsproj,
            nc=list(parsed_tsproj.find(pytmc_parser.NC)),
            box_by_id=box_by_id,
        )

        render_args["tsprojects"].append(proj_info)
        for plc_name, plc_project in parsed_tsproj.plcs_by_name.items():
            logger.debug("Project: %s PLC: %s", tsproj_project, plc_name)

            if plcs and plc_name not in plcs:
                logger.debug("Skipping; not in valid list: %s", plcs)
                continue

            records, record_exceptions = get_plc_records(plc_project, dbd)
            plc_info = dict(
                name=plc_name,
                obj=plc_project,
                tmc_path=plc_project.tmc_path,
                records=records,
                record_exceptions=record_exceptions,
            )

            logger.debug(
                "Records for %s: %d",
                plc_name,
                len(records) if records else 0
            )
            proj_info["plcs"].append(plc_info)

            plc_info.update(**get_linter_results(plc_project))

    return render_args


def get_jinja_environment(
    templates: List[pathlib.Path],
    trim_blocks: bool = True,
    lstrip_blocks: bool = True,
    **env_kwargs,
) -> jinja2.Environment:
    """Environment for expanding filename templates."""
    template_dirs = set(str(item.parent) for item in templates)
    loader = jinja2.ChoiceLoader(
        [jinja2.FileSystemLoader(str(path)) for path in template_dirs]
    )

    env = jinja2.Environment(
        loader=loader,
        trim_blocks=trim_blocks,
        lstrip_blocks=lstrip_blocks,
        **env_kwargs,
    )
    env.filters.update(get_jinja_filters())
    return env


def get_jinja_filename_environment(templates) -> jinja2.Environment:
    """Environment for expanding filename templates."""
    loader = jinja2.DictLoader(
        {template.name: template.name for template in templates}
    )
    return jinja2.Environment(
        loader=loader, trim_blocks=True, lstrip_blocks=True
    )


def get_jinja_filters() -> Dict[str, Callable]:
    """ads-deploy jinja filters, including those from ``pytmc template``."""
    saw_tsproj = set()
    name_cache = {}

    def related_source(
        text,
        source_name: str,
        tsproj: pytmc_parser.TcSmProject,
        plc: pytmc_parser.Plc,
    ):
        if tsproj not in saw_tsproj:
            saw_tsproj.add(tsproj)
            to_cache = [
                ("DUTs", plc.dut_by_name),
                ("GVLs", plc.gvl_by_name),
                ("POUs", plc.pou_by_name),
            ]
            for plc in tsproj.plcs:
                for _, source_dict in to_cache:
                    for source_name in source_dict:
                        regex = re.compile(rf"\b{source_name}\b")
                        name_cache[regex] = source_name
        related = set(
            name
            for regex, name in name_cache.items()
            if regex.search(text)
        )

        return [
            f"`{name}`_" for name in sorted(related)
            if name != source_name
        ]

    filters = get_pytmc_jinja_filters()
    filters.update(
        {
            key: value
            for key, value in locals().items()
            if not key.startswith("_") and callable(value)
        }
    )
    return filters


def render_template(
    env: jinja2.Environment,
    template: str,
    context: dict
) -> str:
    """
    Render a template given the jinja environment.
    """
    return env.from_string(template).render(context)


def get_simple_library_versions(plc: pytmc_parser.Plc) -> List[dict]:
    """Get library versions."""
    if 'DefaultResolution' not in pytmc_parser.TWINCAT_TYPES:
        return []

    def parse_library(text, version_key):
        library_name, version_and_vendor = text.split(', ')
        version, vendor = version_and_vendor.split('(')
        vendor = vendor.rstrip(')')
        version = version.strip()

        if version == '*':
            version = 'Unset'

        return (
            library_name,
            {'name': library_name,
             'vendor': vendor,
             version_key: version,
             },
        )

    libraries = dict(
        parse_library(lib.text, version_key='default')
        for lib in plc.find(pytmc_parser.TWINCAT_TYPES['DefaultResolution'])
    )
    resolved = dict(
        parse_library(lib.text, version_key='version')
        for lib in plc.find(pytmc_parser.TWINCAT_TYPES['Resolution'])
    )

    for name, info in resolved.items():
        if name not in libraries:
            libraries[name] = info
        else:
            libraries[name]['version'] = info['version']

    return list(libraries.values())


if get_simple_library_versions not in helpers:
    helpers.append(get_simple_library_versions)


def main(
    project: pathlib.Path,
    output_path: Union[str, pathlib.Path],
    *,
    plcs: Optional[List[str]] = None,
    templates: Optional[List[pathlib.Path]] = None,
    dbd: Optional[str] = None,
    dry_run: bool = False
) -> None:
    """
    ``ads-deploy docs`` entrypoint.
    """
    templates = [
        pathlib.Path(item) for item in (templates or DEFAULT_TEMPLATES)
    ]

    if not templates:
        raise ValueError("No templates provided.")

    jinja_env = get_jinja_environment(templates)
    jinja_filename_env = get_jinja_filename_environment(templates)

    output_path = pathlib.Path(output_path)

    if not output_path.is_dir():
        raise ValueError(f"Output path is not a directory: {output_path}")

    project = pathlib.Path(project).resolve()
    if not project.exists():
        logger.error("Project does not exist: %s", project)
        sys.exit(1)

    solution_path, projects = util.get_tsprojects_from_filename(project)

    full_render_args = build_template_kwargs(
        solution_path, projects, plcs=plcs, dbd=dbd
    )

    @functools.lru_cache(maxsize=None)
    def get_template_source(template_path: pathlib.Path) -> str:
        with open(template_path, "rt") as fp:
            return fp.read()

    def write_file(template_path, render_args, template_type=""):
        tpl = jinja_filename_env.get_template(template_path.name)
        target_filename = tpl.render(**render_args)

        logger.info(
            "Rendering %s template: %s -> %s",
            template_type,
            template_path.name,
            target_filename,
        )

        # template = jinja_env.get_template(template_path.name)
        template = get_template_source(template_path)
        # contents = template.render(**render_args)
        ctx = dict(get_render_context())
        ctx.update(render_args)
        contents = render_template(jinja_env, template, context=ctx)
        if dry_run:
            print("** dry run ** file:", target_filename)
            print(contents)
        else:
            with open(output_path / target_filename, "wt") as f:
                f.write(contents)

    logger.debug("All templates: %s", templates)
    for template_path in templates:
        if "{plc" in template_path.name.replace(" ", ""):
            # A bit of hacking: generate template per PLC
            for tsproj in full_render_args["tsprojects"]:
                for plc in tsproj["plcs"]:
                    render_args = dict(full_render_args)
                    render_args["tsproj"] = tsproj
                    render_args["plc"] = plc
                    write_file(template_path, render_args, "per-PLC")
        elif "{tsproj" in template_path.name.replace(" ", ""):
            # A bit of hacking: generate template per tsproj
            for tsproj in full_render_args["tsprojects"]:
                render_args = dict(full_render_args)
                render_args["tsproj"] = tsproj
                write_file(template_path, render_args, "per-tsproj")
        else:
            write_file(template_path, full_render_args, "general")

    logger.info("Done")
