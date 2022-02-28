{% import "util.macro" as util %}

{{ util.section('Data Types') }}

{% set plc_data_types = get_data_types(plc.obj) %}
{% set tmc_data_types = enumerate_types(plc.obj.tmc) | list %}
{% set data_types = plc_data_types + tmc_data_types %}

{% for data_type in data_types | sort(attribute="qualified_type_name") %}
{% if data_type.records %}

{% set subsection_name %}{{ data_type.qualified_type_name }}{% endset %}
{{ util.subsection(subsection_name) }}

.. list-table::
    :header-rows: 1
    :align: center

    * - Record
      - Type
      - Description
      - Pragma
    {% for record in data_type.records | sort(attribute="pvname") %}
    {% set package = record.package %}
    {% set extended_description %}
{{ record.long_description | default(record.fields.DESC) }}{% if package.linked_to_pv %}; Linked to PV: {{package.linked_to_pv}}{% endif %}
    {% endset %}
    {% set pragma %}
        {% for key, value in config_to_pragma(package.config) | sort %}
| {{ key }}: {{ value }}
        {% endfor %}
    {% endset %}
    * - {{ record.pvname }}
      - {{ record.record_type }}
      - {{ extended_description }}
      - {{ pragma | indent(8) }}

    {% endfor %}{# for record... #}
{% endif %} {# if data_type.records #}
{% endfor %}{# for data_type... #}

{{ util.section('Database Records') }}

{% set records = plc.records %}
{% if records %}
.. list-table::
    :header-rows: 1
    :align: center

    * - Record
      - Type
      - Description
      - Pragma
    {% for record in records | sort(attribute="pvname") %}
    {% set package = record.package %}
    {% set extended_description %}
{{ record.long_description | default(record.fields.DESC) }}{% if package.linked_to_pv %}; Linked to PV: {{package.linked_to_pv}}{% endif %}
    {% endset %}
    {% set pragma %}
        {% for key, value in config_to_pragma(package.config) | sort %}
| {{ key }}: {{ value }}
        {% endfor %}
    {% endset %}
    * - {{ record.pvname }}
      - {{ record.record_type }}
      - {{ extended_description }}
      - {{ pragma | indent(8) }}

    {% endfor %}{# for record... #}

{% else %}
No records defined.
{% endif %}
