{% import "util.macro" as util %}

{{ util.section('Settings') }}

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

{{ util.section('Pragmas') }}

Total pragmas found: {{ plc.pragma_count }}
Total linter errors: {{ plc.pragma_errors }}

        {% for filename, items in plc.linter_results | groupby('filename') %}
            {{- util.subsection(filename) }}

            {% for item in items %}
#. Line {{ item.line_number }} ({{ item.exception.__class__.__name__ }})

::

    {{ item.exception | string | indent(4) }}

    Full pragma:

    {{ item.pragma if item.pragma else '' | indent(4) }}

            {% endfor %}{# for item in items #}
        {% endfor %}{# for ... in plc.linter_results #}


{{ util.section('Libraries') }}

.. csv-table::
    :header: Library, Vendor, Default, Version
    :align: center

    {% for item in get_simple_library_versions(plc.obj) | sort(attribute="name") %}
        {{ item.name }}, {{ item.vendor }}, {{ item.default }}, {{ item.version }}
    {% endfor %}{# for library... #}

{{ util.section("Symbols") }}

{% set symbols = get_symbols(plc.obj) %}

{% for group, symbols in symbols | groupby(attribute="top_level_group") %}

    {{- util.subsection(group) }}

{% if symbols|length > 10 %}
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

{% if symbols|length > 10 %}
.. raw:: html

   </details>
   <br />

{% endif %}

{% endfor %}{# for group... #}
