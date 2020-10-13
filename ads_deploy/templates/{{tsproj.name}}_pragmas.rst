{% import "util.macro" as util %}

{{ util.section("Pragmas") }}

.. csv-table::
    :header: PLC Name, Total Pragmas, Errors
    :align: center

    {% for plc in tsproj.plcs %}
    :ref:`{{ plc.name }} <{{ plc.name }}_overview_pragmas>`, {{ plc.pragma_count }}, {{ plc.pragma_errors }}
    {% endfor %}

{% for plc in tsproj.plcs %}

.. _{{ plc.name }}_overview_pragmas:

{% set subsection_name -%}
{{ plc.name }}
{%- endset %}

{{ util.subsection(plc.name) }}

Total pragmas found: {{ plc.pragma_count }}
Total linter errors: {{ plc.pragma_errors }}

        {% for filename, items in plc.linter_results | groupby('filename') %}
            {{- util.subsection(filename) }}

            {% for item in items %}
#. Line {{ item.line_number }} ({{ item.exception.__class__.__name__ }})

::

    {{ item.exception | string | indent(4) }}

    Full pragma:

    {{ item.pragma if item.pragma else ''| indent(4) }}

            {% endfor %}{# for item in items #}
        {% endfor %}{# for ... in plc.linter_results #}

{% endfor %}
