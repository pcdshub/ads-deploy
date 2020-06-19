{% import "util.macro" as util %}

{% set sectionname %}{{tsproj.filename}} Summary{% endset %}
{{ util.section(sectionname) }}

{{ util.subsection("Pragma Summary") }}

.. csv-table::
    :header: PLC Name, Total Pragmas, Errors
    :align: center

    {% for plc in tsproj.plcs %}
    :ref:`{{ plc.name }} <{{ plc.name }}_pragmas>`, {{ plc.pragma_count }}, {{ plc.pragma_errors }}
    {% endfor %}

{{ util.subsection("NC Settings") }}

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

{{ util.subsubsection(header) }}

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

{{ util.subsection("Boxes") }}

{% for box_id, box in tsproj.box_by_id | dictsort %}

{{ util.subsubsection(box.name | trim("=+-")) }}

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

{{ util.subsection("Links") }}

.. raw:: html

   <details>
        <summary>{{ tsproj.links|length}} Links</summary>
.. csv-table::
    :header: Owner A, Item A, Owner B, Item B
    :align: center

    {% for link in tsproj.links | sort(attribute="a") %}
        {{ link.a[0] }}, {{ link.a[1] }}, {{ link.b[0] }}, {{ link.b[1] }}
    {% endfor %}{# for link... #}

.. raw:: html

   </details>
