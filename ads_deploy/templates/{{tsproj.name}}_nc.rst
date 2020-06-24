{% import "util.macro" as util %}

{{ util.section("NC Settings") }}

{% for nc in tsproj.nc %}
.. csv-table::
    :header: Axis ID, Name
    :align: center

    {% for axis_id, axis in nc.axis_by_id | dictsort %}
        {{ axis_id }}, {{ axis.name }}
    {% endfor %}{# for axis... #}

{% for axis_id, axis in nc.axis_by_id | dictsort %}

{% set header -%}
Axis {{ axis_id }}: {{ axis.name }}
{%- endset %}

{{ util.subsection(header) }}

.. csv-table::
    :header: Setting, Value
    :align: center

    Axis ID, {{ axis_id }}
    Name, {{ axis.name }}
    {% for setting, value in axis.summarize() | sort %}
    {{ setting }}, {{ value }}
    {% endfor %}{# for setting... #}

{% endfor %}{# for axis... #}

{% endfor %}{# for nc... #}
