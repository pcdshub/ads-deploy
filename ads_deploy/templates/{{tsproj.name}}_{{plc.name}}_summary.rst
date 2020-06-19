{% import "util.macro" as util %}

{% set section_name %}{{ plc.name }}{% endset %}
{{ util.section(section_name) }}

{{ util.subsection('Settings') }}

.. list-table::
    :header-rows: 1
    :align: center

    * - Setting
      - Value
      - Description
    * - AMS Net ID
      - {{ plc.obj.ams_id | default("UNSET") }}
      -
    * - Target IP address
      - {{ plc.obj.target_ip | default("UNSET") }}
      - Based on AMS Net ID by convention
    * - AMS Port
      - {{ plc.obj.port | default("UNSET") }}
      -

.. _{{ plc.name }}_pragmas:

{{ util.subsection('Pragmas') }}

Total pragmas found: {{ plc.pragma_count }}
Total linter errors: {{ plc.pragma_errors }}

        {% for filename, items in plc.linter_results | groupby('filename') %}
            {{- util.subsubsection(filename) }}

            {% for item in items %}
#. Line {{ item.line_number }} ({{ item.exception.__class__.__name__ }})

::

    {{ item.exception | string | indent(4) }}

    Full pragma:

    {{ item.pragma | indent(4) }}

            {% endfor %}{# for item in items #}
        {% endfor %}{# for ... in plc.linter_results #}

{{ util.subsection("Symbols") }}


{% for group, symbols in plc.symbols | groupby(attribute="top_level_group") %}

    {{- util.subsubsection(group) }}

{% if symbols|length > 2 %}
.. raw:: html

   <details>
       <summary>{{symbols|length}} Symbols</summary>

{% endif %}
.. csv-table::
    :header: Symbol, Type, Offset/Size
    :align: center

    {% for symbol in symbols | sort(attribute="name") %}
        {{ symbol.name }}, {{ symbol.summary_type_name }}, {{ symbol.BitOffs[0].text }} ({{ symbol.BitSize[0].text }})
    {% endfor %}{# for symbol... #}

{% if symbols|length > 2 %}
.. raw:: html

   </details>

{% endif %}
{% endfor %}{# for group... #}
