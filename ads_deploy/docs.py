"""
`ads-deploy docs` is used to generate Sphinx-compatible markdown for TwinCAT
projects that contain pytmc pragmas.

This can also be used in conjunction with
[doctr](https://github.com/drdoctr/doctr) to generate documentation with
continuous integration.  LCLS maintains its own tools for that in
[pcds-ci-helpers](https://github.com/pcdshub/pcds-ci-helpers/).
"""

# TODO: Thought for the future: this could be integrated into pytmc as part of
# the `pytmc stcmd` refactor into `pytmc template`, with the additional render
# context arguments provided here.

import argparse
import logging
import pathlib

import jinja2
import pytmc
import pytmc.bin.pragmalint
from pytmc import parser as pytmc_parser

from . import util

DESCRIPTION = __doc__
MODULE_PATH = pathlib.Path(__file__).parent
DEFAULT_TEMPLATES = [MODULE_PATH / 'docs_template.jinja2']
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
        '--plcs',
        type=str,
        action='append',
        help='Specify one or more PLC names to generate specifically'
    )

    parser.add_argument(
        '--template',
        dest='templates',
        type=str,
        action='append',
        help='Specify the template (or templates) for documentation'
    )

    parser.add_argument(
        '--output',
        dest='output_path',
        type=str,
        help='Write documentation to this location'
    )

    return parser


def lint_plc(plc_project):
    pragma_count = 0
    linter_errors = 0
    results = []

    for fn, source in plc_project.source.items():
        for info in pytmc.bin.pragmalint.lint_source(fn, source):
            pragma_count += 1
            if info.exception is not None:
                linter_errors += 1
                results.append(info)

    return {'pragma_count': pragma_count,
            'pragma_errors': linter_errors,
            'linter_results': results}


def get_jinja_environment(templates):
    template_dirs = set(str(item.parent) for item in templates)

    loader = jinja2.ChoiceLoader(
        [jinja2.FileSystemLoader(str(path)) for path in template_dirs]
    )

    jinja_env = jinja2.Environment(
        loader=loader,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    @jinja2.evalcontextfilter
    def title_fill(eval_ctx, text, fill_char):
        return fill_char * len(text)

    jinja_env.filters['title_fill'] = title_fill
    return jinja_env


def build_template_kwargs(solution_path, projects, plcs=None):
    render_args = {
        'solution': solution_path,
        'solution_name': solution_path.name if solution_path else None,
        'tsprojects': [],
    }

    for tsproj_project in projects:
        parsed_tsproj = pytmc.parser.parse(tsproj_project)

        proj_info = dict(
            directory=tsproj_project.parent,
            filename=tsproj_project.name,
            plcs=[],
            obj=parsed_tsproj,
            nc=list(parsed_tsproj.find(pytmc_parser.NC)),
            box_by_id={
                int(box.attributes['Id']): box
                for box in parsed_tsproj.find(pytmc_parser.Box)
            },
            links=list(parsed_tsproj.find(pytmc_parser.Link)),
        )

        render_args['tsprojects'].append(proj_info)
        for plc_name, plc_project in parsed_tsproj.plcs_by_name.items():
            logger.debug('Project: %s PLC: %s', tsproj_project, plc_name)

            if plcs and plc_name not in plcs:
                logger.debug('Skipping; not in valid list: %s', plcs)
                continue

            symbols = set(plc_project.find(pytmc_parser.Symbol))

            for symbol in symbols:
                symbol.top_level_group = (
                    symbol.name.split('.')[0] if symbol.name else 'Unknown')

            plc_info = dict(
                name=plc_name,
                obj=plc_project,
                tmc_path=plc_project.tmc_path,
                symbols=symbols,
            )

            proj_info['plcs'].append(plc_info)

            plc_info.update(**lint_plc(plc_project))

    return render_args


def main(project, plcs=None, templates=None, output_path=None):
    if templates is not None:
        templates = [pathlib.Path(item) for item in templates]
    else:
        templates = DEFAULT_TEMPLATES

    jinja_env = get_jinja_environment(templates)

    solution_path, projects = util.get_tsprojects_from_filename(project.name)

    render_args = build_template_kwargs(solution_path, projects, plcs=plcs)

    for template_path in templates:
        template = jinja_env.get_template(template_path.name)
        print(template.render(**render_args))
