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
import pytmc.bin.db
import pytmc.bin.pragmalint
from pytmc import parser as pytmc_parser

from . import util

# from . import templates as templates_module

DESCRIPTION = __doc__
MODULE_PATH = pathlib.Path(__file__).parent
TEMPLATE_PATH = MODULE_PATH / 'templates'
DEFAULT_TEMPLATES = list(TEMPLATE_PATH.glob('*.rst'))
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
        '--dbd',
        '-d',
        default=None,
        type=str,
        help='Specify an expanded .dbd file for validating record fields'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry-run only - do not write files'
    )

    parser.add_argument(
        '--output',
        dest='output_path',
        default='.',
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

    loader = jinja2.ChoiceLoader([jinja2.FileSystemLoader(str(path))
                                  for path in template_dirs])

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


def get_jinja_filename_environment(templates):
    loader = jinja2.DictLoader({template.name: template.name
                                for template in templates})

    return jinja2.Environment(
        loader=loader,
        trim_blocks=True,
        lstrip_blocks=True,
    )


if 'Entry' not in pytmc_parser.TWINCAT_TYPES:
    class Entry(pytmc_parser.TwincatItem):
        @property
        def entry_type(self):
            return getattr(self, 'Type', [None])[0]

        @property
        def comment(self):
            return self.Comment[0].text if hasattr(self, 'Comment') else ''

    class EtherCAT(pytmc_parser.TwincatItem):
        ...

    class Pdo(pytmc_parser.TwincatItem):
        ...

    pytmc_parser.Entry = Entry
    pytmc_parser.Pdo = Pdo
    pytmc_parser.EtherCAT = EtherCAT


def get_boxes(tsproj):
    return {
        int(box.attributes['Id']): box
        for box in tsproj.find(pytmc_parser.Box)
    }


def get_symbols(plc_project):
    symbols = set(plc_project.find(pytmc_parser.Symbol))

    for symbol in symbols:
        symbol.top_level_group = (
            symbol.name.split('.')[0] if symbol.name else 'Unknown')
    return symbols


def get_plc_records(plc_project, dbd):
    if plc_project.tmc is None:
        return None, None

    try:
        return pytmc.bin.db.process(
            plc_project.tmc, dbd_file=dbd, allow_errors=True,
            show_error_context=True,
        )
    except Exception:
        logger.exception(
            'Failed to create EPICS records'
        )
        return None, None


def build_template_kwargs(solution_path, projects, *, plcs=None, dbd=None):
    render_args = {
        'solution': solution_path,
        'solution_name': solution_path.name if solution_path else None,
        'tsprojects': [],
    }

    for tsproj_project in projects:
        parsed_tsproj = pytmc.parser.parse(tsproj_project)

        proj_info = dict(
            directory=tsproj_project.parent,
            name=tsproj_project.stem,
            filename=tsproj_project.name,
            plcs=[],
            obj=parsed_tsproj,
            nc=list(parsed_tsproj.find(pytmc_parser.NC)),
            box_by_id=get_boxes(parsed_tsproj),
            links=list(parsed_tsproj.find(pytmc_parser.Link)),
        )

        render_args['tsprojects'].append(proj_info)
        for plc_name, plc_project in parsed_tsproj.plcs_by_name.items():
            logger.debug('Project: %s PLC: %s', tsproj_project, plc_name)

            if plcs and plc_name not in plcs:
                logger.debug('Skipping; not in valid list: %s', plcs)
                continue

            records, record_exceptions = get_plc_records(plc_project, dbd)
            plc_info = dict(
                name=plc_name,
                obj=plc_project,
                tmc_path=plc_project.tmc_path,
                symbols=get_symbols(plc_project),
                records=records,
                record_exceptions=record_exceptions,
            )

            proj_info['plcs'].append(plc_info)

            plc_info.update(**lint_plc(plc_project))

    return render_args


def main(project, output_path, *, plcs=None, templates=None, dbd=None,
         dry_run=False):
    templates = [
        pathlib.Path(item)
        for item in (templates or DEFAULT_TEMPLATES)
    ]

    if not templates:
        raise ValueError('No templates provided.')

    jinja_env = get_jinja_environment(templates)
    jinja_filename_env = get_jinja_filename_environment(templates)

    output_path = pathlib.Path(output_path)

    if not output_path.is_dir():
        raise ValueError(f'Output path is not a directory: {output_path}')

    solution_path, projects = util.get_tsprojects_from_filename(project.name)

    full_render_args = build_template_kwargs(
        solution_path, projects, plcs=plcs, dbd=dbd)

    def write_file(template_path, render_args, template_type=''):
        target_filename = jinja_filename_env.get_template(
            template_path.name).render(**render_args)

        logger.info('Rendering %s template: %s -> %s',
                    template_type,
                    template_path.name,
                    target_filename)

        template = jinja_env.get_template(template_path.name)
        contents = template.render(**render_args)
        if dry_run:
            print('** dry run ** file:', target_filename)
            print(contents)
        else:
            with open(output_path / target_filename, 'wt') as f:
                f.write(contents)

    logger.debug('All templates: %s', templates)
    for template_path in templates:
        if '{plc' in template_path.name.replace(' ', ''):
            # A bit of hacking: generate template per PLC
            for tsproj in full_render_args['tsprojects']:
                for plc in tsproj['plcs']:
                    render_args = dict(full_render_args)
                    render_args['tsproj'] = tsproj
                    render_args['plc'] = plc
                    write_file(template_path, render_args, 'per-PLC')
        elif '{tsproj' in template_path.name.replace(' ', ''):
            # A bit of hacking: generate template per tsproj
            for tsproj in full_render_args['tsprojects']:
                render_args = dict(full_render_args)
                render_args['tsproj'] = tsproj
                write_file(template_path, render_args, 'per-tsproj')
        else:
            write_file(template_path, full_render_args, 'general')

    logger.info('Done')
