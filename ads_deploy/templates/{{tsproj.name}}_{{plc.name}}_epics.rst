{% import "util.macro" as util %}

{% set section_name %}{{ plc.name }} EPICS{% endset %}
{{ util.section(section_name) }}

{{ util.subsection('Database') }}

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
    {% set package = record._ads_deploy_record_package_ %}
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
