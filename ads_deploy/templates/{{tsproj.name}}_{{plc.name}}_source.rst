{% import "util.macro" as util %}

{% for section, source_dict in [('DUTs', plc.obj.dut_by_name), ('GVLs', plc.obj.gvl_by_name), ('POUs', plc.obj.pou_by_name)] %}

{{ util.section(section) }}

{% for source_name, source in source_dict | dictsort %}

{{ util.subsection(source_name) }}

::

    {{ source.get_source_code() | indent(4) }}


{% set related = source.get_source_code() | related_source(source_name, tsproj.obj, plc.obj) %}
{% if related %}
Related:
{% for item in related %}
    * {{ item }}
{% endfor %}
{% endif %}

{% endfor %}{# for dut_name, ... #}
{% endfor %}{# for source_dict ... #}
