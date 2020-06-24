{% import "util.macro" as util %}

{{ util.section("Boxes") }}

{% for box_id, box in tsproj.box_by_id | dictsort %}

{{ util.subsection(box.name | trim("=+-")) }}

{% if box.EtherCAT %}
{% set ethercat = box.EtherCAT[0] %}

.. raw:: html

   <details>
        <summary>EtherCAT{% if ethercat.Pdo %} ({{ethercat.Pdo|length}} PDOs){% endif %}</summary>

.. csv-table:: Basic Settings
    :header: Name, Data
    :align: center

    Name, {{ box.name }}
    ID, {{ box_id }}
    {% for item in ethercat.BootStrapData %}
        BootStrapData, {{ item.text }}
    {% endfor %}
    {% for item in ethercat.SyncMan %}
        SyncMan, {{ item.text }}
    {% endfor %}
    {% for item in ethercat.Fmmu %}
        Fmmu, {{ item.text }}
    {% endfor %}
    {% for item in ethercat.CoeProfile %}
        CoeProfile, {{ item.attributes.get('ProfileNo') }}
    {% endfor %}

{% for pdo in ethercat.Pdo %}

    {% set pdotitle -%}
    PDO {{ pdo.name}} (Index {{pdo.attributes.Index}}, Flags {{pdo.attributes.Flags}}, SyncMan {{pdo.attributes.SyncMan}})
    {%- endset %}

{{ pdotitle }}

{% if pdo.Entry %}
.. csv-table::
    :header: Name, Comment, BitLen, Index, Type
    :align: center

        {% for entry in pdo.Entry %}
        "{{ entry.name }}", "{{ entry.comment | replace("\n", " ")}}", {{entry.attributes.BitLen}}, "{{entry.attributes.Index}}", "{{entry.entry_type.qualified_type}}"
        {% endfor %}

{% endif %}{# if pdo.Entry #}
{% endfor %}{# for pdo in ... #}

.. raw:: html

   </details>

{% endif %}{# if ethercat #}
{% endfor %}{# for box_id... #}
