{% import "util.macro" as util %}

{% set section_name %}{{plc.name}} Source Code{% endset %}
{{ util.section(section_name) }}

{% for source_dict in [plc.obj.dut_by_name, plc.obj.gvl_by_name, plc.obj.pou_by_name] %}

{% for source_name, source in source_dict | dictsort %}

{% set header = source.tag + ': ' + source_name %}
{{ util.subsection(header) }}

::

    {{ source.get_source_code() | indent(4) }}

{% endfor %}{# for dut_name, ... #}
{% endfor %}{# for source_dict ... #}
